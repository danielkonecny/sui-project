import pickle
import os
import numpy as np


def iterate_through_logs(directory_str="logs"):
    directory = os.fsencode(directory_str)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".pickle"):
            with open(os.path.join(directory_str, filename), "rb") as f:
                try:
                    data = pickle.load(f)
                    yield data, filename
                except EOFError:
                    print(f"File {filename} failed.")
                except pickle.UnpicklingError:
                    print(f"Pickle error.")


def get_game_report(game_index, player_count, move_count, winner):
    print(f"GAME: {game_index}")
    print(f"- number of players: {player_count}")
    print(f"- number of moves done: {move_count}")
    print(f"- winner: {winner} (indexing from 0)\n")


def get_adjacent_vector(boards):
    index = 0
    adjacent_vector = np.zeros(((len(boards) - 1) * len(boards)) // 2)
    for area_index in range(len(boards)):
        for adjacent_index in boards[area_index]['adjacent_areas']:
            if adjacent_index > area_index:
                adjacent_vector[index-area_index+adjacent_index-1] = 1
        index += (len(boards) - 1 - area_index)
    return adjacent_vector


def get_dice_vector(boards):
    dice_vector = np.zeros(len(boards))
    for area_index in range(len(boards)):
        dice_vector[area_index] = boards[area_index]['dices']/8
    return dice_vector


def get_owner_vector(boards, player_count):
    # Using one-hot encoding.
    owner_vector = np.zeros((len(boards), player_count))
    for area_index in range(len(boards)):
        owner_index = boards[area_index]['owner']
        owner_vector[area_index][owner_index] = 1
    return owner_vector.flatten()


def get_turn_vector(turn):
    threshold = 50
    if turn > threshold:
        return np.array([0])
    else:
        turn = 1 - turn/threshold
        return np.array([turn])


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


def prepare_dataset():
    first_game = True
    battles = None
    winners = None

    for log, game_index in iterate_through_logs():
        battle_count = len(log['battles'])
        area_count = len(log['battles'][0]['areas'])
        player_count = log['players']
        size = ((area_count-1)*area_count)//2 + area_count + player_count*area_count + 1
        game_battles = np.empty((battle_count, size))
        game_winners = np.empty((battle_count, player_count))
        battle_index = 0

        winner_vector = get_winner_vector(log['battles'][-1]['areas'], log['players'])
        for battle in log['battles']:
            adjacent_vector = get_adjacent_vector(battle['areas'])
            dice_vector = get_dice_vector(battle['areas'])
            owner_vector = get_owner_vector(battle['areas'], log['players'])
            turn_vector = get_turn_vector(battle['turn'])
            game_battles[battle_index] = np.hstack((adjacent_vector, dice_vector, owner_vector, turn_vector))
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

    assert len(battles) == len(winners)

    return battles, winners


class Dataset:
    def __init__(self):
        self.train_xs = None
        self.train_ys = None
        self.test_xs = None
        self.test_ys = None
        self.player_count = 4
        self.data_shape = 552
        # self.data_shape = (29, 34)

    def __str__(self):
        report = "DATASET\n"
        report += f"Train Xs: {self.train_xs.shape}\nTrain Ys: {self.train_ys.shape}\n"
        report += f"Test Xs: {self.test_xs.shape}\nTest Ys: {self.test_ys.shape}"
        return report

    def load(self, path="dicewars/ai/xrysav27/datasets/"):
        self.train_xs = np.load(f"{path}train_xs.npy")
        self.train_ys = np.load(f"{path}train_ys.npy")
        self.test_xs = np.load(f"{path}test_xs.npy")
        self.test_ys = np.load(f"{path}test_ys.npy")

    def reload(self, path="dicewars/ai/xrysav27/datasets/", train_percentage=0.9):
        xs, ys = prepare_dataset()
        size = len(xs)

        shuffle = np.random.permutation(size)
        shuffled_xs = xs[shuffle]
        shuffled_ys = ys[shuffle]

        dividing_index = int(size*train_percentage)
        self.train_xs = shuffled_xs[:dividing_index]
        self.train_ys = shuffled_ys[:dividing_index]
        self.test_xs = shuffled_xs[dividing_index:]
        self.test_ys = shuffled_ys[dividing_index:]

        np.save(f"{path}train_xs.npy", self.train_xs)
        np.save(f"{path}train_ys.npy", self.train_ys)
        np.save(f"{path}test_xs.npy", self.test_xs)
        np.save(f"{path}test_ys.npy", self.test_ys)

    def provide_batch(self, batch_size=256):
        size = len(self.train_ys)
        shuffle = np.random.permutation(size)
        for i in range(0, size, batch_size):
            batch_indices = shuffle[i:i + batch_size]
            yield self.train_xs[batch_indices], self.train_ys[batch_indices]


if __name__ == '__main__':
    dataset = Dataset()
    dataset.reload()
    print(dataset)
