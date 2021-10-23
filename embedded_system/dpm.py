import numpy as np
from environment import Environment
from policies import QLearning
import matplotlib.pyplot as plt
import math


class DPM:

    VERBOSE = False

    @property
    def pcba(self):
        return self._pcba

    @property
    def agent(self):
        return self._agent

    def __init__(self,
                 # Environment variables
                 inter_arrivals, sq_length, sp_state_machine, sp_transfer_rate, sr_alpha,
                 # Policy variables
                 episode_duration, learning_rate, discount_factor,
                 verbose: bool = False):
        self.VERBOSE = verbose
        self._pcba = Environment(inter_arrivals=inter_arrivals,
                                 episode_duration=episode_duration,
                                 sq_length=sq_length,
                                 sp_state_machine=sp_state_machine,
                                 sp_transfer_rate=sp_transfer_rate,
                                 sr_alpha=sr_alpha)
        self._agent = QLearning(shape=self.pcba.environment_shape,
                                learning_rate=learning_rate,
                                discount_factor=discount_factor,
                                verbose=verbose)

        self.delta = 1
        self.episode_duration = episode_duration

    def print(self, message: str):
        if self.VERBOSE:
            print(message)

    def run(self):
        clk = 0
        transitions = []
        queue_requests = []
        power = []
        self.pcba.reset()
        while clk < self.episode_duration:
            print(f"\n________________________CLOCK t = {clk}________________________________________ ")

            if np.random.random() < self.agent.epsilon:
                # take lowest q_value(s, a)
                self.print(f"Taking A'")
                current_sp_state = self.pcba.ble_module.current_state
                current_sr_state = self.pcba.ios_app.current_state
                current_sq_state = self.pcba.service_queue.current_state
                current_state = f'(sp={current_sp_state},sr={current_sr_state},sq={current_sq_state})'

                # best action with minimal Cost() in current state
                min_action = self.agent.q_values.filter(items=[current_state], axis=0).idxmin(axis=1)[0]
                self.print(f'Setting BLE module to {min_action}')
                self.pcba.ble_module.set_power_mode(command=min_action)
                self.pcba.stimulate(clock=clk)
            else:
                # pick a random action to take
                self.print('Randomly picking an action to take')
                possible_actions = self.pcba.possible_actions

                random_action = possible_actions[np.random.randint(0, len(possible_actions))]
                print(f'Setting BLE module to {random_action}')
                self.pcba.ble_module.set_power_mode(command=random_action)
                self.pcba.stimulate(clock=clk)

            transitions.append(self.pcba.ble_module.current_action)
            requests.append(self.pcba.service_queue.requests)
            queue_requests.append(self.pcba.service_queue.current_state)

            self.print(f"Observing my ({self.pcba.ble_module.current_action}) action "
                       f"in my previous state {self.pcba.ble_module.previous_state}")
            # environment state space
            state_space = [self.pcba.ble_module, self.pcba.ios_app, self.pcba.service_queue]

            # calculate previous cost
            real_cost = self.agent.cost_function(state_space=state_space,
                                                 delta=self.delta)
            power.append(real_cost)
            self.print(f"\nCost(sp={self.pcba.ble_module.previous_state}, "
                       f"a={self.pcba.ble_module.previous_action}) -> {real_cost}")

            # calculate previous q_value but don't persist value
            self.agent.calculate_q_value(state_space=state_space,
                                         action=self.pcba.ble_module.previous_action,
                                         cost=real_cost,
                                         debug=True)

            previous_action = self.pcba.ble_module.previous_action
            previous_sp_state = self.pcba.ble_module.previous_state
            previous_sr_state = self.pcba.ios_app.previous_state
            previous_sq_state = self.pcba.service_queue.previous_state
            previous_state = f'(sp={previous_sp_state},sr={previous_sr_state},sq={previous_sq_state})'
            previous_state_action = (previous_state, previous_action)

            current_sp_state = self.pcba.ble_module.current_state
            current_sr_state = self.pcba.ios_app.previous_state
            current_sq_state = self.pcba.service_queue.previous_state
            current_state = f'(sp={current_sp_state},sr={current_sr_state},sq={current_sq_state})'

            # TODO: add support for multiple service providers and service queues
            # for _sp in self.pcba.sps
            #     for _sq in self.pcba.sqs

            for _action in self.pcba.ble_module.actions:
                virtual_state_action = (previous_state, _action)
                self.print(f"\n\t__________________ VIRTUAL STATE ({virtual_state_action}) _______________________________")

                if previous_state_action == virtual_state_action:
                    self.print(f"\t(-) Already processed real State")
                    self.print(f"\n\t__________________ VIRTUAL STATE (END) _______________________________")
                    continue

                print(virtual_state_action)
                # calculate cost for taking action_prime but don't persist value
                virtual_cost = self.agent.cost_function(state_space=state_space,
                                                        is_virtual_state=True,
                                                        delta=self.delta)

                self.print(f"\nCost(S'={current_state}, A'={_action}) -> {virtual_cost}")

                self.agent.calculate_q_value(state_space=state_space,
                                             action=_action,
                                             cost=virtual_cost,
                                             is_virtual_state=True,
                                             debug=True)

                self.print(f"\n\t__________________ VIRTUAL STATE (END) _______________________________")
            self.print(self.pcba.service_queue.queue)

            clk += 1
        return transitions, queue_requests, power

    def report(self, transitions: list, queue_requests: list, power: list):
        ble_state_index = len(self.pcba.ios_app.states) * len(self.pcba.service_queue.states)

        print("\n\n\tsp=active")
        print(self.agent.q_values.iloc[0:ble_state_index])

        print("\n\n\tsp=sleep")
        print(self.agent.q_values.iloc[ble_state_index:ble_state_index*2])

        print("\n\n\tsp=transient")
        print(self.agent.q_values.iloc[ble_state_index*2:ble_state_index*3])

        # FIGURE 1
        plt.figure(1)
        plt.plot(self.pcba.inter_arrival_timeline, label='Interarrivals', color='black', marker='o')
        go_active = [1 if i == 'go_active' else 0 for i in transitions]
        plt.plot(go_active, label='Power Mode')
        plt.yticks([0, 1], ('Sleep', 'Active'))
        plt.ylabel('Power Mode / Interarrivals')
        plt.xlabel('Cycle')
        plt.title('Service Provider - Power Mode')
        plt.minorticks_on()
        plt.legend()

        # FIGURE 2
        plt.figure(2)
        rms_queue_requests = [float(i) ** 2 / len(queue_requests) for i in queue_requests]
        rms_queue_requests = math.sqrt(sum(rms_queue_requests))
        plt.plot(np.ones(self.episode_duration) * rms_queue_requests, label='RMS Requests In Queue', color='green', linestyle='dashed')
        plt.stem(range(0, self.episode_duration), queue_requests, label='Requests In Queue')  # , color='blue
        plt.annotate(f"{rms_queue_requests:0.2f} Requests", xy=(95, rms_queue_requests*1.1))
        plt.ylabel('Number Of Requests')
        plt.xlabel('Cycle')
        plt.title('Service Queue (w/ Length = 12) - Requests')
        plt.minorticks_on()
        plt.xlabel('Cycle')
        plt.legend()

        # FIGURE 3
        plt.figure(3)
        rms_power_dpm = [float(i) ** 2 / len(power) for i in power]
        rms_power_dpm = math.sqrt(sum(rms_power_dpm))
        active_power_mode = self.pcba.ble_module.state_machine[0]['state']['power']
        sleep_power_mode = self.pcba.ble_module.state_machine[1]['state']['power']
        power_always_active = [i * active_power_mode if i > 0 else sleep_power_mode for i in self.pcba.requests_arrival]
        rms_power_always_active = [float(i) ** 2 / len(power_always_active) for i in power_always_active]
        rms_power_always_active = math.sqrt(sum(rms_power_always_active))
        plt.plot(power, label='Power - (DPM)')
        plt.plot(np.ones(self.episode_duration) * rms_power_dpm, label='RMS Power - (DPM)', linestyle='dashed')
        plt.plot(np.ones(self.episode_duration) * power_always_active, label='Power - (Process Immediately)')
        plt.plot(np.ones(self.episode_duration) * rms_power_always_active, label='RMS Power - (Process Immediately)',
                 linestyle='dashed')
        plt.annotate(f"{rms_power_dpm:0.2f} mW", xy=(95, rms_power_dpm+5))
        plt.annotate(f"{rms_power_always_active:0.2f} mW", xy=(65, rms_power_always_active+5))
        plt.ylabel('(mW)')
        plt.xlabel('Cycle')
        plt.title('Service Provider - Power Cost ')
        plt.minorticks_on()
        plt.legend()

        plt.show()


