import unittest

from easyagents import core, env, agents
from easyagents.backends import tfagents
from easyagents.backends import core as bcore
from easyagents.callbacks import duration, log

agents.seed = 0
_lineworld_name = env._LineWorldEnv.register_with_gym()
_stepcount_name = env._StepCountEnv.register_with_gym()
_mountaincar_continuous_name = 'MountainCarContinuous-v0'


class TfDqnAgentTest(unittest.TestCase):

    def setUp(self):
        self.env_name = env._StepCountEnv.register_with_gym()

    def test_train(self):
        model_config = core.ModelConfig("CartPole-v0")
        tc = core.StepsTrainContext()
        dqn_agent = tfagents.TfDqnAgent(model_config=model_config)
        dqn_agent.train(train_context=tc, callbacks=[duration.Fast(), log.Iteration()])


class TfPpoAgentTest(unittest.TestCase):

    def setUp(self):
        self.env_name = env._StepCountEnv.register_with_gym()

    def test_train(self):
        model_config = core.ModelConfig(_lineworld_name)
        tc = core.PpoTrainContext()
        ppo_agent = tfagents.TfPpoAgent(model_config=model_config)
        ppo_agent.train(train_context=tc, callbacks=[duration.Fast(), log.Iteration()])

    def test_save_load(self):
        model_config = core.ModelConfig(_lineworld_name)
        tc = core.PpoTrainContext()
        ppo_agent = tfagents.TfPpoAgent(model_config=model_config)
        ppo_agent.train(train_context=tc, callbacks=[duration._SingleIteration(), log.Iteration()])
        tempdir = bcore._get_temp_path()
        bcore._mkdir(tempdir)
        ppo_agent.save(tempdir, [])
        ppo_agent = tfagents.TfPpoAgent(model_config=model_config)
        ppo_agent.load(tempdir, [])
        pc = core.PlayContext()
        pc.max_steps_per_episode = 10
        pc.num_episodes = 1
        ppo_agent.play(play_context=pc, callbacks=[])
        bcore._rmpath(tempdir)


class TfRandomAgentTest(unittest.TestCase):

    def test_train(self):
        model_config = core.ModelConfig(_lineworld_name)
        tc = core.TrainContext()
        random_agent = tfagents.TfRandomAgent(model_config=model_config)
        random_agent.train(train_context=tc, callbacks=[duration.Fast(), log.Iteration()])
        assert tc.episodes_done_in_iteration == 1

    def test_play(self):
        model_config = core.ModelConfig(_lineworld_name)
        random_agent = tfagents.TfRandomAgent(model_config=model_config)
        pc = core.PlayContext()
        pc.max_steps_per_episode = 10
        pc.num_episodes = 1
        random_agent.play(play_context=pc, callbacks=[])
        assert pc.num_episodes == 1

    def test_save_load(self):
        model_config = core.ModelConfig(_lineworld_name)
        random_agent = tfagents.TfRandomAgent(model_config=model_config)
        tempdir = bcore._get_temp_path()
        bcore._mkdir(tempdir)
        random_agent.save(directory=tempdir, callbacks=[])
        random_agent.load(directory=tempdir, callbacks=[])
        bcore._rmpath(tempdir)


class TfReinforceAgentTest(unittest.TestCase):

    def test_train(self):
        model_config = core.ModelConfig(_lineworld_name)
        tc = core.EpisodesTrainContext()
        reinforce_agent = tfagents.TfReinforceAgent(model_config=model_config)
        reinforce_agent.train(train_context=tc, callbacks=[duration.Fast(), log.Iteration()])
        assert tc.episodes_done_in_iteration == tc.num_episodes_per_iteration > 0
        assert tc.iterations_done_in_training == tc.num_iterations > 0


class TfSacAgentTest(unittest.TestCase):

    def setUp(self):
        self.env_name = env._StepCountEnv.register_with_gym()

    def test_train(self):
        model_config = core.ModelConfig(_mountaincar_continuous_name)
        tc = core.StepsTrainContext()
        dqn_agent = tfagents.TfSacAgent(model_config=model_config)
        dqn_agent.train(train_context=tc, callbacks=[duration.Fast(), log.Iteration(), log.Agent()])


if __name__ == '__main__':
    unittest.main()
