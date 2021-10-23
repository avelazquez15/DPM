from services import ServiceProvider, ServiceRequestor, ServiceQueue
import numpy as np
import pandas as pd


class Environment:
    @property
    def ble_module(self):
        """
        https://www.ti.com/product/CC2652R7#product-details
        :return:
        """
        return self._ble_module

    @property
    def ios_app(self):
        return self._ios_app

    @property
    def service_queue(self):
        return self._service_queue

    @property
    def environment_shape(self):
        return self._environment_shape

    @environment_shape.setter
    def environment_shape(self, value):
        self._environment_shape = value

    @property
    def inter_arrival(self):
        return self._inter_arrival

    @inter_arrival.setter
    def inter_arrival(self, value):
        self._inter_arrival = value

    @property
    def inter_arrival_timeline(self):
        return self._inter_arrival_timeline

    @inter_arrival_timeline.setter
    def inter_arrival_timeline(self, value):
        self._inter_arrival_timeline = value

    @property
    def requests_arrival(self):
        return self._requests_arrival

    @requests_arrival.setter
    def requests_arrival(self, value):
        self._requests_arrival = value

    @property
    def possible_actions(self):
        return self._possible_actions

    @possible_actions.setter
    def possible_actions(self, actions: list):
        self._possible_actions = actions

    @staticmethod
    def generate_requests(transfer_rate: float) -> int:
        def _required_requests(megabytes, _transfer_rate):
            bytes2bits = 8
            return megabytes * bytes2bits / _transfer_rate

        # average streamed audio song file ranges from 1-8 MBs
        return _required_requests(megabytes=np.random.randint(1, 8), _transfer_rate=transfer_rate)

    def __init__(self,
                 # Environment variables
                 inter_arrivals, episode_duration,
                 # Service Provider variables
                 sq_length: int, sp_state_machine: list, sp_transfer_rate: float, sr_alpha: float):

        self._ble_module = ServiceProvider(state_machine=sp_state_machine, transfer_rate=sp_transfer_rate)
        self._ios_app = ServiceRequestor(states=['idle', 'low', 'high'], alpha=sr_alpha)
        self._service_queue = ServiceQueue(states=list(range(sq_length)))
        column_actions = [_state['state']['command'] for _state in self.ble_module.state_machine
                          if _state['state']['command'] is not None]
        ble_module = len(self.ble_module.states)
        ios_module = len(self.ios_app.states)
        queue_module = len(self.service_queue.states)
        self._possible_actions = column_actions
        state_space = np.array([np.zeros(ble_module * ios_module * queue_module)]*len(self.possible_actions))

        df = pd.DataFrame(data=state_space.T, columns=column_actions)

        # create sp_active row indexes
        sp_active_sr_idle_sq = [f'(sp=active,sr=idle,sq={_n})' for _n in self.service_queue.states]
        sp_active_sr_low_sq = [f'(sp=active,sr=low,sq={_n})' for _n in self.service_queue.states]
        sp_active_sr_high_sq = [f'(sp=active,sr=high,sq={_n})' for _n in self.service_queue.states]
        # create sp_sleep row indexes
        sp_sleep_sr_idle_sq = [f'(sp=sleep,sr=idle,sq={_n})' for _n in self.service_queue.states]
        sp_sleep_sr_low_sq = [f'(sp=sleep,sr=low,sq={_n})' for _n in self.service_queue.states]
        sp_sleep_sr_high_sq = [f'(sp=sleep,sr=high,sq={_n})' for _n in self.service_queue.states]
        # create sp_transient row indexes
        sp_transient_sr_idle_sq = [f'(sp=transient,sr=idle,sq={_n})' for _n in self.service_queue.states]
        sp_transient_sr_low_sq = [f'(sp=transient,sr=low,sq={_n})' for _n in self.service_queue.states]
        sp_transient_sr_high_sq = [f'(sp=transient,sr=high,sq={_n})' for _n in self.service_queue.states]

        # assign row indexes to DataFrame
        df.index = sp_active_sr_idle_sq + sp_active_sr_low_sq + sp_active_sr_high_sq + sp_sleep_sr_idle_sq + \
                   sp_sleep_sr_low_sq + sp_sleep_sr_high_sq + sp_transient_sr_idle_sq + sp_transient_sr_low_sq + \
                   sp_transient_sr_high_sq

        self._environment_shape = df
        self._inter_arrival = inter_arrivals
        self._inter_arrival_timeline = [1 if i in self._inter_arrival else 0 for i in range(0, episode_duration)]
        self._requests_arrival = []

    def stimulate(self, clock: int):

        print(f"\n Environment Stimulated(Clock={clock})")
        if clock in self.inter_arrival:
            client_requests = self.generate_requests(transfer_rate=self.ble_module.transfer_rate)
            # print(f"Client Requested -> {client_requests}")
            self.ios_app.requests = client_requests
            self.service_queue.allocate_space(requests=client_requests)
            self.requests_arrival.append(client_requests)
        else:
            self.requests_arrival.append(0)

        if self.service_queue.is_deque_ready and self.ble_module.current_state == 'active':
            self.service_queue.dequeue_request()

        else:
            self.service_queue.enqueue_request()

        self.ios_app.determine_state()

    def reset(self):
        self.requests_arrival = []