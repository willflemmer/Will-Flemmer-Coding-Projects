import gym
from keras.optimizers import Adam
from collections import deque
import random
import time
import matplotlib.pyplot as plt
from keras.layers import Dense, Input, GaussianNoise
from keras.models import Model
import numpy as np
from keras.layers import Conv2D, BatchNormalization, Activation, Add


def identity_block_dense(x, list_of_layers, stage, block):

    #Define Naming Process:
    dense_name_base = 'res' + str(stage) + block
    bn_name_base = 'bn' + str(stage) + block
    
    
    #copying x:
    x_short = x
    
    #First component of main path:
    x = Dense(list_of_layers[0], name = dense_name_base + 'A')(x)
    #x = BatchNormalization(axis = 1, name = bn_name_base + 'A')(x)
    x = Activation('relu')(x)
    
    #Second Component of main path:
    x = Dense(list_of_layers[1], name = dense_name_base + 'B')(x)
    #x = BatchNormalization(axis = 1, name = bn_name_base + 'B')(x)
    x = Activation('relu')(x)
    
    #Third Component of main path:
    x = Dense(list_of_layers[2], name = dense_name_base + 'C')(x)
    #x = BatchNormalization(axis = 1, name = bn_name_base + 'C')(x)
    
    x = Add()([x, x_short])
    
    x = Activation('relu')(x)
    
    return x


class MountainCarDQN:
    def __init__(self, env):
        self.env = env
        
        self.action_space = env.action_space.n
        self.observation_space = env.observation_space.shape
        self.input_dims = self.observation_space[0]
        
        self.epsilon = 0
        self.min_epsilon = 0.1
        self.epsilon_decay = 0.05
        
        self.gamma = 0.99
        self.learning_rate = 0.001
        self.replay_buffer = deque(maxlen = 20000)
        self.batch_size = 32
        
        self.main_net = self.create_net()
        self.target_net = self.create_net()
        self.target_net.set_weights(self.main_net.get_weights())
        self.network_sync_counter = 0
        self.SYNC_EVERY = 5
        
    def create_net(self):

        input1 = Input(shape = (self.input_dims, ))
        #dense1 = Dense(24, activation = 'relu')(input1)
        #gauss1 = GaussianNoise(0.017)(dense1)
        #dense2 = Dense(24, activation = "relu")(gauss1)
        
        '''
        res1 = identity_block_dense(gauss1, [16, 16, 24], 1, 'res-1')
        res2 = identity_block_dense(res1, [16, 16, 24], 1, 'res-2')
        res3 = identity_block_dense(res2, [16, 16, 24], 1, 'res-3')
        res4 = identity_block_dense(res3, [16, 16, 24], 1, 'res-4')
        res5 = identity_block_dense(res4, [16, 16, 24], 1, 'res-5')
        res6 = identity_block_dense(res5, [16, 16, 24], 1, 'res-6')
        '''
        
        dense3 = Dense(1000, activation = "relu")(input1)
        #gauss2 = GaussianNoise(0.017)(dense3)
        dense2 = Dense(1000, activation = 'relu')(dense3)
        values = Dense(self.action_space, activation =  'linear')(dense2)
        
        
        model_f = Model(inputs = [input1], outputs = [values])      
        model_f.compile(optimizer = Adam(learning_rate = self.learning_rate), loss = 'mse')
        model = model_f
        
        return model
    
    def exploit_rollout(self,state, action):
        done = False
        total_reward = 0
        #print('rollout')
        new_state, reward, done, info = env.step(action)
        total_reward +=reward
        state = np.array([new_state]) 
        while not done:
            #print('state', state)
            actions = self.main_net.predict(state)[0]
            #print('actions', actions)
            action = np.argmax(actions)
            #print('action', action)
            new_state, reward, done, info = env.step(action)
            total_reward +=reward
            state = np.array([new_state]) 
            
        return total_reward
    
    def choose_best_action(self, state):
        ar_list =[]
        #print('choosing best action')
        for action in range(self.env.action_space.n):
            reward = self.exploit_rollout(state, action)
            ar_list.append((action, reward))
            
        best_action = 0
        best_r = 0
        print(ar_list)
        for tup in ar_list:
            r = tup[1]
            a = tup[0]
            print(a)
            if r> best_r:
                best_action = a
                best_r = r
        
        return best_action
    
    
    def choose_action(self, state, test_mode = False, compare = False): #must be array with shape (1, self.observation_space)
        
        self.epsilon = max(self.min_epsilon, self.epsilon)
        
        if np.random.rand(1) < self.epsilon:
            action = self.env.action_space.sample()
            
        else:
            #action = self.choose_best_action(state)
            action = np.argmax(self.main_net.predict(state)[0])

        '''
        if test_mode == True:
            action = self.choose_best_action(state)
            print(action)
            
            
        if compare == True:
            action = np.argmax(self.main_net.predict(state)[0])
        '''
        return action
    
    
    def train(self):
        #print('training method')
        if len(self.replay_buffer) < self.batch_size:
            return
        
        loss_list = [i[5] for i in self.replay_buffer]
        loss_sum = sum(loss_list)
        p_list = np.nan_to_num([i/loss_sum for i in loss_list])
        self.p_list = p_list
        index_list = [i for i in range(len(p_list))]
        
        
        if sum(p_list) < 0.9: #NOT USING PRIORITY REPLAY
            sample_batch = random.sample(self.replay_buffer, self.batch_size)
        else:    
            chosen_indexes = [np.random.choice(index_list, p=p_list) for _ in range(self.batch_size)]
            sample_batch = [self.replay_buffer[i] for i in chosen_indexes]
        
        states = []
        new_states = []
        for sample in sample_batch:
            state, action, reward, new_state, done, loss = sample
            states.append(state)
            new_states.append(new_state)
            
        states = np.array(states)
        states = states.reshape(self.batch_size, 4)
        
        new_states = np.array(new_states)
        new_states = new_states.reshape(self.batch_size, 4)
        
        targets = self.main_net.predict(states) #predict Q(s,a) using main net
        next_targets = self.target_net.predict(new_states) #predict Q(s_prime, a) using target net
        
        index = 0
        for sample in sample_batch:
            state, action, reward, new_state, done, loss = sample
            target = targets[index]
            
            if done:
                target[action] = reward
            
            else:
                future_Q = max(next_targets[index])
                target[action] = reward + self.gamma * future_Q
                
            
           
            #targets[index] = target #DELETE THIS IF STOPS WORKING
            index += 1
        #print(target)
        #print(targets)
        self.main_net.fit(states, targets, verbose = 0)
      
    def calculate_loss(self, state):
        y_true = self.target_net.predict(state)
        y_pred = self.main_net.predict(state)
        loss = sum(sum(abs(y_true - y_pred)))
        return loss        
        
    def play_one(self, state, test_mode = False, compare = False):
        total_reward = 0
        done = False
        
        while not done:
            action = self.choose_action(state, test_mode = test_mode, compare = compare)
            loss = self.calculate_loss(state)
            new_state, reward, done, info = env.step(action)
            
            new_state = new_state.reshape(1, 4)
            
            
            #for mountain car
            '''
            if new_state[0][0] >= 0.5:
                reward += 10
                print('::: REWARD GRANTED - SUCESS :::')
                '''
            
            
            self.replay_buffer.append([state, action, reward, new_state, done, loss])
            
            
            total_reward += reward
            #self.train() #original
            state = new_state
        #for cartpole
        total_reward -=200
        
        self.train()
        self.network_sync_counter +=1
        
        if self.network_sync_counter >= self.SYNC_EVERY:
            self.target_net.set_weights(self.main_net.get_weights())
            self.network_sync_counter = 0
            
        
        self.epsilon -= self.epsilon_decay
        return total_reward
            

