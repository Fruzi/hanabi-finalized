# coding=utf-8
# Copyright 2018 The Dopamine Authors and Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#
# This file is a fork of the original Dopamine code incorporating changes for
# the multiplayer setting and the Hanabi Learning Environment.
#
"""The entry point for running a Rainbow agent on Hanabi."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags

from third_party.dopamine import logger

from hanabi_learning_environment.agents.evolved_b import EvolvedB
from hanabi_learning_environment.agents.evolved_c import EvolvedC
from hanabi_learning_environment.agents.evolved_d import EvolvedD

import run_mixed_experiment

COLOR_CHAR = ["R", "Y", "G", "W", "B"]
FLAGS = flags.FLAGS
# checkpoint_counter = 0

flags.DEFINE_multi_string(
    'gin_files', [],
    'List of paths to gin configuration files (e.g.'
    '"configs/hanabi_rainbow.gin").')
flags.DEFINE_multi_string(
    'gin_bindings', [],
    'Gin bindings to override the values set in the config files '
    '(e.g. "DQNAgent.epsilon_train=0.1").')

flags.DEFINE_string('base_dir', None,
                    'Base directory to host all required sub-directories.')

flags.DEFINE_string('checkpoint_dir', '',
                    'Directory where checkpoint files should be saved. If '
                    'empty, no checkpoints will be saved.')
flags.DEFINE_string('checkpoint_file_prefix', 'ckpt',
                    'Prefix to use for the checkpoint files.')
flags.DEFINE_string('logging_dir', '',
                    'Directory where experiment data will be saved. If empty '
                    'no checkpoints will be saved.')
flags.DEFINE_string('logging_file_prefix', 'log',
                    'Prefix to use for the log files.')
flags.DEFINE_string('partner', 'evolved_b',
                    'Initial partner to be adapted', short_name='p')
flags.DEFINE_integer('sp_ratio', 2, 'The ration between self-play and mixed-play', short_name='r')
flags.DEFINE_integer('priming_iters', 3000, 'Number of iterations played in self-play when starting training')
flags.DEFINE_integer('mixed_iters', 5000,
                     'Number of iterations played both in self-play and mixed-play after priming step')
flags.DEFINE_integer('priming_type', -1, '-1 for self-play only, 0 for mixed-play only')
flags.DEFINE_boolean('use_partner_data', False, 'Whether the agent should use that states and actions created by the '
                                                'rule-based partner in his training')

partners = {'evolved_b': EvolvedB, 'evolved_c': EvolvedC, 'evolved_d': EvolvedD}


def launch_experiment():
    """Launches the experiment.

    Specifically:
    - Load the gin configs and bindings.
    - Initialize the Logger object.
    - Initialize the environment.
    - Initialize the observation stacker.
    - Initialize the agent.
    - Reload from the latest checkpoint, if available, and initialize the
      Checkpointer object.
    - Run the experiment.
    """
    # -------------------- Setup -----------------------
    if FLAGS.base_dir == None:
        raise ValueError('--base_dir is None: please provide a path for '
                         'logs and checkpoints.')
    run_mixed_experiment.load_gin_configs(FLAGS.gin_files, FLAGS.gin_bindings)
    experiment_logger = logger.Logger('{}/logs'.format(FLAGS.base_dir))
    environment = run_mixed_experiment.create_environment()
    obs_stacker = run_mixed_experiment.create_obs_stacker(environment)
    agent = run_mixed_experiment.create_agent(environment, obs_stacker)
    checkpoint_dir = '{}/checkpoints'.format(FLAGS.base_dir)
    start_iteration, experiment_checkpointer = run_mixed_experiment.initialize_checkpointing(agent,
                                                                                             experiment_logger,
                                                                                             checkpoint_dir,
                                                                                             FLAGS.checkpoint_file_prefix)
    # ------------- Parameters ------------------------
    num_steps = 10000
    priming_iterations = FLAGS.priming_iters
    mixed_iterations = FLAGS.mixed_iters
    finale_iterations = 10000 - (priming_iterations + mixed_iterations)
    learner = partners[FLAGS.partner]({'players': 2})
    # ------------------- Runs of the algorithm -----------------
    if start_iteration < priming_iterations:
        agent = run_mixed_experiment.run_mixed_experiment(agent, environment,
                                                          start_iteration, obs_stacker,
                                                          experiment_logger,
                                                          experiment_checkpointer, checkpoint_dir, learner,
                                                          priming_iterations,
                                                          num_steps,
                                                          checkpoint_every_n=100,
                                                          self_train_ratio=FLAGS.priming_type)
        start_iteration = priming_iterations
    if priming_iterations <= start_iteration < priming_iterations + mixed_iterations:
        agent = run_mixed_experiment.run_mixed_experiment(agent, environment,
                                                          start_iteration, obs_stacker,
                                                          experiment_logger,
                                                          experiment_checkpointer, checkpoint_dir, learner,
                                                          priming_iterations + mixed_iterations,
                                                          num_steps,
                                                          checkpoint_every_n=100,
                                                          self_train_ratio=FLAGS.sp_ratio,
                                                          view_partner_tuples=FLAGS.use_partner_data)
        start_iteration = priming_iterations + mixed_iterations
    if priming_iterations + mixed_iterations <= start_iteration:
        run_mixed_experiment.run_mixed_experiment(agent, environment,
                                                  start_iteration, obs_stacker,
                                                  experiment_logger,
                                                  experiment_checkpointer, checkpoint_dir, learner,
                                                  10000,
                                                  num_steps,
                                                  checkpoint_every_n=100,
                                                  self_train_ratio=-1)


def main(unused_argv):
    """This main function acts as a wrapper around a gin-configurable experiment.

    Args:
      unused_argv: Arguments (unused).
    """
    launch_experiment()


if __name__ == '__main__':
    app.run(main)
