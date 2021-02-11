"""Playable class used to play games with the server"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

import run_experiment as xp
import rainbow_agent as rainbow
import logger
import os
import numpy as np


class RainbowPlayer(object):

    def __init__(self, agent_config):
        self.base_dir = agent_config['base_dir']
        self.observation_size = agent_config["observation_size"]
        self.num_players = agent_config["num_players"]
        self.num_actions = agent_config["max_moves"]
        self.experiment_logger = logger.Logger(self.base_dir + '/logs')

        self.agent = rainbow.RainbowAgent(
            observation_size=self.observation_size,
            num_actions=self.num_actions,
            num_players=self.num_players,
        )
        path_weights = os.path.join(self.base_dir, 'checkpoints')
        print("\n\n\n\n\n {} \n\n\n\n\n".format(path_weights))
        start_iteration, experiment_checkpointer = xp.initialize_checkpointing(self.agent, self.experiment_logger,
                                                                               path_weights, "ckpt")
        self.agent.eval_mode = False
        self.played = False

        print("\n---------------------------------------------------")
        print("Initialized Model weights at start iteration: {}".format(start_iteration))
        print("---------------------------------------------------\n")

    def act(self, observation):
        # Returns Integer Action
        action_int = self.agent._select_action(observation["vectorized"], observation["legal_moves_as_int"])
        # Decode it back to dictionary object
        # action_dict = observation["legal_moves"][
        #     np.where(np.equal(action_int, observation["legal_moves_as_int"]))[0][0]]
        # print(f"Action int {action_int}")
        # print(f"rainbow about to translate move int, legal moves are {observation['legal_moves']}")
        for move in observation['legal_moves']:
            if move['move_int'] == action_int:
                # print(f"action decoded to {move}")
                return move

        # return action_dict
        # return action_int.item()
