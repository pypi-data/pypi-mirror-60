from numerous.engine.system import Item, Subsystem
from numerous.multiphysics import EquationBase, Equation
from numerous.engine.model import Model
from numerous.engine.simulation import Simulation
import numpy as np
import pytest
from pytest import approx


class Item1(Item, EquationBase):
    def __init__(self, tag='item1'):
        super(Item1, self).__init__(tag)
        self.t1 = self.create_namespace('t1')
        self.add_state('x', 1)
        self.add_state('t', 0)
        self.t1.add_equations([self])

    @Equation()
    def eval(self, scope):
        scope.t_dot = 1
        scope.x_dot = -1 * np.exp(-1 * scope.t)



class Subsystem1(Subsystem, EquationBase):
    def __init__(self, tag='subsystem1', item1=object):
        super(Subsystem1, self).__init__(tag)
        self.t1 = self.create_namespace('t1')
        self.add_parameter('x_dot_mod', 0)
        self.t1.add_equations([self])
        self.register_items([item1])

        item1.t1.x_dot += self.t1.x_dot_mod
        print(self.t1.x_dot_mod)

    @Equation()
    def eval(self, scope):
        scope.x_dot_mod = -1


@pytest.fixture
def system1():
    class System(Subsystem, EquationBase):
        def __init__(self, tag='system1', subsystem1=object):
            super(System, self).__init__(tag)

            self.register_items([subsystem1])
    return System(subsystem1=Subsystem1(item1=Item1()))

def expected_sol(t):
    return -1*(t*np.exp(t) -1)*np.exp(-t)

def test_overloadaction_sum(system1):
    model = Model(system1)
    sim = Simulation(model, t_start=0, t_stop=10, num=100)
    sim.solve()
    df = sim.model.historian.df
    assert approx(np.array(df['system1.subsystem1.item1.t1.x']), rel=100) == expected_sol(np.linspace(0, 10, 101)[1:])