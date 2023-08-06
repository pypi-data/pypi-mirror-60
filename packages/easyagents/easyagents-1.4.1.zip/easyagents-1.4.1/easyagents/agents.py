"""This module contains the public api of the EasyAgents reinforcement learning library.

    It consist mainly of the class hierarchy of the available agents (algorithms), registrations and
    the management of the available backends. In their implementation the agents forward their calls
    to the chosen backend.
"""

from abc import ABC
from collections import namedtuple
import json
import os
import statistics
from typing import Dict, List, Optional, Tuple, Type, Union

from easyagents import core
from easyagents.backends import core as bcore
from easyagents.callbacks import plot
import easyagents.backends.default
import easyagents.backends.tfagents
import tensorflow as tf

# import easyagents.backends.tforce

_backends: [bcore.BackendAgentFactory] = []

"""The seed used for all agents and gym environments. If None no seed is set (default)."""
seed: Optional[int] = None


def load(directory: str,
         callbacks: Union[List[core.AgentCallback], core.AgentCallback, None] = None):
    """Loads an agent from directory.

    After a successful load play() may be called directly.
    The agent, model, backend, seed and play policy are restored according to the previously saved agent.

    Args:
        directory: the directory containing the previously saved policy.
        callbacks: list of callbacks called during save (eg log.Agent)

    Result:
        a new instance of EasyAgents
    """
    assert directory
    agent_json_path = os.path.join(directory, EasyAgent._KEY_EASYAGENT_FILENAME)
    policy_directory = os.path.join(directory, EasyAgent._KEY_POLICY_DIRECTORY)
    assert os.path.isdir(directory), f'directory "{directory}" not found.'
    assert os.path.isfile(agent_json_path), 'file "{agent_json_path}" not found.'
    assert os.path.isdir(policy_directory), f'directory "{policy_directory}" not found.'
    with open(agent_json_path) as jsonfile:
        agent_dict = json.load(jsonfile)
    result = EasyAgent._from_dict(agent_dict)
    callbacks = result._to_callback_list(callbacks=callbacks)
    result._backend_agent.load(directory=policy_directory, callbacks=callbacks)
    return result


def register_backend(backend: bcore.BackendAgentFactory):
    """registers a backend as a factory for agent implementations.

    If another backend with the same name is already registered, the old backend is replaced by backend.
    """
    assert backend
    old_backends = [b for b in _backends if b.backend_name == backend.backend_name]
    for old_backend in old_backends:
        _backends.remove(old_backend)
    _backends.append(backend)


def activate_tensorforce():
    """registers the tensorforce backend.

    Due to an incompatibility between tensorforce and tf-agents, both libraries may not run
    in the same python instance. Thus - for the time being - once this method is called,
    the tfagents backend may not be used anymore.
    """
    import easyagents.backends.tforce

    global _backends

    assert  easyagents.backends.core._tf_eager_execution_active is None or \
            easyagents.backends.core._tf_eager_execution_active == False, \
            "tensorforce can not be activated, since tensorflow eager execution mode was already actived."

    _backends = []
    register_backend(easyagents.backends.default.DefaultAgentFactory(register_tensorforce=True))
    register_backend(easyagents.backends.tforce.TensorforceAgentFactory())

def _activate_tfagents():
    """registers the tfagents backend.

    Due to an incompatibility between tensorforce and tf-agents, both libraries may not run
    in the same python instance.
    """
    global _backends

    assert  easyagents.backends.core._tf_eager_execution_active is None or \
            easyagents.backends.core._tf_eager_execution_active == True, \
            "tfagents can not be activated, since tensorflow eager execution mode was already disabled."
    _backends = []
    register_backend(easyagents.backends.default.DefaultAgentFactory(register_tensorforce=False))
    register_backend(easyagents.backends.tfagents.TfAgentAgentFactory())


_activate_tfagents()


