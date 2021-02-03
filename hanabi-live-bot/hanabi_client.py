# Imports (standard library)
import json

# Imports (3rd-party)
import os

import websocket

# Imports (local application)
from constants import ACTION
from game_state import GameState
from constants import MAX_CLUE_NUM
import constants
from hanabi_learning_environment.agents.evolved_b import EvolvedB
from rainbow_gui import RainbowPlayer
import numpy as np
from vectorizer import ObservationVectorizer
import json_to_pyhanabi

AGENTS = {'evolved_b': EvolvedB, 'rules': EvolvedB, 'regular_rainbow': RainbowPlayer, 'changed_rainbow': RainbowPlayer,
          'rb': RainbowPlayer, '3_phase_with_rules': RainbowPlayer, '3_phase': RainbowPlayer,
          '3_phase_with_rules+': RainbowPlayer, '3_phase+': RainbowPlayer, 'manager': None, 'blank': RainbowPlayer,
          '2-phase2': RainbowPlayer, '2-phase3': RainbowPlayer}


class HanabiClient:
    def __init__(self, url, cookie, agent_type):
        # Initialize all class variables
        self.commandHandlers = {}
        self.tables = {}
        self.users = {}
        self.username = ""
        self.ws = None
        self.games = {}

        # Initialize the website command handlers (for the lobby)
        self.commandHandlers["welcome"] = self.welcome
        self.commandHandlers["warning"] = self.warning
        self.commandHandlers["error"] = self.error
        self.commandHandlers["chat"] = self.chat
        self.commandHandlers["table"] = self.table
        self.commandHandlers["tableList"] = self.table_list
        self.commandHandlers["tableGone"] = self.table_gone
        self.commandHandlers["tableStart"] = self.table_start
        self.commandHandlers['userList'] = self.user_list
        self.commandHandlers['user'] = self.user
        self.commandHandlers['userGone'] = self.user_gone

        # Initialize the website command handlers (for the game)
        self.commandHandlers["init"] = self.init
        self.commandHandlers["gameAction"] = self.game_action
        self.commandHandlers["gameActionList"] = self.game_action_list
        self.commandHandlers["databaseID"] = self.database_id
        self.commandHandlers['connected'] = self.connected
        self.commandHandlers['finishOngoingGame'] = self.finish_ongoing_game
        self.played = False
        self.all_connected = False
        self.need_to_make_first_play = False
        self.data_for_first_action = None
        self.agent_type = agent_type
        self.is_manager = False
        if agent_type == 'evolved_b' or agent_type == 'rules':
            self.rule_based_agent = True
        else:
            self.rule_based_agent = False
        self.agent = None
        # Moved initialization to here so the bot is ready to play faster
        if self.rule_based_agent:
            self.agent = AGENTS[self.agent_type]({'players': 2})
        elif agent_type == 'manager':
            self.agent = None
            self.is_manager = True
        else:
            if 'regular' in self.agent_type or 'rb' in self.agent_type:
                base_dir = os.path.abspath('saved_agents/baseline')
            elif 'changed' in self.agent_type:
                base_dir = os.path.abspath('saved_agents/changed')
            elif '3_phase_with_rules' == self.agent_type:
                base_dir = os.path.abspath('saved_agents/3_phase_with_rules')
            elif '3_phase' == self.agent_type:
                base_dir = os.path.abspath('saved_agents/3_phase')
            elif '3_phase_with_rules+' == self.agent_type:
                base_dir = os.path.abspath('saved_agents/3_phase_with_rules+')
            elif '3_phase+' == self.agent_type:
                base_dir = os.path.abspath('saved_agents/3_phase+')
            elif 'blank' == self.agent_type:
                base_dir = os.path.abspath('saved_agents/blank')
            elif '2-phase2' == self.agent_type:
                base_dir = os.path.abspath('saved_agents/2_phase_short_2')
            elif '2-phase3' == self.agent_type:
                base_dir = os.path.abspath('saved_agents/2_phase_short_3')
            agent_config = {'observation_size': 658, 'num_players': 2,
                            'max_moves': 20,
                            'base_dir': base_dir}
            self.agent = AGENTS[self.agent_type](agent_config)

        # Start the WebSocket client
        print('Connecting to "' + url + '".')

        self.ws = websocket.WebSocketApp(
            url,
            on_message=lambda ws, message: self.websocket_message(ws, message),
            on_error=lambda ws, error: self.websocket_error(ws, error),
            on_open=lambda ws: self.websocket_open(ws),
            on_close=lambda ws: self.websocket_close(ws),
            cookie=cookie,
        )
        self.ws.run_forever()

    # ------------------
    # WebSocket Handlers
    # ------------------

    def websocket_message(self, ws, message):
        # WebSocket messages from the server come in the format of:
        # commandName {"field_name":"value"}
        # For more information, see:
        # https://github.com/Zamiell/hanabi-live/blob/master/src/websocketMessage.go
        result = message.split(" ", 1)  # Split it into two things
        if len(result) != 1 and len(result) != 2:
            print("error: received an invalid WebSocket message:")
            print(message)
            return

        command = result[0]
        try:
            data = json.loads(result[1])
        except:
            print(
                'error: the JSON data for the command of "' + command + '" was invalid'
            )
            return

        if command in self.commandHandlers:
            print('debug: got command "' + command + '"')
            try:
                self.commandHandlers[command](data)
            except Exception as e:
                print('error: command handler for "' + command + '" failed:', e)
                return
        else:
            print('debug: ignoring command "' + command + '"')

    def websocket_error(self, ws, error):
        print("Encountered a WebSocket error:", error)

    def websocket_close(self, ws):
        print("WebSocket connection closed.")

    def websocket_open(self, ws):
        print("Successfully established WebSocket connection.")

    # --------------------------------
    # Website Command Handlers (Lobby)
    # --------------------------------

    def welcome(self, data):
        # The "welcome" message is the first message that the server sends us
        # once we have established a connection
        # It contains our username, settings, and so forth
        self.username = data["username"]

    def error(self, data):
        # Either we have done something wrong,
        # or something has gone wrong on the server
        print(data)

    def warning(self, data):
        # We have done something wrong
        print(data)

    def chat(self, data):
        # We only care about private messages
        if data["recipient"] != self.username:
            return

        # We only care about private messages that start with a forward slash
        if not data["msg"].startswith("/"):
            return
        data["msg"] = data["msg"][1:]  # Remove the slash

        # We want to split it into two things
        result = data["msg"].split(" ", 1)
        command = result[0]

        if command == "join":
            self.chat_join(data)
        elif command == "start":
            self.chat_start()
        elif command == 'create':
            self.chat_create(data)
        elif command == 'terminate':
            self.chat_terminate(data)
        else:
            msg = "That is not a valid command."
            self.chat_reply(msg, data["who"])

    def chat_join(self, data):
        # Someone sent a private message to the bot and requested that we join
        # their game
        if self.is_manager:
            # msg = "The manager can't join games"
            # self.chat_reply(msg, data["who"])
            for user in self.users.values():
                reg_length = len("bot_manager")
                if len(self.username) > reg_length:
                    preamble = 'bot_' + self.username[reg_length:]
                else:
                    preamble = 'bot_'
                if preamble in user['name'] and user['name'] != 'bot_manager':
                    if user['tableID'] == 0:
                        msg = f'/join {data["who"]}'
                        self.chat_reply(msg, user["name"])
                        return
            msg = "All AI players are currently engaged in active games. Please wait a few minutes and try again"
            self.chat_reply(msg, data['who'])
            return
        # Find the person the bot manager has told us to join
        data["msg"] = data["msg"][1:]  # Remove the slash
        parsed = data["msg"].split(" ", 1)
        if len(parsed) > 1:
            person_to_join = parsed[1]
        else:
            msg = "You can't send join requests directly to AI players, bot_manager handles that"
            self.chat_reply(msg, data['who'])
            return
            # person_to_join = data['who']
        # Find the table that the current user is currently in
        table_id = None
        for table in self.tables.values():
            # Ignore games that have already started (and shared replays)
            if table["running"]:
                continue
            # if data["who"] in table["players"]:
            if person_to_join in table["players"]:
                if len(table["players"]) == 6:
                    msg = "Your game is full. Please make room for me before requesting that I join your game."
                    self.chat_reply(msg, data["who"])
                    return

                table_id = table["id"]
                break

        if table_id is None:
            msg = "Please create a table first before requesting that I join your game."
            self.chat_reply(msg, data["who"])
            return

        self.send(
            "tableJoin",
            {
                "tableID": table_id,
            },
        )

    def chat_start(self):
        for table in self.tables.values():
            if self.username in table['players']:
                self.send(
                    "tableStart",
                    {
                        'tableID': table['id']
                    }
                )
                break

    def chat_create(self, data):
        data["msg"] = data["msg"][1:]  # Remove the slash
        parsed = data["msg"].split(" ", 1)
        if len(parsed) > 1:
            name = parsed[1:]
            name = ' '.join(name)
        else:
            name = 'Bots Only Game'
        self.send(
            "tableCreate",
            {
                'name': name,
                'options': {'variantName': "No Variant", 'timed': False, 'timePerTurn': 20, 'timeBase': 120,
                            'speedRun': False, 'oneLessCard': False, 'oneExtraCard': False, 'emptyClause': False,
                            'detrimentalCharacters': False, 'deckPlays': False, 'cardCycle': False,
                            'allOrNothing': False},
                'password': ""
            }
        )

    def chat_terminate(self, data):
        tableID = -1
        for table in self.tables.values():
            if self.username in table['players']:
                tableID = table['id']
        if tableID == -1:
            self.chat_reply("Couldn't find an ongoing game to terminate.", data['who'])
        self.send(
            "tableTerminate",
            {
                'tableID': tableID
            }
        )

    def table(self, data):
        self.tables[data["id"]] = data

    def table_list(self, data_list):
        for data in data_list:
            self.table(data)

    def table_gone(self, data):
        del self.tables[data["tableID"]]

    def user(self, data):
        self.users[data['userID']] = data

    def user_list(self, data_list):
        for data in data_list:
            self.user(data)

    def user_gone(self, data):
        del self.users[data['userID']]

    def table_start(self, data):
        # The server has told us that a game that we are in is starting
        # So, the next step is to request some high-level information about the
        # game (e.g. number of players)
        # The server will respond with an "init" command
        self.send(
            "getGameInfo1",
            {
                "tableID": data["tableID"],
            },
        )

    # -------------------------------
    # Website Command Handlers (Game)
    # -------------------------------

    def init(self, data):
        # At the beginning of the game, the server sends us some high-level
        # data about the game, including the names and ordering of the players
        # at the table
        # Make a new game state and store it on the "games" dictionary
        state = GameState()
        self.played = False
        self.games[data["tableID"]] = state
        state.current_player = data['options']['startingPlayer']
        state.player_names = data["playerNames"]
        state.last_moves = []
        state.our_player_index = data["ourPlayerIndex"]
        state.num_players = len(state.player_names)
        state.hand_size = 4 if state.num_players > 3 else 5
        state.max_moves = 2 * state.hand_size + (state.num_players - 1) * constants.NUM_COLORS + (
                state.num_players - 1) * constants.NUM_RANKS
        # Initialize the hands for each player (an array of cards)
        for _ in range(len(state.player_names)):
            state.observed_hands.append([])
            state.card_knowledge.append([])
            state.cards_plausible.append([])
        self.all_connected = False
        self.need_to_make_first_play = False
        self.data_for_first_action = None
        # Initialize the play stacks
        """
        This is hard coded to 5 because there 5 suits in a no variant game
        The website supports variants that have 3, 4, and 6 suits
        TODO This code should compare "data['variant']" to the "variants.json"
        file in order to determine the correct amount of suits
        https://raw.githubusercontent.com/Zamiell/hanabi-live/master/public/js/src/data/variants.json
        """
        state.fireworks = {'R': 0, 'Y': 0, 'G': 0, 'B': 0, 'W': 0}
        # At this point, the JavaScript client would have enough information to
        # load and display the game UI; for our purposes, we do not need to
        # load a UI, so we can just jump directly to the next step
        # Now, we request the specific actions that have taken place thus far
        # in the game (which will come in a "gameActionList")
        self.send(
            "getGameInfo2",
            {
                "tableID": data["tableID"],
            },
        )

    def game_action(self, data):
        # Local variables
        state = self.games[data["tableID"]]

        # We just received a new action for an ongoing game
        self.handle_action(data["action"], data["tableID"])
        add_to_last_moves(state, data['action'])
        if state.current_player == state.our_player_index and not self.played:
            self.decide_action(data["tableID"])
            self.played = True

    def game_action_list(self, data):
        # Local variables
        state = self.games[data["tableID"]]

        # We just received a list of all of the actions that have occurred thus
        # far in the game
        for action in data["list"]:
            self.handle_action(action, data["tableID"])
            add_to_last_moves(state, action)

        # Let the server know that we have finished "loading the UI"
        # (so that our name does not appear as red / disconnected)
        self.send(
            "loaded",
            {
                "tableID": data["tableID"],
            },
        )
        if state.current_player == state.our_player_index and not self.played:
            if self.all_connected:
                self.decide_action(data["tableID"])
                self.played = True
            else:
                self.need_to_make_first_play = True
                self.data_for_first_action = data["tableID"]

    def connected(self, data):
        connected_players = data['list']
        self.all_connected = True
        for player in connected_players:
            if not player:
                self.all_connected = False
        if self.all_connected and self.need_to_make_first_play:
            self.decide_action(data["tableID"])
            self.played = True

    def finish_ongoing_game(self, data):
        self.send(
            "tableUnattend",
            {"tableID": data['tableID']}
        )

    def handle_action(self, data, table_id):
        print(
            'debug: got a game action of "%s" for table %d' % (data["type"], table_id)
        )

        # Local variables
        state = self.games[table_id]
        state.gained_info = False
        state.gained_score = False
        if data["type"] == "draw":
            # Add the newly drawn card to the player's hand
            hand = state.observed_hands[data["playerIndex"]]
            hand.append(
                {
                    "order": data["order"],
                    "suit_index": server_suit_index_to_real_index(data["suitIndex"]),
                    "rank": data["rank"] - 1,
                    "color": suit_index_to_color(server_suit_index_to_real_index(data['suitIndex']))
                }
            )
            knowledge = state.card_knowledge[data["playerIndex"]]
            knowledge.append(
                {
                    "order": data['order'],
                    'rank': None,
                    'color': None
                }
            )
            plausibles = state.cards_plausible[data['playerIndex']]
            plausibles.append(
                {
                    "rank": [0, 1, 2, 3, 4],
                    "color": [0, 1, 2, 3, 4],
                    "explicit_color": None,
                    "explicit_rank": None
                }
            )
            state.deck_size -= 1

        elif data["type"] == "play":
            player_index = data["playerIndex"]
            order = data["order"]
            card = remove_card_from_hand(state, player_index, order)
            if card is not None:
                if data['rank'] == 5 and state.information_tokens < MAX_CLUE_NUM:
                    state.information_tokens += 1
                    state.gained_info = True
                state.fireworks[suit_index_to_color(server_suit_index_to_real_index(data['suitIndex']))] += 1
                state.gained_score = True


        elif data["type"] == "discard":
            player_index = data["playerIndex"]
            order = data["order"]
            card = remove_card_from_hand(state, player_index, order)
            if card is not None:
                state.discard_pile.append(
                    {'color': suit_index_to_color(server_suit_index_to_real_index(data['suitIndex'])),
                     'rank': data['rank'] - 1})

            # Discarding adds a clue
            # But misplays are represented as discards,
            # and misplays do not grant a clue
            if not data["failed"]:
                state.information_tokens += 1
                state.gained_info = True
            else:
                state.life_tokens -= 1

        elif data["type"] == "clue":
            # Each clue costs one clue token
            state.information_tokens -= 1
            clue = data['clue']
            player_index = data["target"]
            affected_orders = data['list']
            for i, card in enumerate(state.observed_hands[player_index]):
                if card['order'] in affected_orders:
                    # rank clue
                    if clue['type'] == 1:
                        state.card_knowledge[player_index][i]['rank'] = clue['value'] - 1
                        state.cards_plausible[player_index][i]['rank'] = [clue['value'] - 1]
                        state.cards_plausible[player_index][i]['explicit_rank'] = clue['value'] - 1
                    else:
                        state.card_knowledge[player_index][i]['color'] = server_suit_index_to_real_index(clue['value'])
                        state.cards_plausible[player_index][i]['color'] = [
                            server_suit_index_to_real_index(clue['value'])]
                        state.cards_plausible[player_index][i]['explicit_color'] = server_suit_index_to_real_index(
                            clue['value'])
                else:
                    if clue['type'] == 1:
                        if clue['value'] - 1 in state.cards_plausible[player_index][i]['rank']:
                            state.cards_plausible[player_index][i]['rank'].remove(clue['value'] - 1)
                    else:
                        if server_suit_index_to_real_index(clue['value']) in state.cards_plausible[player_index][i][
                            'color']:
                            state.cards_plausible[player_index][i]['color'].remove(
                                server_suit_index_to_real_index(clue['value']))

        elif data["type"] == "turn":
            # A turn is comprised of one or more game actions
            # (e.g. play + draw)
            # The turn action will be the final thing sent on a turn,
            # which also includes the index of the new current player
            # TODO: this action may be removed from the server in the future
            # since the client is expected to calculate the turn on its own
            # from the actions
            state.turn = data["num"]
            state.current_player = data["currentPlayerIndex"]
            if state.current_player == state.our_player_index:
                self.played = False

    def database_id(self, data):
        # Games are transformed into shared replays after they are completed
        # The server sends a "databaseID" message when the game has ended
        # Use this as a signal to leave the shared replay
        self.send(
            "tableUnattend",
            {
                "tableID": data["tableID"],
            },
        )

        # Delete the game state for the game to free up memory
        del self.games[data["tableID"]]

    # ------------
    # AI functions
    # ------------

    def decide_action(self, table_id):
        # Local variables
        state = self.games[table_id]
        if self.rule_based_agent:
            d = state_to_dictionary(state)
            action = self.agent.act(d)
        else:
            rainbow_obs = state_to_rainbow_obs(state)
            action = self.agent.act(rainbow_obs)
        server_action = self.agent_action_to_server_action(action, table_id)
        self.send(
            "action", server_action
        )

    # -----------
    # Subroutines
    # -----------

    def chat_reply(self, message, recipient):
        self.send(
            "chatPM",
            {
                "msg": message,
                "recipient": recipient,
                "room": "lobby",
            },
        )

    def send(self, command, data):
        if not isinstance(data, dict):
            data = {}
        self.ws.send(command + " " + json.dumps(data))
        print('debug: sent command "' + command + '"')

    def agent_action_to_server_action(self, action, table_id):
        state = self.games[table_id]
        action_type = action['action_type']
        if action_type == 'PLAY':
            ret = {
                "tableID": table_id,
                "type": ACTION.PLAY,
                "target": state.observed_hands[state.our_player_index][action["card_index"]]['order']
            }
        elif action_type == 'DISCARD':
            ret = {
                "tableID": table_id,
                "type": ACTION.DISCARD,
                "target": state.observed_hands[state.our_player_index][action["card_index"]]['order'],
            }
        elif action_type == 'REVEAL_RANK':
            ret = {
                "tableID": table_id,
                "type": ACTION.RANK_CLUE,
                "target": (state.current_player + action['target_offset']) % state.num_players,
                "value": action["rank"] + 1
            }
        else:
            ret = {
                "tableID": table_id,
                "type": ACTION.COLOR_CLUE,
                "target": (state.current_player + action['target_offset']) % state.num_players,
                "value": suit_to_server_index(action["color"])
            }
        return ret


