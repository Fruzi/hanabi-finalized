def get_vector(file):
    with open(file) as iFile:
        bits = []
        for line in iFile:
            for char in line:
                if char == '0' or char == '1':
                    bits.append(int(char))
        return bits


def get_hands(vec):
    hand = []
    for i in range(5):
        offset = i * 25
        color = -1
        rank = -1
        for j in range(0, 25):
            if vec[offset + j] == 1:
                color = int(j / 5)
                rank = j % 5
        hand.append({'color': color, 'rank': rank})
    return hand


def get_missing_cards(vec):
    return vec[125:127]


def get_deck_size(vec):
    offset = 127
    deck_size = 0
    for i in range(40):
        if vec[offset + i] == 1:
            deck_size += 1
    return deck_size


def get_fireworks(vec):
    offset = 127 + 40
    fireworks = []
    for j in range(0, 25):
        if vec[offset + j] == 1:
            color = int(j / 5)
            rank = j % 5
            fireworks.append({'color': color, 'rank': rank + 1})
    return fireworks


def get_info(vec):
    offset = 127 + 40 + 25
    info = 0
    for i in range(8):
        if vec[offset + i] == 1:
            info += 1
    return info


def get_life(vec):
    offset = 127 + 40 + 25 + 8
    life = 0
    for i in range(3):
        if vec[offset + i] == 1:
            life += 1
    return life


def get_num_copies(rank):
    if rank == 5:
        return 1
    if rank > 1:
        return 2
    return 3


def get_discard(vec):
    offset = 127 + 40 + 25 + 8 + 3
    discards = []
    for c in range(5):
        for r in range(5):
            for i in range(get_num_copies(r + 1)):
                if vec[offset + i] == 1:
                    discards.append({'color': c, 'rank': r})
            offset += get_num_copies(r + 1)
    return discards


def get_last_action(vec):
    offset = 127 + 40 + 25 + 8 + 3 + 50
    if vec[offset] == 1:
        made_by = 0
    else:
        made_by = 1
    offset += 2
    for i in range(4):
        if vec[offset + i]:
            move_type = i
            break
    offset += 4
    if vec[offset] == 1:
        move_target = 0
    else:
        move_target = 1
    offset += 2
    revealed_color = -1
    for i in range(5):
        if vec[offset + i]:
            revealed_color = i
            break
    offset += 5
    revealed_rank = -1
    for i in range(5):
        if vec[offset + i]:
            revealed_rank = i
            break
    offset += 5
    indices_affected = []
    for i in range(5):
        if vec[offset + i]:
            indices_affected.append(i)
            break
    offset += 5
    card_played_index = -1
    for i in range(5):
        if vec[offset + i]:
            card_played_index = i
            break
    offset += 5
    card_played = None
    for j in range(0, 25):
        if vec[offset + j] == 1:
            color = int(j / 5)
            rank = j % 5
            card_played = {'color': color, 'rank': rank}
            break
    offset += 25
    score_increased = (vec[offset] == 1)
    offset += 1
    gained_info = (vec[offset] == 1)
    offset += 1
    return {'made_by': made_by, 'move_type': move_type, 'target': move_target, 'color_revealed': revealed_color,
            'rank_revealed': revealed_rank, 'affected_cards': indices_affected, 'played_card_ind': card_played_index,
            'played_card': card_played, 'scored': score_increased, 'gained_info_token': gained_info}


def get_card_knowledge(vec):
    offset = 127 + 40 + 25 + 8 + 3 + 50 + 55
    player_options = []
    for q in range(2):
        card_options = []
        for i in range(5):
            options = {'color': [], 'rank': []}
            for j in range(25):
                if vec[offset + j] == 1:
                    color = int(j / 5)
                    rank = j % 5
                    if color not in options['color']:
                        options['color'].append(color)
                    if rank not in options['rank']:
                        options['rank'].append(rank)
            offset += 25
            specifically_revealed_color = None
            for j in range(5):
                if vec[offset + j] == 1:
                    specifically_revealed_color = j
            options['specifically_revealed_color'] = specifically_revealed_color
            offset += 5
            specifically_revealed_rank = None
            for j in range(5):
                if vec[offset + j] == 1:
                    specifically_revealed_rank = j
            options['specifically_revealed_rank'] = specifically_revealed_rank
            offset += 5
            card_options.append(options)
        player_options.append(card_options)
    return player_options

def parse_obs(file):
    vec = get_vector(file)
    hands = get_hands(vec)
    print(hands)
    missing_cards = get_missing_cards(vec)
    print(missing_cards)
    deck_size = get_deck_size(vec)
    print(deck_size)
    fireworks = get_fireworks(vec)
    print(fireworks)
    info = get_info(vec)
    print(info)
    life = get_life(vec)
    print(life)
    discard_pile = get_discard(vec)
    # print(discard_pile)
    last_action = get_last_action(vec)
    print(f"last action was made by {last_action['made_by']}, targeting {last_action['target']}")
    card_knowledge = get_card_knowledge(vec)
    for i in range(2):
        print(f"card knowledge for (relative) player {i}")
        for j in range(5):
            print(f"{card_knowledge[i][j]}")
        print("")


if __name__ == "__main__":
    file = '/home/uzi/actual_hanabi_obs'
    parse_obs(file)