class EasyAgent(ABC):
    """Abstract base class for all easy reinforcment learning agents.

    Besides forwarding train and play it implements persistence."""

    _KEY_BACKEND = 'backend'
    _KEY_EASYAGENT_CLASS = 'easyagent_class'
    _KEY_EASYAGENT_FILENAME = 'easyagent.json'
    _KEY_MODEL_CONFIG = 'model_config'
    _KEY_POLICY_DIRECTORY = 'policy'
    _KEY_VERSION = 'version'

    def __init__(self,
                 gym_env_name: str,
                 fc_layers: Union[Tuple[int, ...], int, None] = None,
                 backend: str = None):
        """
            Args:
                gym_env_name: name of an OpenAI gym environment to be used for training and evaluation
                fc_layers: defines the neural network to be used, a sequence of fully connected
                    layers of the given size. Eg (75,40) yields a neural network consisting
                    out of 2 hidden layers, the first one containing 75 and the second layer
                    containing 40 neurons.
                backend=the backend to be used (eg 'tfagents'), if None a default implementation is used.
                    call get_backends() to get a list of the available backends.
        """
        model_config = core.ModelConfig(gym_env_name=gym_env_name, fc_layers=fc_layers, seed=seed)
        self._initialize(model_config=model_config, backend_name=backend)
        return

    def _initialize(self, model_config: core.ModelConfig, backend_name: str = None):
        if backend_name is None:
            backend_name = easyagents.backends.default.DefaultAgentFactory.backend_name
        backend: bcore.BackendAgentFactory = _get_backend(backend_name)

        assert model_config is not None, "model_config not set."
        assert backend, f'Backend "{backend_name}" not found. The registered backends are {get_backends()}.'

        self._model_config: core.ModelConfig = model_config
        backend_agent = backend.create_agent(easyagent_type=type(self), model_config=model_config)
        assert backend_agent, f'Backend "{backend_name}" does not implement "{type(self).__name__}". ' + \
                              f'Choose one of the following backend {get_backends(type(self))}.'
        self._backend_agent: Optional[bcore._BackendAgent] = backend_agent
        self._backend_name: str = backend_name
        self._backend_agent._agent_context._agent_saver = self.save
        return

    def _add_plot_callbacks(self, callbacks: List[core.AgentCallback],
                            default_plots: Optional[bool],
                            default_plot_callbacks: List[plot._PlotCallback]
                            ) -> List[core.AgentCallback]:
        """Adds the default callbacks and sorts all callbacks in the order
            _PreProcessCallbacks, AgentCallbacks, _PostProcessCallbacks.

        Args:
            callbacks: existing callbacks to prepare
            default_plots: if set or if None and callbacks does not contain plots then the default plots are added
            default_plot_callbacks: plot callbacks to add.
        """
        pre_process: List[core.AgentCallback] = [plot._PreProcess()]
        agent: List[core.AgentCallback] = []
        post_process: List[core.AgentCallback] = [plot._PostProcess()]

        if default_plots is None:
            default_plots = True
            for c in callbacks:
                default_plots = default_plots and (not isinstance(c, plot._PlotCallback))
        if default_plots:
            agent = default_plot_callbacks

        for c in callbacks:
            if isinstance(c, core._PreProcessCallback):
                pre_process.append(c)
            else:
                if isinstance(c, core._PostProcessCallback):
                    post_process.append(c)
                else:
                    agent.append(c)
        result: List[core.AgentCallback] = pre_process + agent + post_process
        return result

    @staticmethod
    def _from_dict(param_dict: Dict[str, object]):
        """recreates a new agent instance according to the definition previously created by _to_dict.

        Returns:
            new agent instance (excluding any trained policy), the agent type is preserved.
        """
        assert param_dict
        mc: core.ModelConfig = core.ModelConfig._from_dict(param_dict[EasyAgent._KEY_MODEL_CONFIG])
        agent_class = globals()[param_dict[EasyAgent._KEY_EASYAGENT_CLASS]]
        backend: str = param_dict[EasyAgent._KEY_BACKEND]
        result = agent_class(gym_env_name=mc.original_env_name, backend=backend)
        result._initialize(model_config=mc, backend_name=backend)
        return result

    def _to_callback_list(self, callbacks: Union[Optional[core.AgentCallback], List[core.AgentCallback]]) -> List[
        core.AgentCallback]:
        """maps callbacks to an admissible callback list.

        if callbacks is None an empty list is returned.
        if callbacks is an AgentCallback a list containing only this callback is returned
        otherwise callbacks is returned
        """
        result: List[core.AgentCallback] = []
        if not callbacks is None:
            if isinstance(callbacks, core.AgentCallback):
                result = [callbacks]
            else:
                assert isinstance(callbacks, list), "callback not an AgentCallback or a list thereof."
                result = callbacks
        return result

    def _to_dict(self) -> Dict[str, object]:
        """saves the agent definition to a dict.

            Returns:
                dict containing all parameters to recreate the agent (excluding a trained policy)
        """
        result: Dict[str, object] = dict()
        result[EasyAgent._KEY_VERSION] = easyagents.__version__
        result[EasyAgent._KEY_EASYAGENT_CLASS] = self.__class__.__name__
        result[EasyAgent._KEY_BACKEND] = self._backend_name
        result[EasyAgent._KEY_MODEL_CONFIG] = self._model_config._to_dict()
        result[EasyAgent._KEY_POLICY_DIRECTORY] = 'policy'
        return result

    def evaluate(self,
                 num_episodes: int = 50,
                 max_steps_per_episode: int = 50):
        """Plays num_episodes with the current policy and computes metrics on rewards.

        Args:
            num_episodes: number of episodes to play
            max_steps_per_episode: max steps per episode

        Returns:
            extensible score metrics
        """
        play_context = core.PlayContext()
        play_context.max_steps_per_episode = max_steps_per_episode
        play_context.num_episodes = num_episodes
        self.play(play_context=play_context, default_plots=False)
        Metrics = namedtuple('Metrics', 'steps rewards')

        Rewards = namedtuple('Rewards', 'mean std min max all')
        all_rewards = list(play_context.sum_of_rewards.values())
        mean_reward, std_reward, min_reward, max_reward = statistics.mean(all_rewards), statistics.stdev(
            all_rewards), min(all_rewards), max(all_rewards)
        rewards = Rewards(mean=mean_reward, std=std_reward, min=min_reward, max=max_reward, all=all_rewards)

        Steps = namedtuple('Steps', 'mean std min max all')
        all_num_steps = []
        for i in play_context.rewards.keys():
            all_num_steps.append(len(play_context.rewards[i]))

        mean_steps, std_steps, min_steps, max_steps = statistics.mean(all_num_steps), statistics.stdev(
            all_num_steps), min(all_num_steps), max(all_num_steps)
        steps = Steps(mean=mean_steps, std=std_steps, min=min_steps, max=max_steps, all=all_num_steps)

        metrics = Metrics(rewards=rewards, steps=steps)
        return metrics

    def play(self,
             callbacks: Union[List[core.AgentCallback], core.AgentCallback, None] = None,
             num_episodes: int = 1,
             max_steps_per_episode: int = 1000,
             play_context: core.PlayContext = None,
             default_plots: bool = None):
        """Plays num_episodes with the current policy.

        Args:
            callbacks: list of callbacks called during each episode play
            num_episodes: number of episodes to play
            max_steps_per_episode: max steps per episode
            play_context: play configuration to be used. If set override all other play context arguments
            default_plots: if set addes a set of default callbacks (plot.State, plot.Rewards, ...)

        Returns:
            play_context containg the actions taken and the rewards received during training
        """
        assert self._backend_agent._agent_context._is_policy_trained, "No trained policy available. Call train() first."
        if play_context is None:
            play_context = core.PlayContext()
            play_context.max_steps_per_episode = max_steps_per_episode
            play_context.num_episodes = num_episodes
        callbacks = self._to_callback_list(callbacks=callbacks)
        callbacks = self._add_plot_callbacks(callbacks, default_plots, [plot.Steps(), plot.Rewards()])
        self._backend_agent.play(play_context=play_context, callbacks=callbacks)
        return play_context

    def save(self, directory: Optional[str] = None,
             callbacks: Union[List[core.AgentCallback], core.AgentCallback, None] = None) -> str:
        """Saves the currently trained actor policy in directory.

        If save is called before a trained policy is created, eg by calling train, an exception is raised.

        Args:
             directory: the directory to save the policy weights to.
                if the directory does not exist yet, a new directory is created. if None the policy is saved
                in a temp directory.
             callbacks: list of callbacks called during save (eg log.Agent)

        Returns:
            the absolute path to the directory containing the saved policy.
        """
        if directory is None:
            directory = bcore._get_temp_path()
        assert directory
        assert self._backend_agent._agent_context._is_policy_trained, "No trained policy available. Call train() first."

        directory = bcore._mkdir(directory)
        agent_json_path = os.path.join(directory, EasyAgent._KEY_EASYAGENT_FILENAME)
        with open(agent_json_path, 'w') as jsonfile:
            agent_dict = self._to_dict()
            json.dump(agent_dict, jsonfile, sort_keys=True, indent=2)
        callbacks = self._to_callback_list(callbacks=callbacks)
        policy_directory = os.path.join(directory, EasyAgent._KEY_POLICY_DIRECTORY)
        policy_directory = bcore._mkdir(policy_directory)
        self._backend_agent.save(directory=policy_directory, callbacks=callbacks)
        return directory

    def train(self, train_context: core.TrainContext,
              callbacks: Union[List[core.AgentCallback], core.AgentCallback, None],
              default_plots: Optional[bool]):
        """Trains a new model using the gym environment passed during instantiation.

        Args:
            callbacks: list of callbacks called during the training and evaluation
            train_context: training configuration to be used (num_iterations,num_episodes_per_iteration,...)
            default_plots: if set adds a set of default callbacks (plot.State, plot.Rewards, plot.Loss,...).
                if None default callbacks are only added if the callbacks list is empty
        """
        assert train_context, "train_context not set."
        callbacks = self._to_callback_list(callbacks=callbacks)
        callbacks = self._add_plot_callbacks(callbacks, default_plots, [plot.Loss(), plot.Steps(), plot.Rewards()])
        self._backend_agent.train(train_context=train_context, callbacks=callbacks)


