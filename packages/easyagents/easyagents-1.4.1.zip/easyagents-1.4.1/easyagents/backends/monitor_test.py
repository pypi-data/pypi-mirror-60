import unittest

import easyagents.core as core
import easyagents.env
import easyagents.backends.monitor as monitor
import easyagents.backends.debug as debug
import gym


class MonitorTest(unittest.TestCase):

    def setUp(self):
        self.env_name = easyagents.env._StepCountEnv.register_with_gym()
        if self.env_name in monitor._MonitorEnv._monitor_total_counts:
            monitor._MonitorEnv._monitor_total_counts[self.env_name] = monitor._MonitorTotalCounts(self.env_name)
        self.total = monitor._register_gym_monitor(self.env_name)
        self.env: monitor._MonitorEnv = monitor._get(gym.make(self.total.gym_env_name))
        self.env.reset()

    def tearDown(self):
        monitor._MonitorEnv._register_backend_agent(None)
        monitor._MonitorEnv._monitor_total_counts[self.env_name] = monitor._MonitorTotalCounts(self.env_name)

    def test_create(self):
        assert self.env
        assert self.env.total.instances_created == 1
        assert self.env.gym_env_name == self.env_name

    def test_max_steps_per_episode(self):
        self.env.max_steps_per_episode = 3
        while True:
            (state, reward, done, info) = self.env.step(1)
            if done:
                break
            if self.env.steps_done_in_episode > 1000:
                break
        assert self.env.steps_done_in_episode == 3

    def test_register_gym_monitor(self):
        assert self.env_name == self.total._original_env_name
        assert self.total.gym_env_name == monitor._MonitorEnv._NAME_PREFIX + self.env_name
        assert self.total is monitor._MonitorEnv._monitor_total_counts[self.env_name]

    def test_reset_beforeSteps_noEpisodeInc(self):
        self.env.reset()
        self.env.reset()
        assert self.total.episodes_done == 0
        assert self.env.episodes_done == 0

    def test_setbackendagent_twice(self):
        model_config = core.ModelConfig(self.env_name)
        agent = debug.DebugAgent(model_config)
        monitor._MonitorEnv._register_backend_agent(agent)
        monitor._MonitorEnv._register_backend_agent(agent)
        monitor._MonitorEnv._register_backend_agent(None)

    def test_setUp(self):
        assert self.env_name
        assert self.total
        assert self.env


if __name__ == '__main__':
    unittest.main()
