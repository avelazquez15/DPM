from abc import ABC, abstractmethod
from collections import deque


class Service(ABC):

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value

    @property
    def states(self):
        return self._states

    @states.setter
    def states(self, states: list):
        self._states = states

    def __init__(self, states: list, alpha: float = 1.0):
        self._states = states
        self._alpha = alpha


class ServiceProvider(Service):

    @property
    def transfer_rate(self):
        return self._transfer_rate

    @transfer_rate.setter
    def transfer_rate(self, rate):
        self._transfer_rate = rate

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        self._current_state = new_state

    @property
    def previous_state(self):
        return self._previous_state

    @previous_state.setter
    def previous_state(self, state):
        self._previous_state = state

    @property
    def next_state(self):
        return self._next_state

    @next_state.setter
    def next_state(self, state):
        self._next_state = state

    @property
    def action_prime(self):
        return self._action_prime

    @action_prime.setter
    def action_prime(self, value):
        self._action_prime = value

    @property
    def current_action(self):
        return self._current_action

    @current_action.setter
    def current_action(self, action):
        self._current_action = action

    @property
    def previous_action(self):
        return self._previous_action

    @previous_action.setter
    def previous_action(self, action):
        self._previous_action = action

    @property
    def actions(self):
        return [_state['state']['command'] for _state in self.state_machine if _state['state']['command'] is not None]

    @property
    def state_machine(self):
        return self._state_machine

    @state_machine.setter
    def state_machine(self, value):
        self._state_machine = value

    def __init__(self, state_machine: list, transfer_rate: float):
        super().__init__(states=[_state['state']['power_mode'] for _state in state_machine])

        self._state_machine = state_machine
        self._transfer_rate = transfer_rate

        # init states
        for _state in state_machine:
            if _state['state']['init']:
                self._current_state = _state['state']['power_mode']
                self._current_action = _state['state']['command']

        # previous states
        self._previous_state = self.current_state
        self._next_state = self.current_state
        # previous actions
        self._action_prime = self.current_action
        self._previous_action = self.current_action

    def state_prime(self, command):
        for _state in self.state_machine:
            sp_commands = _state['state']['command']
            sp_state = _state['state']['power_mode']

            if command == sp_commands and sp_state == 'active':
                return 'sleep'

            elif command == sp_commands and sp_state == 'sleep':
                return 'active'

    def set_power_mode(self, command: str):
        """
        :param command:
        :return:
        """

        if self.current_state == 'transient':
            self.previous_state = self.current_state
            self.current_state = self.next_state
            return

        self.previous_action = self.current_action
        self.current_action = command

        if self.current_state == 'active' and command == 'go_sleep':
            self.next_state = 'sleep'
            self.current_state = 'transient'

        elif self.current_state == 'active' and command == 'go_active':
            self.previous_state = self.current_state
            self.current_state = 'active'

        elif self.current_state == 'sleep' and command == 'go_active':
            self.next_state = 'active'
            self.current_state = 'transient'

        elif self.current_state == 'sleep' and command == 'go_sleep':
            self.previous_state = self.current_state
            self.current_state = 'sleep'


class ServiceRequestor(Service):

    @property
    def alpha(self) -> float:
        return self._alpha

    @alpha.setter
    def alpha(self, value: float):
        self._alpha = value

    @property
    def ema(self) -> float:
        return self._ema

    @ema.setter
    def ema(self, value: float):
        self._ema = value

    @property
    def requests(self) -> int:
        return self._requests

    @requests.setter
    def requests(self, requests: int):
        self._requests = requests

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        self._current_state = new_state

    @property
    def previous_state(self):
        return self._previous_state

    @previous_state.setter
    def previous_state(self, state):
        self._previous_state = state

    def __init__(self, states: list, alpha: float):
        super().__init__(states=states, alpha=alpha)
        self._ema = 0
        self._requests = 0
        self._current_state = states[0]
        self._previous_state = self.current_state
        # EMAi = α · sri  + (1 − α) · EMAi−1

    def _get_ema_bounds(self, state_index):
        """

        :param state_index: state index
        :return: Tuple containing the (lower_bound, upper_bound)
        """
        """
            0 -> [0, 2−N/2+1 EM A]
            N -> [2N/2−1 EM A, ∞]
        """

        N = len(self.states)
        x = ((-1*N)/2)+state_index  # exponent
        return pow(2, x)*self.ema, pow(2, (x+1))*self.ema

    def determine_state(self):

        # Exponential Weighted Moving Average function
        self.ema = self.alpha * self.requests + self.ema * (1 - self.alpha)
        self.previous_state = self.current_state

        lowest_lower_bound = 0
        # iterate over all states
        for _state in self.states:
            i = self.states.index(_state)
            lower_bound, upper_bound = self._get_ema_bounds(state_index=i)

            # keep track of the lowest lower bound
            if i == 0:
                lowest_lower_bound = lower_bound

            # check if incoming requests is between the EMA lower and upper bounds
            if lower_bound < self.requests < upper_bound:
                self.current_state = _state

            # reached the last state
            # incoming requests didn't fit into any EMA bounds
            # assign to last state if incoming requests is larger then the highest upper bound
            elif i == (len(self.states) - 1) and self.requests > upper_bound:
                self.current_state = _state

            # reached the last state
            # incoming requests didn't fit into any EMA bounds
            # assign to first state if incoming requests is smaller then the lowest lower bound
            elif i == (len(self.states) - 1) and self.requests <= lowest_lower_bound:
                self.current_state = self.states[0]


class ServiceQueue(Service):

    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, value):
        self._queue = value

    @property
    def requests(self):
        return self._requests

    @requests.setter
    def requests(self, request):
        self._requests = request

    @property
    def current_size(self):
        if self.queue:
            return len(self.queue)

        else:
            return 0

    @property
    def current_state(self):
        return self.current_size

    @property
    def previous_state(self):
        return self._previous_state

    @previous_state.setter
    def previous_state(self, state):
        self._previous_state = state

    @property
    def is_deque_ready(self):
        return self._is_deque_ready

    @is_deque_ready.setter
    def is_deque_ready(self, value):
        self._is_deque_ready = value

    @property
    def space_available(self):
        return len(self.states) - self.current_size - 1

    def __init__(self, states: list):
        super().__init__(states=states)
        self._queue = deque()
        self._requests = 0
        self._previous_state = self.current_state
        self._is_deque_ready = False

    def state_prime(self):

        if self.deque_ready and self.current_size > 0:
            return self.current_state - 1

        elif not self.deque_ready and self.space_available > 0:
            return self.current_state + 1

        else:
            return 0

    def allocate_space(self, requests: int):
        if requests <= (self.space_available - self.requests):
            self.requests += requests
            return True

        else:
            return False

    def enqueue_request(self):
        self.previous_state = self.current_state

        self.is_deque_ready = False
        if self.requests > 0 and self.space_available > 0:

            self.queue.append(1)
            self.requests -= 1

        # done enqueuing
        if self.requests == 0:
            self.is_deque_ready = True

        return self.is_deque_ready

    def dequeue_request(self):

        self.previous_state = self.current_state
        self.is_deque_ready = True
        if self.current_size > 0:
            self.queue.popleft()

            # done dequeuing
            if self.current_size == 0:
                self.is_deque_ready = False

        return self.is_deque_ready