def get_backends(agent: Optional[Type[EasyAgent]] = None):
    """returns a list of all registered backends containing an implementation for the EasyAgent type agent.

    Args:
        agent: type deriving from EasyAgent for which the backend identifiers are returned.

    Returns:
        a list of admissible values for the 'backend' argument of EazyAgents constructors or a list of all
        available backends if agent is None.
    """
    result = [b.backend_name for b in _backends]
    if agent:
        result = [b.backend_name for b in _backends if agent in b.get_algorithms()]
    return result


def _get_backend(backend_name: str):
    """Yields the backend with the given name.

    Returns:
        the backend instance or None if no backend is found."""
    assert backend_name
    backends = [b for b in _backends if b.backend_name == backend_name]
    assert len(backends) <= 1, f'no backend found with name "{backend_name}". Available backends = {get_backends()}'
    result = None
    if backends:
        result = backends[0]
    return result


class CemAgent(EasyAgent):
    """creates a new agent based on the cross-entropy-method algorithm.

       From https://learning.mpi-sws.org/mlss2016/slides/2016-MLSS-RL.pdf:
        Initialize µ ∈Rd,σ ∈Rd
        for iteration = 1,2,... num_iterations do
            Collect num_episodes_per_iteration samples of θi ∼ N(µ,diag(σ))
            Perform a noisy evaluation Ri ∼ θi
            Select the top elite_set_fraction of samples (e.g. p = 0.2), which we’ll call the elite set
            Fit a Gaussian distribution, with diagonal covariance, to the elite set, obtaining a new µ,σ.
        end for
        Return the ﬁnal µ.

        see https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.81.6579&rep=rep1&type=pdf
    """

    def __init__(self, gym_env_name: str, fc_layers: Optional[Tuple[int, ...]] = None, backend: str = None):
        super().__init__(gym_env_name, fc_layers, backend)
        assert False, "CemAgent is currently not available (pending migration of keras-rl to tf2.0)"

    def train(self,
              callbacks: Union[List[core.AgentCallback], core.AgentCallback, None] = None,
              num_iterations: int = 100,
              num_episodes_per_iteration: int = 50,
              max_steps_per_episode: int = 500,
              elite_set_fraction: float = 0.1,
              num_iterations_between_eval: int = 5,
              num_episodes_per_eval: int = 10,
              train_context: core.CemTrainContext = None,
              default_plots: bool = None):
        """Trains a new model using the gym environment passed during instantiation.

        Args:
            callbacks: list of callbacks called during training and evaluation
            num_iterations: number of times the training is repeated (with additional data)
            num_episodes_per_iteration: number of episodes played in each iteration. for each episode a new
                policy is sampled from the current weight distribution.
            max_steps_per_episode: maximum number of steps per episode
            elite_set_fraction: the fraction of policies which are members of the elite set.
                These policies are used to fit a new weight distribution in each iteration.
            num_iterations_between_eval: number of training iterations before the current policy is evaluated.
                if 0 no evaluation is performed.
            num_episodes_per_eval: number of episodes played to estimate the average return and steps
            train_context: training configuration to be used. if set overrides all other training context arguments.
            default_plots: if set adds a set of default callbacks (plot.State, plot.Rewards, plot.Loss,...).
                if None default callbacks are only added if the callbacks list is empty

        Returns:
            train_context: the training configuration containing the loss and sum of rewards encountered
                during training
        """
        if train_context is None:
            train_context = core.CemTrainContext()
            train_context.num_iterations = num_iterations
            train_context.max_steps_per_episode = max_steps_per_episode
            train_context.elite_set_fraction = elite_set_fraction
            train_context.num_iterations_between_eval = num_iterations_between_eval
            train_context.num_episodes_per_eval = num_episodes_per_eval

        super().train(train_context=train_context, callbacks=callbacks, default_plots=default_plots)
        return train_context


