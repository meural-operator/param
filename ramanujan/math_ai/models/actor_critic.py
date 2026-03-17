import torch
import torch.nn as nn
import torch.nn.functional as F

class ActorCriticGCFNetwork(nn.Module):
    """
    Neural Policy-Value network (AlphaZero style) for GCF convergence.
    Observes the numerical trajectory of the sequence [prev_q, prev_p, q, p] 
    and predicts the optimal continuous subspaces for the polynomial coefficients.
    """
    def __init__(self, state_dim=4, hidden_dim=128, action_dim=2):
        super(ActorCriticGCFNetwork, self).__init__()
        
        # Shared feature extractor
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        
        # Actor head: Outputs mean and log_std for continuous action distribution
        # Assuming action_dim = (a_n, b_n) continuous proxy values
        self.actor_mean = nn.Linear(hidden_dim, action_dim)
        self.actor_log_std = nn.Parameter(torch.zeros(1, action_dim))
        
        # Critic head: Predicts the expected convergence reward (0 to 100)
        self.critic = nn.Linear(hidden_dim, 1)
        
    def forward(self, state):
        """
        State: [prev_q, prev_p, q, p] scaled logarithmically to prevent float overflow.
        """
        # We assume the state is already log-scaled or normalized by the environment wrapper
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        
        # Policy (Actor)
        action_mean = self.actor_mean(x)
        action_log_std = self.actor_log_std.expand_as(action_mean)
        action_std = torch.exp(action_log_std)
        
        # Value (Critic) expected digits of precision
        value = self.critic(x)
        
        return action_mean, action_std, value
