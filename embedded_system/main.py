import numpy as np
import pandas as pd
from environment import Environment
from policies import QLearning
import matplotlib.pyplot as plt


class DPM:

    VERBOSE = False

    @property
    def pcba(self):
        return self._pcba

    @property
    def agent(self):
        return self._agent

    def __init__(self):
        self._pcba = Environment()
        self._agent = QLearning(shape=self.pcba.environment_shape,
                                learning_rate=0.85,
                                discount_factor=0.90)

        self.delta = 1

    def print(self, message: str):
        if self.VERBOSE:
            print(message)

    def run(self):

        duration = 200
        clk = 0
        transitions = []
        requests = []
        queue_requests = []
        while clk < duration:
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
            self.print(f"\nCost(s={self.pcba.ble_module.previous_state}, "
                  f"a={self.pcba.ble_module.previous_action}) -> {real_cost}")

            # calculate previous q_value but don't persist value
            q_min_prime = self.agent.calculate_q_value(state_space=state_space,
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

            # for _sp_state in self.pcba.ble_module.states:
            #
            #     for _sq_state in self.pcba.service_queue.states:
            #         # sp_state_prime = self.pcba.ble_module.state_prime(command=_action)
            #         # virtual_state = previous_state

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

                virtual_q_min_prime = self.agent.calculate_q_value(state_space=state_space,
                                                                   action=_action,
                                                                   cost=virtual_cost,
                                                                   is_virtual_state=True,
                                                                   debug=True)
                #print(self.agent.q_values)
                self.print(f"\n\t__________________ VIRTUAL STATE (END) _______________________________")
            self.print("\n[AFTER]")
            self.print(self.pcba.service_queue.queue)
            #input("Press key to stimulate environment")

            clk += 1
        return transitions, requests, queue_requests


if __name__ == '__main__':

    TOTAL_EPISODES = 20
    episodes = np.array(range(TOTAL_EPISODES))
    dpm = DPM()

    transitions = []
    requests = []
    queue_requests = []

    for _episode in episodes:
        print(f"________________ Starting Episode #{_episode} ________________ ")
        transitions, requests, queue_requests = dpm.run()

    len_state_space = len(dpm.pcba.ble_module.states) * len(dpm.pcba.ios_app.states) * len(dpm.pcba.service_queue.states)

    print("\n\n\tsp=active")
    print(dpm.agent.q_values[0:36])

    print("\n\n\tsp=sleep")
    print(dpm.agent.q_values[36:72])

    print("\n\n\tsp=transient")
    print(dpm.agent.q_values[72:108])

    fig, axs = plt.subplots(2)
    fig.suptitle('')

    axs[0].plot(range(0, 200), queue_requests, label='queue size', color='blue')
    axs[0].stem(dpm.pcba._timeline, label='interarrivals', markerfmt='D')

    axs[1].plot(range(0, 200), transitions, label='transitions', color='red')

    fig.legend()
    plt.show()
