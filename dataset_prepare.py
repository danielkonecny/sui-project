import pickle
import os
import numpy as np


def iterate_through_logs(directory_str="game_logs"):
    directory = os.fsencode(directory_str)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".pickle"):
            with open(os.path.join(directory_str, filename), "rb") as f:
                data = pickle.load(f)
        yield data, filename


def get_game_report(game_index, player_count, move_count, winner):
    print(f"GAME: {game_index}")
    print(f"- number of players: {player_count}")
    print(f"- number of moves done: {move_count}")
    print(f"- winner: {winner} (indexing from 0)\n")


def get_adjacent_matrix(boards):
    adjacent_matrix = np.zeros((len(boards), len(boards)))
    for area_index in range(len(boards)):
        adjacent_indices = boards[area_index]['adjacent_areas']
        adjacent_matrix[area_index][adjacent_indices] = 1
    return adjacent_matrix


def get_dice_matrix(boards):
    dice_matrix = np.zeros((len(boards), 1))
    for area_index in range(len(boards)):
        dice_matrix[area_index][0] = boards[area_index]['dices']
    return dice_matrix


def get_owner_matrix(boards, player_count):
    # Using one-hot encoding.
    owner_matrix = np.zeros((len(boards), player_count))
    for area_index in range(len(boards)):
        owner_index = boards[area_index]['owner']
        owner_matrix[area_index][owner_index] = 1
    return owner_matrix


def get_winner_vector(last_battle, player_count):
    winner_vector = np.zeros(player_count)
    for area in last_battle:
        winner_vector[area['owner']] += 1

    for player_index in range(len(winner_vector)):
        if winner_vector[player_index] == len(last_battle)-1:
            winner_vector[player_index] = 1
        elif winner_vector[player_index] == 1:
            winner_vector[player_index] = 0
        else:
            winner_vector[player_index] = 0

    return winner_vector


def save_dataset(battles, winners):
    np.save("datasets/battles.npy", battles)
    np.save("datasets/winners.npy", winners)


def main():
    first_game = True
    battles = None
    winners = None

    for log, game_index in iterate_through_logs("test_logs"):
        battle_count = len(log['battles'])
        area_count = len(log['battles'][0]['areas'])
        player_count = log['players']
        game_battles = np.empty((battle_count, area_count, area_count+player_count+1))
        game_winners = np.empty((battle_count, player_count))
        battle_index = 0

        winner_vector = get_winner_vector(log['battles'][-1]['areas'], log['players'])
        for battle in log['battles']:
            adjacent_matrix = get_adjacent_matrix(battle['areas'])
            dice_matrix = get_dice_matrix(battle['areas'])
            owner_matrix = get_owner_matrix(battle['areas'], log['players'])
            game_battles[battle_index] = np.hstack((adjacent_matrix, dice_matrix, owner_matrix))
            game_winners[battle_index] = winner_vector
            battle_index += 1

        get_game_report(game_index, log['players'], len(game_battles), np.where(winner_vector == 1.0)[0][0])

        if first_game:
            battles = game_battles
            winners = game_winners
            first_game = False
        else:
            battles = np.concatenate((battles, game_battles))
            winners = np.concatenate((winners, game_winners))

    save_dataset(battles, winners)


if __name__ == '__main__':
    main()