class DqnAgent(EasyAgent):
    """creates a new agent based on the Dqn algorithm.

    From wikipedia:
    The DeepMind system used a deep convolutional neural network, with layers of tiled convolutional filters to mimic
    the effects of receptive fields. Reinforcement learning is unstable or divergent when a nonlinear function
    approximator such as a neural network is used to represent Q.
    This instability comes from the correlations present in the sequence of observations, the fact that small updates
    to Q may significantly change the policy and the data distribution, and the correlations between Q and the
    target values.

    The technique used experience replay, a biologically inspired mechanism that uses a random sample of prior actions
    instead of the most recent action to proceed.[2] This removes correlations in the observation sequence and smooths
    changes in the data distribution. Iterative update adjusts Q towards target values that are only periodically
    updated, further reducing correlations with the target.[17]

    see also: https://deepmind.com/research/publications/human-level-control-through-deep-reinforcement-learning
    """

    def train(self,
              callbacks: Union[List[core.AgentCallback], core.AgentCallback, None] = None,
              num_iterations: int = 20000,
              max_steps_per_episode: int = 500,
              num_steps_per_iteration: int = 1,
              num_steps_buffer_preload=1000,
              num_steps_sampled_from_buffer=64,
              num_iterations_between_eval: int = 1000,
              num_episodes_per_eval: int = 10,
              learning_rate: float = 0.001,
              train_context: core.StepsTrainContext = None,
              default_plots: bool = None):
        """Trains a new model using the gym environment passed during instantiation.

        Args:
            callbacks: list of callbacks called during training and evaluation
            num_iterations: number of times the training is repeated (with additional data)
            max_steps_per_episode: maximum number of steps per episode
            num_steps_per_iteration: number of steps played per training iteration
            num_steps_buffer_preload: number of initial collect steps to preload the buffer
            num_steps_sampled_from_buffer: the number of steps sampled from buffer for each iteration training
            num_iterations_between_eval: number of training iterations before the current policy is evaluated.
                if 0 no evaluation is performed.
            num_episodes_per_eval: number of episodes played to estimate the average return and steps
            learning_rate: the learning rate used in the next iteration's policy training (0,1]
            train_context: training configuration to be used. if set overrides all other training context arguments.
            default_plots: if set adds a set of default callbacks (plot.State, plot.Rewards, plot.Loss,...).
                if None default callbacks are only added if the callbacks list is empty

        Returns:
            train_context: the training configuration containing the loss and sum of rewards encountered
                during training
        """
        if train_context is None:
            train_context = core.StepsTrainContext()
            train_context.num_iterations = num_iterations
            train_context.max_steps_per_episode = max_steps_per_episode
            train_context.num_steps_per_iteration = num_steps_per_iteration
            train_context.num_steps_buffer_preload = num_steps_buffer_preload
            train_context.num_steps_sampled_from_buffer = num_steps_sampled_from_buffer
            train_context.num_iterations_between_eval = num_iterations_between_eval
            train_context.num_episodes_per_eval = num_episodes_per_eval
            train_context.learning_rate = learning_rate

        super().train(train_context=train_context, callbacks=callbacks, default_plots=default_plots)
        return train_context


