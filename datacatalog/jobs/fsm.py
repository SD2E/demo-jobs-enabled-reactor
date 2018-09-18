from transitions import Machine
import datetime
import inspect
from attrdict import AttrDict
from pprint import pprint
import functools

class JobFSM(AttrDict):
    FILTER_KEYS = ('_id', 'transitions', 'states', 'state', 'machine')
    FILTER_TYPES = (functools.partial)
    pass

class JobStateMachine(object):
    """Load and manage Job state from serialized record"""
    states = ['created', 'running', 'failed', 'finished','validating',
    'validated', 'rejected', 'finalized', 'retired']
    transitions = [
        {'trigger': 'run', 'source': ['created', 'running'], 'dest': 'running'},
        {'trigger': 'update', 'source': ['running'], 'dest': '='},
        {'trigger': 'fail', 'source': '*', 'dest': 'failed'},
        {'trigger': 'finish', 'source': ['running', 'finished'], 'dest': 'finished'},
        {'trigger': 'validate', 'source': 'finished', 'dest': 'validating'},
        {'trigger': 'validated', 'source': 'validating', 'dest': 'validated'},
        {'trigger': 'reject', 'source': 'validating', 'dest': 'rejected'},
        {'trigger': 'finalize', 'source': 'validated', 'dest': 'finalized'},
        {'trigger': 'retire', 'source': [
            'failed', 'finished', 'validating', 'validated', 'validated', 'finalized'], 'dest': 'retired'}
    ]

    def __init__(self, jobdef, status='created'):

        self.data = {}
        ts = current_time()
        for k in jobdef:
            setattr(self, k, jobdef.get(k, None))

        # These will be empty if jobdef refers to a newly created job
        if 'history' not in jobdef:
            self.history = [{'CREATE': {'date': ts, 'data': None}}]
        if 'status' not in jobdef:
            self.status = 'CREATED'
        if 'last_event' not in jobdef:
            self.last_event = 'CREATE'
        if 'updated' not in jobdef:
            self.updated = ts

        initial_state = status
        if getattr(self, 'status') is not None:
            initial_state = getattr(self, 'status')
        self.machine = Machine(
            model=self, states=JobStateMachine.states,
            transitions=JobStateMachine.transitions,
            initial=initial_state.lower(),
            auto_transitions=False,
            after_state_change='update_history')

    def handle(self, event_name, opts={}):
        eventfn = event_name.lower()
        eventname = event_name.upper()
        vars(self)[eventfn](opts, event=eventname)
        return self

    def get_history(self):
        return self.history

    def update_history(self, opts, event):
        ts = current_time()
        history_entry = {}
        history_entry[str(event).upper()] = {'date': ts, 'data': opts}
        self.history.append(history_entry)
        self.status = self.state
        self.last_event = event.upper()
        self.updated = ts

    def as_dict(self):
        pr = {}
        for name in dir(self):
            if name not in JobFSM.FILTER_KEYS:
                value = getattr(self, name)
                if not isinstance(value, JobFSM.FILTER_TYPES):
                    if not name.startswith('__') and not inspect.ismethod(value):
                        pr[name] = value
        return JobFSM(pr)

def current_time():
    return datetime.datetime.utcnow()
