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


class EvolvedB(RulebasedAgent):
    """Agent that applies a simple heuristic."""

    def __init__(self, config, *args, **kwargs):
        """Initialize the agent."""
        super().__init__()
        self.totalCalls = 0
        self.config = config
        # Extract max info tokens or set default to 8.
        self.max_information_tokens = config.get('information_tokens', 8)

        self.rules = [Ruleset.play_safe_card,
                      Ruleset.tell_playable_card_outer,
                      Ruleset.play_probably_safe_factory(0.6, True),
                      Ruleset.discard_probably_useless_factory(0.8),
                      Ruleset.discard_oldest_no_info,
                      Ruleset.discard_probably_useless_factory(0.4),
                      Ruleset.tell_most_information,
                      Ruleset.play_probably_safe_factory(0.2, True),
                      Ruleset.play_probably_safe_factory(0.25),
                      Ruleset.discard_least_likely_to_be_be_necessary]

    def act(self, observation):
        return self.get_move(observation)