def get_legal_moves(state):
    """ Computes observation['legal_moves'] or observation.legal_moves(), depending on use_pyhanabi_mock"""
    # order is 1. discard 2. play 3. reveal_color reveal rank and RYGWB for color
    legal_moves = []

    # discard if possible
    if state.information_tokens < MAX_CLUE_NUM:
        for i in range(state.hand_size):
            legal_moves.append({'action_type': 'DISCARD', 'card_index': i})

    # play
    for i in range(state.hand_size):
        legal_moves.append({'action_type': 'PLAY', 'card_index': i})

    # clue if info token available
    if state.information_tokens > 0:
        hand_list = observed_hands_to_rainbow_obs(state)

        # append colors
        for i in range(1, state.num_players):
            colors = set()
            for card in hand_list[i]:
                colors.add(card['color'])

            colors = sort_colors(colors)
            for c in colors:
                legal_moves.append({'action_type': 'REVEAL_COLOR', 'target_offset': i, 'color': c})

        # append ranks
        for i in range(1, state.num_players):
            ranks = set()
            for card in hand_list[i]:
                ranks.add(card['rank'])
            for r in ranks:
                legal_moves.append({'action_type': 'REVEAL_RANK', 'target_offset': i, 'rank': r})
    for move in legal_moves:
        move['move_int'] = get_move_uid(move)
    return legal_moves


