import torch
import numpy as np
from ramanujan.math_ai.models.actor_critic import ActorCriticGCFNetwork
from ramanujan.math_ai.environments.AbstractRLEnvironment import AbstractRLEnvironment

class AlphaTensorMCTS:
    """
    Neural-Guided Monte Carlo Tree Search.
    Uses the Actor-Critic Policy network to predict the Upper Confidence Bound (UCB)
    for specific mathematical sub-spaces, avoiding blind combinatorial brute force.
    """
    def __init__(self, env: AbstractRLEnvironment, network: ActorCriticGCFNetwork, 
                 num_simulations=100, c_puct=1.5):
        self.env = env
        self.network = network
        self.num_simulations = num_simulations
        self.c_puct = c_puct
        
        # State evaluations cache
        self.Q = {}  # Q value (expected reward)
        self.N = {}  # Visit count
        self.P = {}  # Prior probabilities from network
        
    def _get_state_key(self, state):
        return tuple(np.round(state, 5))
        
    def search(self, initial_state):
        """
        Executes N rollouts from the current root state guided by the neural policy.
        Returns the most promising coefficient values.
        """
        best_actions = []
        for _ in range(self.num_simulations):
            self.env.reset() # Start from depth 0
            
            state = initial_state
            episode_actions = []
            
            # Walk down the tree until terminal depth
            for step in range(self.env.max_steps):
                state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                
                with torch.no_grad():
                    action_mean, action_std, value = self.network(state_t)
                
                # Sample continuous action from the normal distribution defined by the policy
                dist = torch.distributions.Normal(action_mean, action_std)
                action = dist.sample().squeeze(0).numpy()
                
                # Convert continuous action (proxy values) to actual a_n, b_n limits
                # (For polynomial domains, the action maps to scaling multipliers or bounds)
                # Keep track of traversed path
                s_key = self._get_state_key(state)
                if s_key not in self.P:
                    self.P[s_key] = 1.0  # Simplified prior for continuous domain
                    self.N[s_key] = 0
                    self.Q[s_key] = 0.0
                    
                # Execute environment step
                obs, reward, done, _ = self.env.step(action)
                episode_actions.append(action)
                
                # Backpropagate value
                self.N[s_key] += 1
                self.Q[s_key] += (reward - self.Q[s_key]) / self.N[s_key]
                
                state = obs
                if done:
                    # If this full trajectory yielded a very high reward, cache it
                    if reward > 50.0:  # arbitrary high digits matched threshold
                        best_actions.append((reward, episode_actions[0])) # store top-level action
                    break
                    
        # Return the highest value top-level actions found during the neural rollouts
        best_actions.sort(key=lambda x: x[0], reverse=True)
        # Return just the actions, stripped of rewards
        return [act[1] for act in best_actions]