class DoubleDqnAgent(DqnAgent):
    """Agent based on the Double Dqn algorithm (https://arxiv.org/abs/1509.06461)"""


class DuelingDqnAgent(DqnAgent):
    """Agent based on the Dueling Dqn algorithm (https://arxiv.org/abs/1511.06581)."""


class PpoAgent(EasyAgent):
    """creates a new agent based on the PPO algorithm.

        PPO is an actor-critic algorithm using 2 neural networks. The actor network
        to predict the next action to be taken and the critic network to estimate
        the value of the game state we are currently in (the expected, discounted
        sum of future rewards when following the current actor network).

        see also: https://spinningup.openai.com/en/latest/algorithms/ppo.html
    """

    def train(self,
              callbacks: Union[List[core.AgentCallback], core.AgentCallback, None] = None,
              num_iterations: int = 100,
              num_episodes_per_iteration: int = 10,
              max_steps_per_episode: int = 500,
              num_epochs_per_iteration: int = 10,
              num_iterations_between_eval: int = 5,
              num_episodes_per_eval: int = 10,
              learning_rate: float = 0.001,
              train_context: core.PpoTrainContext = None,
              default_plots: bool = None):
        """Trains a new model using the gym environment passed during instantiation.

        Args:
            callbacks: list of callbacks called during training and evaluation
            num_iterations: number of times the training is repeated (with additional data)
            num_episodes_per_iteration: number of episodes played per training iteration
            max_steps_per_episode: maximum number of steps per episode
            num_epochs_per_iteration: number of times the data collected for the current iteration
                is used to retrain the current policy
            num_iterations_between_eval: number of training iterations before the current policy is evaluated.
                if 0 no evaluation is performed.
            num_episodes_per_eval: number of episodes played to estimate the average return and steps
            learning_rate: the learning rate used in the next iteration's policy training (0,1]
            train_context: training configuration to be used. if set overrides all other training context arguments.
            default_plots: if set adds a set of default callbacks (plot.State, plot.Rewards, plot.Loss,...).
                if None default callbacks are only added if the callbacks list is empty

        Returns:
            train_context: the training configuration containing the loss and sum of rewards encountered
                during training
        """
        if train_context is None:
            train_context = core.PpoTrainContext()
            train_context.num_iterations = num_iterations
            train_context.num_episodes_per_iteration = num_episodes_per_iteration
            train_context.max_steps_per_episode = max_steps_per_episode
            train_context.num_epochs_per_iteration = num_epochs_per_iteration
            train_context.num_iterations_between_eval = num_iterations_between_eval
            train_context.num_episodes_per_eval = num_episodes_per_eval
            train_context.learning_rate = learning_rate

        super().train(train_context=train_context, callbacks=callbacks, default_plots=default_plots)
        return train_context


