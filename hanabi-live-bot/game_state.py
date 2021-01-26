from constants import MAX_CLUE_NUM

NUM_COLORS = 5
NUM_RANKS = 5


class GameState:
    def __init__(self):
        self.information_tokens = MAX_CLUE_NUM
        self.player_names = []
        self.our_player_index = -1
        self.discard_pile = []  # A list of dicionaries, each representing a card in the discard pile.
        self.turn = -1
        self.current_player = -1
        self.current_player_offset = 0
        self.life_tokens = 3
        self.max_life_tokens = 3
        self.num_players = 0
        self.hand_size = 0
        self.deck_size = 50
        self.num_colors = 5
        self.num_ranks = 5
        self.variant = 'Hanabi-Full'
        self.max_information_tokens = MAX_CLUE_NUM
        self.max_moves = 0
        self.fireworks = {'R': 0, 'Y': 0, 'G': 0, 'W': 0, 'B': 0}
        self.legal_moves = []  # A list of dictionaries of the form {'action_type: 'PLAY', 'card_index' : 3}, for example.
        self.legal_moves_as_int = []  # A list of the int representation of legal moves
        self.observed_hands = []  # A list of lists representing player's hands, each containing a dictionary for each card in
        # that hand, e.g. [{'color': None, 'rank': -1}, {'color': None, 'rank': -1}, {'color': None, 'rank': -1}...
        self.card_knowledge = []  # A list of lists representing player's knowledge of their own hands, each contaiing a
        # dictionary for each card in that hand, e.g. [[{'color': 'R', 'rank': None}, {'color': 'Y', 'rank': None}...
        self.cards_plausible = []
        self.last_moves = []
        self.gained_info = False
        self.gained_score = False

    def __str__(self) -> str:
        return "turn: {}\n" \
               "observed_hands: {}".format(self.turn, self.observed_hands)

    def num_cards(self, color, rank, variant):
        """ Input: Color string in "RYGWB" and rank in [0,4]
        Output: How often deck contains card with given color and rank, i.e. 1-cards will be return 3"""
        if rank == 0:
            return 3
        elif rank < 4:
            return 2
        elif rank == 4:
            return 1
        else:
            return 0
