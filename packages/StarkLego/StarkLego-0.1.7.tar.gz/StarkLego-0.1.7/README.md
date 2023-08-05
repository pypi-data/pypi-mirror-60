# StarkLego

## Introduction
Welcome to *StarkLego*! You can use this python library to access different environments to interact with your RL agents, or you can even
construct your own `.ldr` files using the built in tools that StarkLego provides.

## Setting up Development Environment 
The library was written in `Python 3.5.6`. When you install the library using `pip`, the library should already download 
all of the required libraries to run *StarkLego*. However, if this does not happen then you can download the following `pip` libraries manually:

| Library | Recommended Version |
|----|:----|
| tensorflow | 1.8.0 |
| gym | latest |
| numpy | 1.16 |
| pyldraw | 0.8.2 |

You can also run the following line in your command-line:<br/>
`pip install gym pyldraw==0.8.2 numpy==1.16.0 tensorflow==1.8.0`

__IMPORTANT:__ Create a `ldraw-license.txt` file in the directory wherever you are running your code from. This is necessary because in order to use the ldraw libraries you will need to include this.

## Lego Piece Support
So far, only the following Lego Pieces are supported:
- 2X2 Brick
Due to the lack of support for more than the *2X2 Brick*, there is no customization available.

## Constructing Your Own LDR Files
You might want to use this library to construct your own LDR files which contain different parts. 
The following is an example of how to use the *StarkLego* package to create a Lego World.

```python
from StarkLego.lego_builders.service.builder import LegoWorld
from StarkLego.lego_builders.service.builder import TwoXTwoBlock

my_lego_world = LegoWorld(6,12,6)

my_lego_world.add_part_to_world(part=TwoXTwoBlock(), x=0, z=0)
my_lego_world.add_part_to_world(TwoXTwoBlock(), 2, 2)
my_lego_world.add_part_to_world(TwoXTwoBlock(), 2, 2)

print(my_lego_world.ldraw_content)
# Expected output 
#1 272 0.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 1.000000 3003.DAT
#1 272 40.000000 0.000000 40.000000 1.000000 0.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 1.000000 3003.DAT
#1 272 40.000000 -24.000000 40.000000 1.000000 0.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 1.000000 3003.DAT

```
## Using Environments For Training Agents

These environments cater to the agents available in the `stable_baselines` RL library. 
You can get `stable_baselines` by running the following in your command-line: <br/>
`pip install stable-baselines==2.9.0`

### How to run
If you wish to run one of these environments, please feel free using the code below:

```python
from StarkLego.environments.env_low_height import LegoEnv
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
import numpy as np


env = DummyVecEnv([lambda: LegoEnv(4, 14, 4, 4)])

model = PPO2(MlpPolicy, env, verbose=1, learning_rate=0.0001, gamma=1)
model.learn(total_timesteps=3)
obs = env.reset()

print("Done training")

for i in range(4):
    action, _states = model.predict(obs, deterministic=True)   #determinstic is `False` by default
    obs, rewards, done, info = env.step(action)
    env.render()
    if done:
        print(info[0].get("ldrContent"))   #print the state through `info` due to environment resetting

```
### List of Supported Environments
### env_low_height
The goal is to minimize the height of the Lego build. 

| Space | Data Type |
|----|:----|
| action_space | spaces.Box |
| observation_space | spaces.Box |


The only specifications than can be made are the dimensions of the LEGO World, and the number of pieces per build iteration.
#### Constructor:`LegoEnv(x, y, z, noLegoPieces)`
- x: the maximum `x` dimenstion of the Lego World
- y: the maximum `y` dimenstion of the Lego World
- z: the maximum `z` dimenstion of the Lego World
- noLegoPieces: The number of Lego pieces to be inserted into the Lego World

This environment does not allow any customization for which
lego pieces can be used. 