def get_legal_moves_as_int(legal_moves, num_moves):
    legal_moves_as_int = [-np.Inf for _ in range(num_moves)]
    tmp_legal_moves_as_int = [get_move_uid(move) for move in legal_moves]
    for move in tmp_legal_moves_as_int:
        legal_moves_as_int[move] = 0.0
    return np.array(legal_moves_as_int)


def get_move_uid(move, hand_size=5, num_colors=5, num_ranks=5, num_players=2):
    if move["action_type"] == "DISCARD":
        card_index = move["card_index"]
        return card_index

    elif move["action_type"] == "PLAY":
        card_index = move["card_index"]
        return hand_size + card_index

    elif move["action_type"] == "REVEAL_COLOR":
        target_offset = move["target_offset"]
        color = suit_to_index(move["color"])
        return hand_size + hand_size + (target_offset - 1) * num_colors + color

    elif move["action_type"] == "REVEAL_RANK":
        rank = move["rank"]
        target_offset = move["target_offset"]
        return hand_size + hand_size + (num_players - 1) * num_colors + (
                target_offset - 1) * num_ranks + rank
    else:
        print("\n==================")
        print("MOVE IS NOT POSSIBLE")
        print("===================\n")
        return -2


def sort_colors(colors):
    """ Sorts list, s.t. colors are in order RYGWB """
    result = list()
    for i in range(len(colors)):
        if 'R' in colors:
            colors.remove('R')
            result.append('R')
        if 'Y' in colors:
            colors.remove('Y')
            result.append('Y')
        if 'G' in colors:
            colors.remove('G')
            result.append('G')
        if 'W' in colors:
            colors.remove('W')
            result.append('W')
        if 'B' in colors:
            colors.remove('B')
            result.append('B')

    return result


