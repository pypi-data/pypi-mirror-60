import unittest
import tempfile
import os
import math

from easyagents import agents, core
from easyagents.callbacks import duration, plot


class PlotTest(unittest.TestCase):

    def test_is_nan(self):
        p = plot._PlotCallback(core.PlotType.PLAY_STEP)
        assert not p._is_nan([])
        assert not p._is_nan(None)
        assert not p._is_nan([1])
        assert not p._is_nan([1,2])
        assert not p._is_nan([math.nan,1])
        assert p._is_nan([math.nan])
        assert p._is_nan([math.nan,math.nan])

    def test_play_plotstate(self):
        agent = agents.PpoAgent("CartPole-v0")
        agent.train([duration._SingleEpisode()])
        agent.play([plot.State()])

    def test_play_plotrewards(self):
        agent = agents.PpoAgent("CartPole-v0")
        agent.train([duration._SingleIteration()])
        agent.play([plot.Rewards()])

    def test_train_plotsteprewards(self):
        rndAgent = agents.RandomAgent('CartPole-v0')
        rndAgent.play([plot.StepRewards()] )

    def test_default_plots_False_nocallback(self):
        agent = agents.PpoAgent("CartPole-v0")
        p = plot.Loss()
        c = agent._add_plot_callbacks([], False, [p])
        assert not p in c

    def test_default_plots_None_durationcallback(self):
        agent = agents.PpoAgent("CartPole-v0")
        p = plot.Loss()
        c = agent._add_plot_callbacks([duration.Fast()], None, [p])
        assert p in c

    def test_default_plots_None_nocallback(self):
        agent = agents.PpoAgent("CartPole-v0")
        p = plot.Loss()
        c = agent._add_plot_callbacks([], None, [p])
        assert p in c

    def test_default_plots_None_plotcallback(self):
        agent = agents.PpoAgent("CartPole-v0")
        p = plot.Loss()
        r = plot.Rewards()
        c = agent._add_plot_callbacks([r], None, [p])
        assert not p in c
        assert r in c

    def test_default_plots_True_plotcallback(self):
        agent = agents.PpoAgent("CartPole-v0")
        p = plot.Loss()
        r = plot.Rewards()
        c = agent._add_plot_callbacks([r], True, [p])
        assert p in c
        assert r in c

    def test_train_plotsteprewards(self):
        ppoAgent = agents.PpoAgent('CartPole-v0')
        ppoAgent.train([plot.StepRewards(), duration.Fast()] )

    def test_train_plotloss(self):
        agent = agents.PpoAgent("CartPole-v0")
        agent.train([duration._SingleIteration(), plot.Loss()])

    def test_train_plotrewards(self):
        agent = agents.PpoAgent("CartPole-v0")
        agent.train([duration._SingleIteration(), plot.Rewards()])

    def test_train_plotstate(self):
        agent = agents.PpoAgent("CartPole-v0")
        agent.train([duration._SingleIteration(), plot.State()])

#    def test_train_plotstate_tensorforce(self):
#        agent = agents.PpoAgent("CartPole-v0", backend='tensorforce')
#        agent.train([duration.Fast(), plot.State()])

    def test_train_plotsteps(self):
        agent = agents.PpoAgent("CartPole-v0")
        agent.train([duration._SingleIteration(), plot.Steps()])

    def test_train_multiple_subplots(self):
        agent = agents.PpoAgent("CartPole-v0")
        agent.train([duration._SingleIteration(), plot.State(), plot.Rewards(), plot.Loss(), plot.Steps()])

    def test_train_tomovie(self):
        agent = agents.PpoAgent("CartPole-v0")
        agent.train([duration._SingleIteration(), plot.Rewards(), plot.ToMovie()])

    def test_train_tomovie_with_filename(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        filepath = f.name
        f.close()
        os.remove(filepath)
        assert not os.path.isfile(filepath)
        filepath += '.gif'
        agent = agents.PpoAgent("CartPole-v0")
        m = plot.ToMovie(filepath=filepath, fps=10)
        agent.train([duration._SingleIteration(), plot.Rewards(), m])
        try:
            os.remove(m.filepath)
        except:
            pass

if __name__ == '__main__':
    unittest.main()
