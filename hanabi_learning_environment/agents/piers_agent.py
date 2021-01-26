# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Simple Agent."""

from hanabi_learning_environment.agents.rulebased_agent import RulebasedAgent
from hanabi_learning_environment.agents.ruleset import Ruleset


class PiersAgent(RulebasedAgent):
    """Agent that applies a simple heuristic."""

    def __init__(self, config, *args, **kwargs):
        """Initialize the agent."""
        self.totalCalls = 0
        self.config = config
        # Extract max info tokens or set default to 8.
        self.max_information_tokens = config.get('information_tokens', 8)

        # self.rules = [Ruleset.play_safe_card,Ruleset.tell_playable_card_outer,Ruleset.discard_randomly,Ruleset.legal_random]
        self.rules = [Ruleset.hail_mary,
                      Ruleset.play_safe_card,
                      Ruleset.play_probably_safe_factory(0.6, True),
                      Ruleset.tell_anyone_useful_card,
                      Ruleset.tell_dispensable_factory(3),
                      Ruleset.osawa_discard,
                      Ruleset.discard_oldest_first,
                      Ruleset.tell_most_information]

    def act(self, observation):
        return self.get_move(observation)
