# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Environments/00_EnvBase.ipynb.

# %% auto 0
__all__ = ['ebase']

# %% ../../nbs/Environments/00_EnvBase.ipynb 4
from fastcore.utils import *
import numpy as np

# %% ../../nbs/Environments/00_EnvBase.ipynb 5
class ebase(object):
    """Base environment. All environments should inherit from this one."""
    
    def __init__(self):
               
        self.T = self.TransitionTensor()
        self.F = np.array(self.FinalStates())
        self.R = self.RewardTensor()
        self.O = self.ObservationTensor()
                
        self.Aset = self.actions()
        self.Sset = self.states() 
        self.Oset = self.observations()

        # CHECKS
        R, T, O = self.R, self.T, self.O
        
        # number of agents
        N = R.shape[0]  
        assert O.shape[0] == N, "Inconsistent number of agents"
        assert len(T.shape[1:-1]) == N, "Inconsistent number of agents"
        assert len(R.shape[2:-1]) == N, "Inconsistent number of agents"
        
        # number of actions for each agent        
        M = T.shape[1] 
        assert np.allclose(T.shape[1:-1], M), 'Inconsistent number of actions'
        assert np.allclose(R.shape[2:-1], M), 'Inconsistent number of actions'
        assert np.all(list(map(len, self.Aset)) == np.array(M).repeat(N)),\
            'Inconsistent number of actions'
            
        # number of states
        Z = T.shape[0] 
        assert T.shape[-1] == Z, 'Inconsistent number of states'
        assert R.shape[-1] == Z, 'Inconsistent number of states'
        assert R.shape[1] == Z, 'Inconsistent number of states'
        assert O.shape[1] == Z, 'Inconsistent number of states'
        assert len(self.F) == Z, 'Inconsistent number of states'
        assert len(self.Sset) == Z, 'Inconsistent number of states'

        # number of observations
        Q = O.shape[-1]
        assert np.all(list(map(len, self.Oset)) == np.array(Q).repeat(N)),\
            'Inconsistent number of observations'
        
        assert np.allclose(T.sum(-1), 1), 'Transition model wrong'
        assert np.allclose(O.sum(-1), 1), 'Observation model wrong'


# %% ../../nbs/Environments/00_EnvBase.ipynb 9
@patch
def TransitionTensor(self:ebase):
    raise NotImplementedError

# %% ../../nbs/Environments/00_EnvBase.ipynb 13
@patch
def RewardTensor(self:ebase):
    raise NotImplementedError

# %% ../../nbs/Environments/00_EnvBase.ipynb 18
@patch
def ObservationTensor(self:ebase):
    """Default observation tensor: perfect observation"""
    self.defaultObsTensUsed = True
    self.Q = self.Z
    Oiso = np.ones((self.N, self.Z, self.Q))
    for i in range(self.N):
        Oiso[i, :, :] = np.eye(self.Q)
    return Oiso

# %% ../../nbs/Environments/00_EnvBase.ipynb 21
@patch
def FinalStates(self:ebase):
    """Default final states: no final states"""
    return np.zeros(self.Z, dtype=int)

# %% ../../nbs/Environments/00_EnvBase.ipynb 26
@patch
def actions(self:ebase):
    """Default action set representations `act_im`."""
    return [[str(a) for a in range(self.M)] for _ in range(self.N)]

# %% ../../nbs/Environments/00_EnvBase.ipynb 28
@patch
def states(self:ebase):
    """Default state set representation `state_s`."""
    return [str(s) for s in range(self.Z)]

# %% ../../nbs/Environments/00_EnvBase.ipynb 30
@patch
def observations(self:ebase):
    """Default observation set representations `obs_io`."""
    if hasattr(self, 'defaultObsTensUsed'):
        return [[str(o) for o in self.states()] for _ in range(self.N)]
    else:
        return [[str(o) for o in range(self.Q)] for _ in range(self.N)]


# %% ../../nbs/Environments/00_EnvBase.ipynb 32
@patch
def id(self:ebase):
    """
    Returns id string of environment
    """
    # Default
    id = f"{self.__class__.__name__}"
    return id

@patch
def __str__(self:ebase): return self.id()

@patch
def __repr__(self:ebase): return self.id()

# %% ../../nbs/Environments/00_EnvBase.ipynb 34
@patch
def step(self:ebase, 
         jA:Iterable # joint actions
        ) -> tuple:  # (observations_i, rewards_i, done, info)
    """
    Iterate the environment one step forward.
    """
    # choose a next state according to transition tensor T
    tps = self.T[tuple([self.state]+list(jA))].astype(float)
    next_state = np.random.choice(range(len(tps)), p=tps)

    # obtain the current rewards
    rewards = self.R[tuple([slice(self.N),self.state]+list(jA)
                           +[next_state])]

    # advance the state and collect info
    self.state = next_state
    obs = self.observation()     

    # if state is a final state the episode is done
    done = self.state in np.where(self.F==1)[0]

    # report the true state in the info dict
    info = {'state': self.state}

    return obs, rewards.astype(float), done, info

# %% ../../nbs/Environments/00_EnvBase.ipynb 35
@patch
def observation(self:ebase
               ) -> np.ndarray:  # observations_i
    """
    Possibly random observation for each agent from the current state.
    """
    OBS = np.zeros(self.N, dtype=int)
    for i in range(self.N):
        ops = self.O[i, self.state]
        obs = np.random.choice(range(len(ops)), p=ops)
        OBS[i] = obs
    return OBS
