import numpy as np
import random
import math
from RMDP_ml.Math.Geometry import distance


class Q_learning:
    def __init__(self, center: list, side_length: float):
        # orders、agents、resturants info
        self.Ds_0, self.D_x, self.D_y = generateTestData.importOrderValue()
        self.vehiceList, self.vehiclelist_x, self.vehiclelist_y = generateTestData.importVehicleValue()
        self.restaurantList, self.restauranList_x, self.restauranList_y = generateTestData.importRestaurantValue()

        # q_table setting
        self.state_index = 2500
        self.action_index = 2
        self.q_table = np.zeros((self.state_index, self.action_index))
        self.old_qtable = np.zeros((self.state_index, self.action_index))
        self.center = center  # [5,4]
        self.side_length = side_length*2
        self.total_episodes = 20000       # Total episodes
        self.learning_rate = 0.8          # Learning rate
        self.max_orders = 50               # Max orders per episode
        self.gamma = 0.95                 # Discounting rate
        self.epsilon = 1.0                 # Exploration rate
        self.max_epsilon = 1.0             # Exploration probability at start
        self.min_epsilon = 0.01            # Minimum exploration probability
        self.decay_rate = 0.005            # Exponential decay rate for exploration prob
        self.nearBY = 5                    # most nearby agent

        self.agentPosition = []
        self.agentPosition_index = []
        self.capacity = 5
        for i in range(0, len(self.vehiceList)):
            temp = np.zeros((5, 2))
            self.agentPosition.append(temp)
            self.agentPosition_index.append(0)
        self.index = 0

    def Qing(self):
        for episode in range(self.total_episodes):

            for order in self.Ds_0:
                rest_pos = np.array([1, 1])
                delivery_pos = np.array([10, 7])
                agents_dis = np.zeros((self.nearBY, 1))  # 存距離
                agents = []  # vehicle class
                counter = 0
                for v in self.vehiceList:
                    v_capacity = 0
                    if v_capacity >= self.capacity:
                        continue
                    vehicle_pos = [4, 8]
                    dist = distance(
                        vehicle_pos[0], rest_pos[0], vehicle_pos[1], rest_pos[1])
                    if counter < 5:
                        agents_dis[counter] = dist
                        agents.append(v)
                        counter += 1
                    else:
                        index = np.argmax(agents_dis)
                        if agents_dis[index] > dist:
                            agents_dis[index] = dist
                            agents[index] = v

                action = 0
                agent = 0
                for agent in agents:
                    agent_pos = np.array([4, 8])
                    state = abs(self.center-agent_pos)/(self.side_length/50)
                    state = state[0]*50+state[1]
                    # decide action
                    exp_exp_tradeoff = random.uniform(0, 1)
                    if exp_exp_tradeoff > self.epsilon:
                        action = np.argmax(self.q_table[state, :])
                    else:
                        action = random.randint(0, 1)
                    if action == 1:
                        break
                # if all agent false take order
                if action == 0:
                    agent = agents[random.randint(0, 5)]
                    state = abs(self.center-agent)/(self.side_length/50)
                    state = state[0]*50+state[1]
                    action = 1

                # check if agent has order not finish yet
                agent = 0
                agent_capacity = 0
                agent_index = 0  # index of vehicle
                old_state = 0
                old_reward = 0
                order_index = 0
                if agent_capacity > 0:
                    old_state = self.agentPosition[agent_index]
                    old_reward = self.old_qtable[old_state, 1]
                    self.q_table[old_state, 1] = old_reward

                # Take the action with environment
                self.agentPosition[agent_index][self.agentPosition_index[agent_index]] = [
                    state, order_index]
                self.agentPosition_index[agent_index] += 1
                new_state = np.array([self.Ds_info.x, self.Ds_info.y])
                reward = 0  # (resturant to delivery distance)/(finish time)

                # update q_table
                self.old_qtable = self.q_table[state, action]
                self.agentPosition[agent_index] = state
                self.q_table[state, action] = self.q_table[state,
                                                           action]+self.learning_rate*(reward+self.gamma*np.max(self.q_table[new_state, :])-self.q_table[state, action])

            # reduce episode
            self.epsilon = self.min_epsilon + \
                (self.max_epsilon-self.min_epsilon) * \
                np.exp(-self.decay_rate*episode)

    # reward = resturant&delivery distance / finish time
    def real_reward(self, agent_index, order_index, reward):
        states = self.agentPosition[agent_index]
        for i in states:
            if states[0] == order_index:
                state = states[1]
        self.q_table[state, 1] = reward