if __name__ == '__main__':

    TOTAL_EPISODES = 20
    episodes = np.array(range(TOTAL_EPISODES))
    sp_state_machine = [{
        'state': {
            'power_mode': 'active',
            #  P = IxV = (3.87 mA x 3.3V) = 12.771 mW
            'power': 12.771,
            'command': 'go_active',
            'init': False
            }
    }, {
        'state': {
            'power_mode': 'sleep',
            # P = IxV = (0.669 mA x 3.3V) = 2.2077 mW
            'power': 2.2077,
            'command': 'go_sleep',
            'init': True
        }
    }, {
        'state': {
            'power_mode': 'transient',
            'transient_timing': {
                'sleep2active': 80,
                'active2sleep': 36
            },
            'command': None,
            'init': False
    }}]

    dpm = DPM(inter_arrivals=[1, 2, 3, 4, 10, 11, 12, 13, 60, 61],
              episode_duration=100,
              learning_rate=0.80,
              discount_factor=0.10,
              sq_length=12,
              sp_state_machine=sp_state_machine,
              sp_transfer_rate=2.0,
              sr_alpha=1.0,
              verbose=False)

    transitions = []
    requests = []
    queue_requests = []
    power = []

    for _episode in episodes:
        print(f"________________ Starting Episode #{_episode} ________________ ")
        transitions, queue_requests, power = dpm.run()

    dpm.report(transitions, queue_requests, power)