def plot_running_avg(total, compare = False):#Takes an array
    n = len(total)
    avg = np.array(np.empty(n))
    for t in range(n):
        avg[t] = total[max(0, t-100):t+1].mean()
    plt.plot(avg)
    if compare == True:
        plt.title('Compare of averages')
    else:
        plt.title('Average Rewards Against Episodes')
    plt.show()



if __name__ == '__main__':
    Episodes = 500
    env = gym.make('CartPole-v0')
    dqn = MountainCarDQN(env = env)
    reward_list = []
    for i in range(Episodes):
        state = env.reset().reshape(1, 4)
        '''
        if i % 50==0:
            print('Recording')
            env = gym.wrappers.Monitor(env, "./vid",video_callable=lambda episode_id: True, force=True)
            time.sleep(1)
            env.close()
            '''
        reward = dqn.play_one(state)
        reward_list.append(reward)
        print('\n Episode: ',i)
        print('average score:', np.mean(reward_list[-100:]))
    #plt.plot(reward_list)  
    plot_running_avg(np.array(reward_list))
    print('Finished Run: NO PRIORITY REPLAY')

    '''
    reward_list = []
    for i in range(50):
        state = env.reset().reshape(1, 4)
        reward = dqn.play_one(state, test_mode = True)
        reward_list.append(reward)
        print('\n Episode: ',i)
        print('average score:', np.mean(reward_list[-100:]))
    plt.plot(reward_list)  
    plot_running_avg(np.array(reward_list))
    
    reward_list = []
    for i in range(50):
        state = env.reset().reshape(1, 4)
        reward = dqn.play_one(state, compare = True)
        reward_list.append(reward)
        print('\n Episode: ',i)
        print('average score:', np.mean(reward_list[-100:]))
    plt.plot(reward_list)  
    plot_running_avg(np.array(reward_list), compare = True)
    env.close()
'''