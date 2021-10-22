from abc import ABC
from services import ServiceProvider, ServiceRequestor, ServiceQueue

"""
Q-learning is an off-policy method in which the agent learns the value based on action a* derived from the 
another policy, SARSA (State-Action-Reward-State-Action) is an on-policy method where it learns the value based on its 
current action a that's derived from its current policy. 
"""


class Policy(ABC):

    LEARNING_MODE = 1.0
    EXPLORATION_MODE = 0.0
    NEAR_FUTURE = 1.0
    FAR_FUTURE = 0.0

    @property
    def epsilon(self):
        """
        :return: The learning rate
        """
        return self._epsilon

    @epsilon.setter
    def epsilon(self, learning_rate: float):
        """
        Set the epsilon learning rate value.
        :param learning_rate: Value between 0 <= ``learning_rate`` <= 1
        :return: None
        """
        self._epsilon = learning_rate

    @property
    def gamma(self):
        """
        :return: The discount factor.
        """
        return self._gamma

    @gamma.setter
    def gamma(self, discount_factor: float):
        """
        Set the gamma discount factory value.
        :param discount_factor:  Value between 0 <= ``discount_factor`` <= 1
        :return:
        """
        self._gamma = discount_factor

    @property
    def q_values(self):
        return self._q_values

    @q_values.setter
    def q_values(self, shape):
        self._q_values = shape

    def __init__(self, q_values, epsilon=LEARNING_MODE, gamma=NEAR_FUTURE):
        self._epsilon = epsilon
        self._gamma = gamma
        self._q_values = q_values


class QLearning(Policy):
    VERBOSE = False

    def __init__(self,
                 shape: tuple,
                 learning_rate: float = Policy.LEARNING_MODE,
                 discount_factor: float = Policy.NEAR_FUTURE,
                 verbose: bool = False):
        super().__init__(q_values=shape, epsilon=learning_rate, gamma=discount_factor)
        self.VERBOSE = verbose

    def print(self, message: str):
        if self.VERBOSE:
            print(message)

    def calculate_q_value(self,
                          state_space: list[ServiceProvider, ServiceRequestor, ServiceQueue],
                          action: str,
                          cost: float,
                          is_virtual_state: bool = False,
                          debug: bool = False):

        # beginning of calculate_q_value() function
        service_provider, service_requester, service_queue = state_space

        if is_virtual_state:
            # get current_state for SR, SQ, and the projected next state for SP
            sp_state = service_provider.current_state
            sp_state_prime = service_provider.state_prime(command=action)
            sr_state = service_requester.current_state
            sq_state = service_queue.current_state

        else:
            # get previous_state for SR, SQ, and current_state for SP
            sp_state = service_provider.previous_state
            sp_state_prime = service_provider.current_state
            sr_state = service_requester.previous_state
            sq_state = service_queue.previous_state

        # real current-state
        sp_sr_sq_state = f'(sp={sp_state},sr={sr_state},sq={sq_state})'
        sp_sr_sq_state_prime = f'(sp={sp_state_prime},sr={sr_state},sq={sq_state})'

        action_prime = self.q_values.filter(items=[sp_sr_sq_state_prime], axis=0).idxmin(axis=1)[0]

        # sp_state, sr_sq_state = state
        old_q_value = self.q_values[action][sp_sr_sq_state]

        # .filter(items=[], axis=0) will filter the DataFrame row-wise (axis=0) returning the matching row in items
        # .min()[0] returns the value of the column with the minimum value
        # .filter(items=[_state_prime], axis=0).min()[0]
        min_q_prime = self.q_values[action_prime][sp_sr_sq_state_prime]

        # _q_value = (1 - _epsilon) * _old_q_value + _epsilon * (_cost + _min_q_prime)
        q_value = old_q_value + self.epsilon * (cost + self.gamma * min_q_prime - old_q_value)

        if debug:
            if is_virtual_state:
                self.print('\t___ VIRTUAL STATE ___')

            self.print(f"Cost(s={sp_sr_sq_state},a={action}) -> {cost}")
            self.print(f"Q(s={sp_sr_sq_state}, a={action}) -> {q_value}")
            self.print(f"Q(s'={sp_sr_sq_state_prime}, a'={action_prime}) -> {min_q_prime}")

        if is_virtual_state:
            self.q_values.loc[sp_sr_sq_state][action_prime] = q_value

        else:
            self.q_values.loc[sp_sr_sq_state][action] = q_value

        return q_value

    @staticmethod
    def cost_function(state_space: list[ServiceProvider, ServiceRequestor, ServiceQueue],
                      is_virtual_state: bool = False,
                      delta: float = 0.0):

        def _power_cost(_state_action: dict):
            _state_machine = _state_action['service_provider']['state_machine']
            _sp_state = _state_action['service_provider']['state']

            for _sp_item in _state_machine:
                if _sp_item['state']['power_mode'] == _sp_state:
                    return _sp_item['state']['power']

        def _performance_penalty(_state_action: dict):
            return _state_action['service_queue']['state']

        service_provider, service_requester, service_queue = state_space

        sp_state = service_provider.previous_state
        sr_state = service_requester.previous_state
        sq_state = service_queue.previous_state
        if is_virtual_state:
            sp_state = service_provider.current_state
            sq_state = service_queue.current_state

        # check for transient state
        if sp_state == 'transient':
            for _state in service_provider.state_machine:
                if _state['state']['power_mode'] == 'transient':
                    PA2B = 0
                    TA2B = _state['state']['transient_timing']['sleep2active']
                    PB2A = 0
                    TB2A = _state['state']['transient_timing']['active2sleep']

                    if _state['state']['power_mode'] == 'active':
                        PB2A = _state['state']['power']

                    elif _state['state']['power_mode'] == 'sleep':
                        PA2B = _state['state']['power']

                    return (PA2B * TA2B + PB2A * TB2A) / 2.0

        else:
            state_action = {'service_provider': {'state_machine': service_provider.state_machine,
                                                 'state': sp_state},
                            'service_requester': {'state': sr_state},
                            'service_queue': {'state': sq_state}}

            return _power_cost(_state_action=state_action) + delta*_performance_penalty(_state_action=state_action)