def observed_hands_to_rainbow_obs(state):
    original_hands = state.observed_hands[state.our_player_index:] + state.observed_hands[
                                                                     :state.our_player_index]
    new_hand_observation = []
    for hand in original_hands:
        new_hand = []
        for card in hand:
            new_card = {'color': card['color'], 'rank': card['rank']}
            new_hand.append(new_card)
        new_hand_observation.append(new_hand)
    return new_hand_observation


def suit_to_index(suit):
    if suit == 'R':
        return 0
    elif suit == 'Y':
        return 1
    elif suit == 'G':
        return 2
    elif suit == 'W':
        return 3
    elif suit == 'B':
        return 4
    else:
        return None


def suit_to_server_index(suit):
    if suit == 'R':
        return 0
    elif suit == 'Y':
        return 1
    elif suit == 'G':
        return 2
    elif suit == 'B':
        return 3
    elif suit == 'W':
        return 4
    else:
        return None


def server_suit_index_to_real_index(suit_index):
    if suit_index == 3:
        return 4
    elif suit_index == 4:
        return 3
    else:
        return suit_index


def suit_index_to_color(i):
    if i == 0:
        return 'R'
    elif i == 1:
        return 'Y'
    elif i == 2:
        return 'G'
    elif i == 3:
        return 'W'
    elif i == 4:
        return 'B'
    else:
        return None


