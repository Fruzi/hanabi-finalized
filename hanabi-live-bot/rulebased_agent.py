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


class RulebasedAgent:
    """Agent that applies a simple heuristic."""

    def __init__(self):
        self.totalCalls = 0
        self.previous_knowledge = None
        self.last_affected = []

    def get_move(self, observation):
        if observation['current_player_offset'] == 0:
            for index, rule in enumerate(self.rules):
                action = rule(observation)
                if action is not None:
                    print(index)
                    self.totalCalls += 1
                    return action
            # self.totalCalls += 1
            # return Ruleset.legal_random(observation)
        return observation['legal_moves'][0]

    def __str__(self):
        i = 0
        ret = ""
        for rule in self.rules:
            ret = ret + "{}. {}\n".format(i, str(rule))
            i = i + 1
        return ret

    def get_rules(self):
        return self.rules

    def set_rules(self, rules):
        self.rules = rules
