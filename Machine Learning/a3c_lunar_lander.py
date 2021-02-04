from keras import backend as K
from keras.layers import Dense, Input, Activation
from keras.models import Model
from keras.optimizers import Adam
import numpy as np
import gym
import matplotlib.pyplot as plt
import time
from tensorflow import keras

class Agent(object):
    def __init__(self, list_of_layers, alpha, beta, input_dims, n_actions):
        
        self.gamma = 0.99
        self.list_of_layers = list_of_layers
        self.alpha = alpha
        self.beta = beta
        self.input_dims = input_dims
        self.n_actions = n_actions
        
        
        self.layer1_size = list_of_layers[0]
        self.layer2_size = list_of_layers[1]
        
        if len(self.list_of_layers) == 3:
            self.layer3_size = list_of_layers[2]
            
        self.actor, self.critic, self.policy = self.build_network()
        self.action_space = [i for i in range(self.n_actions)]
        
        
    def build_network(self):
        
        input1 = Input(shape = (self.input_dims, ))
        delta = Input(shape = [1]) #for calculting loss
        dense_x = Dense(self.layer1_size, activation = 'relu')(input1)
        #dense1 = identity_block_dense(dense_x, [512, 512 ,1024], 2, 'middle1')
        dense2 = Dense(self.layer2_size, activation = 'relu')(dense_x)
        
        #Same layers used in both actor and critic
        if len(self.list_of_layers) == 3:
            dense3 = Dense(self.layer3_size, activation = 'relu')(dense2)
            probs = Dense(self.n_actions, activation = 'softmax')(dense3)
            values = Dense(1, activation =  'linear')(dense3)
        else:
            probs = Dense(self.n_actions, activation = 'softmax')(dense2)
            values = Dense(1, activation =  'linear')(dense2)
        
        def custom_loss(y_true, y_pred):
            out = K.clip(y_pred, 1e-8, 1-1e-8)
            log_lik = y_true*K.log(out)
            
            return K.sum(-log_lik*delta)
        
        loss_fn = keras.losses.SparseCategoricalCrossentropy()
        actor = Model(inputs = [input1,delta], outputs = [probs])
        actor.compile(optimizer = Adam(learning_rate = self.alpha), loss = 'categorical_crossentropy')
        
        critic = Model(inputs = [input1], outputs = [values])
        critic.compile(optimizer = Adam(learning_rate = self.beta), loss = 'mse')
        
        policy = Model(inputs = [input1], outputs = [probs])
        #We don't train the policy net
        return actor, critic, policy

    def choose_action(self, state):
        state = state.reshape(1, -1)
        #Using policy net to set probabilities of actions
        probabilities = self.policy.predict(state)[0] #[0] as returns a tuple
        
        action = np.random.choice(self.action_space, p = probabilities)
        
        return action
        

    def learn(self, state, action, reward, new_state, done):
        #Learns after each step, no memory. very sample inneficient.
        #Maybe try alter so can use a memory?
        state = state.reshape(1, -1)
        # or (batch_size, -1) or (batch_size, len(state_space))
        new_state = new_state.reshape(1, -1)
        
        critic_value_s = self.critic.predict(state)
        critic_value_new_s = self.critic.predict(new_state)
        
        if not done:
            target = reward + self.gamma*critic_value_new_s
        else:
            target = np.array([reward])
            #print('episode DONE')
            
        delta = target - critic_value_s
        
        #One-Hot Encoding Actions:
        actions = np.zeros([1, self.n_actions])
        actions[np.arange(1), action]= 1.0
        '''print('target type:', type(target))
        print('state shape', state.shape)
        print('target', target)
        print('state', state)'''
        self.actor.fit([state, delta], actions, verbose = 0)
        self.critic.fit(state, target, verbose = 0)
       
        
def plot_running_avg(total):#Takes an array
    n = len(total)
    avg = np.array(np.empty(n))
    for t in range(n):
        avg[t] = total[max(0, t-100):t+1].mean()
    plt.plot(avg)
    plt.title('Average Rewards Against Episodes')
    plt.show()

if __name__ == '__main__':
    env = gym.make('LunarLander-v2')
    input_dims = 8 #number o state variables
    n_actions = 4 #nuber of actions
    agent = Agent([1024, 512], alpha = 0.00001, beta = 0.00005, input_dims = input_dims, n_actions = n_actions)
    
    score_history = []
    episodes = 500
    
    for i in range(episodes):
        done = False
        score = 0
        if i % 50==0:
            print('Recording')
            #env = gym.wrappers.Monitor(env, "./vid-LunarLander", force=True)
            time.sleep(1)
            #env.close()
        observation = env.reset()

            
        while not done:
            action = agent.choose_action(observation)
            prev_obs = observation
            observation, reward, done, info = env.step(action)
            
            '''if int(round(observation[0])) == 0 and int(round(observation[1])) == 0:
                print('Episode Success!!!')'''
            
            agent.learn(prev_obs, action, reward, observation, done)
            
            score +=reward
            
        score_history.append(score)
        avg_score = np.mean(score_history[-100:])
        print('\n score for episode ', i, ' : ', score)
        print('Average score for last 100 episodes: ', avg_score)
        
    plot_running_avg(np.array(score_history))
    plt.plot(score_history)
    env.close()