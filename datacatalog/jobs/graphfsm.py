from .fsm import JobStateMachine
from transitions.extensions import GraphMachine as Machine

class Model(object):
    pass

def plot_graph():

    class Model(object):
        pass

    m = Model()
    machine = Machine(model=m, states=JobStateMachine.states,
                      transitions=JobStateMachine.transitions, initial='created', title='PipelineJob.FSM')

    # draw the whole graph ...
    machine.get_graph().draw('pipelinejob-fsm.png', prog='dot')