def state_to_dictionary(state):
    return \
        {
            'information_tokens': state.information_tokens,
            'our_player_index': state.our_player_index,
            'discard_pile': state.discard_pile,
            'turn': state.turn,
            'current_player': state.current_player,
            'current_player_offset': state.current_player_offset,
            'life_tokens': state.life_tokens,
            'num_players': state.num_players,
            'deck_size': state.deck_size,
            'fireworks': state.fireworks,
            'observed_hands': state.observed_hands[state.our_player_index:] + state.observed_hands[
                                                                              :state.our_player_index],
            'card_knowledge': state.card_knowledge[state.our_player_index:] + state.card_knowledge[
                                                                              :state.our_player_index],
            'cards_plausible': state.cards_plausible[state.our_player_index:] + state.cards_plausible[
                                                                                :state.our_player_index]
        }


def state_to_rainbow_obs(state):
    vectorizer = ObservationVectorizer(state)
    obs = {}
    obs['current_player'] = state.current_player
    obs['current_player_offset'] = state.current_player_offset
    obs['life_tokens'] = state.life_tokens
    obs['information_tokens'] = state.information_tokens
    obs['num_players'] = state.num_players
    obs['deck_size'] = state.deck_size
    obs['fireworks'] = state.fireworks
    obs['observed_hands'] = observed_hands_to_rainbow_obs(state)
    obs['discard_pile'] = state.discard_pile
    obs['card_knowledge'] = state.cards_plausible[state.our_player_index:] + state.cards_plausible[
                                                                             :state.our_player_index]
    obs['last_moves'] = state.last_moves
    legal_moves = get_legal_moves(state)
    vectorized = vectorizer.vectorize_observation(obs)
    d = {'legal_moves_as_int': get_legal_moves_as_int(legal_moves, state.max_moves),
         'vectorized': vectorized, 'legal_moves': legal_moves}
    return d