class RandomAgent(EasyAgent):
    """Agent which always chooses uniform random actions."""

    def train(self,
              callbacks: Union[List[core.AgentCallback], core.AgentCallback, None] = None,
              num_iterations: int = 10,
              max_steps_per_episode: int = 1000,
              num_episodes_per_eval: int = 10,
              train_context: core.TrainContext = None,
              default_plots: bool = None):
        """Evaluates the environment using a uniform random policy.

        The evaluation is performed in batches of num_episodes_per_eval episodes.

        Args:
            callbacks: list of callbacks called during training and evaluation
            num_iterations: number of times a batch of num_episodes_per_eval episodes is evaluated.
            max_steps_per_episode: maximum number of steps per episode
            num_episodes_per_eval: number of episodes played to estimate the average return and steps
            train_context: training configuration to be used. if set overrides all other training context arguments.
            default_plots: if set adds a set of default callbacks (plot.State, plot.Rewards, plot.Loss,...)

        Returns:
            train_context: the training configuration containing the loss and sum of rewards encountered
                during training
        """
        if train_context is None:
            train_context = core.TrainContext()
            train_context.num_iterations = num_iterations
            train_context.max_steps_per_episode = max_steps_per_episode
            train_context.num_epochs_per_iteration = 0
            train_context.num_iterations_between_eval = 1
            train_context.num_episodes_per_eval = num_episodes_per_eval
            train_context.learning_rate = 1

        super().train(train_context=train_context, callbacks=callbacks, default_plots=default_plots)
        return train_context


