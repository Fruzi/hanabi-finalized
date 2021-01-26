"""Playable class used to play games with the server"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

import hanabi_learning_environment.agents.rainbow.run_mixed_experiment as xp
import hanabi_learning_environment.agents.rainbow.rainbow_agent as rainbow
from hanabi_learning_environment.agents.rainbow.third_party.dopamine import logger
import os
import numpy as np


class RainbowPlayer(object):

    def __init__(self, agent_config):
        tf.reset_default_graph()
        # project_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        # self.base_dir = project_path + '/evaluation/trained_models/'
        self.base_dir = agent_config['base_dir']
        self.observation_size = agent_config["observation_size"]
        self.num_players = agent_config["num_players"]
        self.num_actions = agent_config["max_moves"]

        self.experiment_logger = logger.Logger(self.base_dir + '/logs')

        self.agent = rainbow.RainbowAgent(
            observation_size=self.observation_size,
            num_actions=self.num_actions,
            num_players=self.num_players,
            # num_layers=1
        )
        path_weights = os.path.join(self.base_dir, 'checkpoints')
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
        action_dict = observation["legal_moves"][
            np.where(np.equal(action_int, observation["legal_moves_as_int"]))[0][0]]

        # return action_dict
        return action_int.item()