def add_to_last_moves(state, data):
    if data['type'] not in ['draw', 'discard', 'play', 'clue']:
        return
    move = json_to_pyhanabi.get_pyhanabi_move_mock(data, state)
    scored = state.gained_score  # boolean, True if firework increased
    information_token = state.gained_info  # boolean, True if info_token gained on discard or play
    card_info_revealed = list()
    if data['type'] == 'clue':
        card_info_revealed = get_touched_indices(state, data)
    deal_to_player = -1
    if data['type'] == 'draw':
        deal_to_player = data["playerIndex"]
    if 'playerIndex' in data:
        player_index = data['playerIndex']
    elif 'giver' in data:
        player_index = data['giver']
    else:
        exit(0)
    history_item_mock = json_to_pyhanabi.HanabiHistoryItemMock(
        move=move,
        player=player_index,
        scored=scored,
        information_token=information_token,
        color=None,
        rank=None,
        card_info_revealed=card_info_revealed,
        card_info_newly_revealed=None,
        deal_to_player=deal_to_player
    )
    state.last_moves.insert(0, history_item_mock)


def get_touched_indices(state, dict_clue):
    card_info_revealed = list()
    target = dict_clue['target']
    touched_cards = dict_clue['list']
    hand = state.observed_hands[target]
    for c in touched_cards:
        for i in range(len(hand)):
            card = hand[i]
            if card["order"] == c:
                card_index = i
                card_info_revealed.append(card_index)
    return card_info_revealed


def remove_card_from_hand(state, player_index, order):
    hand = state.observed_hands[player_index]
    card_index = -1
    for i in range(len(hand)):
        card = hand[i]
        if card["order"] == order:
            card_index = i
    if card_index == -1:
        print(
            "error: unable to find card with order " + str(order) + " in"
                                                                    "the hand of player " + str(player_index)
        )
        return None
    card = hand[card_index]
    del state.card_knowledge[player_index][card_index]
    del state.cards_plausible[player_index][card_index]
    del hand[card_index]
    return card