class ReinforceAgent(EasyAgent):
    """creates a new agent based on the Reinforce algorithm.

        Reinforce is a vanilla policy gradient algorithm using a single actor network.

        see also: www-anw.cs.umass.edu/~barto/courses/cs687/williams92simple.pdf
    """

    def train(self,
              callbacks: Union[List[core.AgentCallback], core.AgentCallback, None] = None,
              num_iterations: int = 100,
              num_episodes_per_iteration: int = 10,
              max_steps_per_episode: int = 500,
              num_epochs_per_iteration: int = 10,
              num_iterations_between_eval: int = 5,
              num_episodes_per_eval: int = 10,
              learning_rate: float = 0.001,
              train_context: core.EpisodesTrainContext = None,
              default_plots: bool = None):
        """Trains a new model using the gym environment passed during instantiation.

        Args:
            callbacks: list of callbacks called during training and evaluation
            num_iterations: number of times the training is repeated (with additional data)
            num_episodes_per_iteration: number of episodes played per training iteration
            max_steps_per_episode: maximum number of steps per episode
            num_epochs_per_iteration: number of times the data collected for the current iteration
                is used to retrain the current policy
            num_iterations_between_eval: number of training iterations before the current policy is evaluated.
                if 0 no evaluation is performed.
            num_episodes_per_eval: number of episodes played to estimate the average return and steps
            learning_rate: the learning rate used in the next iteration's policy training (0,1]
            train_context: training configuration to be used. if set overrides all other training context arguments.
            default_plots: if set adds a set of default callbacks (plot.State, plot.Rewards, plot.Loss,...).
                if None default callbacks are only added if the callbacks list is empty

        Returns:
            train_context: the training configuration containing the loss and sum of rewards encountered
                during training
        """
        if train_context is None:
            train_context = core.EpisodesTrainContext()
            train_context.num_iterations = num_iterations
            train_context.num_episodes_per_iteration = num_episodes_per_iteration
            train_context.max_steps_per_episode = max_steps_per_episode
            train_context.num_epochs_per_iteration = num_epochs_per_iteration
            train_context.num_iterations_between_eval = num_iterations_between_eval
            train_context.num_episodes_per_eval = num_episodes_per_eval
            train_context.learning_rate = learning_rate

        super().train(train_context=train_context, callbacks=callbacks, default_plots=default_plots)
        return train_context


class SacAgent(DqnAgent):
    """Agent based on the Soft-Actor-Critic algorithm (https://arxiv.org/abs/1812.05905)."""
