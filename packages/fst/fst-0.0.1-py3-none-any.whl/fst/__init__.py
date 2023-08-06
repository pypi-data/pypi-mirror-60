INTITIAL_STATE = 1
FINAL_STATE = 2
NORMAL_STATE = 3
INITIAL_AND_FINAL_STATE = 4
EPSILON = 5


class Edge(object):
    def __init__(self, src, destination, on_symbol, output):
        self.src = src
        self.dest = destination
        self.on_symbol = on_symbol
        self.op = output
        self.src.add_outgoing_edge(self)
    
    def transit(self, ip):
        return (self.dest, self.op) if self.on_symbol == ip else None
    def __repr__(self):
        return (self.src, self.dest, self.on_symbol, self.op).__repr__()
    def __eq__(self, oth):
        return self.__hash__() == oth.__hash__()
    
    def __hash__(self):
        return (self.src, self.dest, self.on_symbol, self.op).__hash__()


class State(object):
    def __init__(self, name, type):
        if not name:
            raise ValueError("state_name cannot be empty.")
        if not isinstance(name, str):
            raise ValueError('state_name has to be a string.')
        self.name = name
        self.type = type
        self.outgoing_edges = []
    
    def add_outgoing_edge(self, edge):
        assert isinstance(edge, Edge), 'Outgoing Edge must be an instance of Edge.'
        self.outgoing_edges.append(edge)
    
    def transit(self, ip_char):
        return [oe.transit(ip_char) for oe in self.outgoing_edges]
    
    def is_final_state(self):
        return self.type == FINAL_STATE
    
    def __repr__(self):
        return self.name.__repr__()
    
    def __eq__(self, oth):
        if isinstance(oth, str):
            return oth == self.name
        return self.name == oth.name
    
    def __hash__(self):
        return self.name.__hash__()


class FST(object):
    def __init__(self):
        self.states = []
        self.edges = []
        self.init_state = None
    
    def add_state(self, name, state_type=NORMAL):
        new_state = State(name, state_type)
        if new_state in self.states:
            raise ValueError('State already defined.')
        if state_type in (INTITIAL_STATE, INITIAL_AND_FINAL_STATE):
            if self.init_state is not None:
                raise ValueError('FST Cannot have more than one INITIAL_STATE.')
            self.init_state = new_state
        self.states.append(State(name, state_type))

    def add_edge(self, src, dest, on_which_symbol, output):
        if src not in self.states:
            raise ValueError('State {} not defined yet.'.format(src))
        if dest not in self.states:
            raise ValueError('State {} not defined yet.'.format(dest))
        src = self.states[self.states.index(src)]
        dest = self.states[self.states.index(dest)]
        new_edge = Edge(src, dest, on_which_symbol, output)
        if new_edge in self.edges:
            raise ValueError('Edge with same parameters already exists.')
        self.edges.append(new_edge)

    def make_transition_function(self, ip, split_by=''):
        if self.init_state is None:
            raise ValueError('INITIAL_STATE is not defined.')
        output = []
        chars = tuple(ip) if split_by == '' else ip.split(split_by)
        pending_states = set([self.states[self.states.index(self.init_state)]])
        for char in chars:
            new_pending_states = set()
            if not pending_states:
                raise ValueError('No states to transit. FST rejecting the input.')
            for ps in pending_states:
                states_ops = ps.transit(char)
                for ret_value in states_ops:
                    if ret_value is not None:
                        next_state, op = ret_value
                        if op != EPSILON:
                            output.append(op)
                        new_pending_states.add(next_state)
            pending_states = new_pending_states
        pending_states = [state for state in pending_states if state.is_final_state()]
        if not pending_states:
            raise ValueError('Failed Parsing input.')
        return output