import tensorflow as tf
import numpy as np


def load_dataset(path, xs, ys):
    battles = np.load(f"{path}{xs}")
    winners = np.load(f"{path}{ys}")
    print("DATASET LOADED")
    print(f"- battles: {battles.shape}")
    print(f"- winners: {winners.shape}")
    return battles, winners


def batch_provider(batch_size=256, path="datasets/", xs="battles.npy", ys="winners.npy"):
    battles, winners = load_dataset(path, xs, ys)
    shuffle = np.random.permutation(len(winners))
    for i in range(0, len(shuffle), batch_size):
        batch_indices = shuffle[i:i + batch_size]
        yield battles[batch_indices], winners[batch_indices]


def define_model(player_count, input_shape):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Flatten(input_shape=input_shape))
    assert model.output_shape == (None, 986)
    model.add(tf.keras.layers.Dense(2048, activation='relu'))
    model.add(tf.keras.layers.Dense(2048, activation='relu'))
    model.add(tf.keras.layers.Dense(4196, activation='relu'))
    model.add(tf.keras.layers.Dense(4196, activation='relu'))
    model.add(tf.keras.layers.Dense(player_count, activation='softmax'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def train_model(model, batch_size=256, epoch_count=10, first_epoch=0):
    # battles, winners = load_dataset("datasets/")
    # model.fit(battles, winners, epochs=epoch_count, batch_size=batch_size, verbose=0)
    path = "datasets/"
    xs = "train_battles.npy"
    ys = "train_winners.npy"

    losses = []

    for epoch_index in range(first_epoch, first_epoch+epoch_count):
        print(f"Epoch {epoch_index:04d}")
        batch_index = 0
        for boards, winners in batch_provider(batch_size, path, xs, ys):
            loss = model.train_on_batch(boards, winners)
            print(f"- Batch {batch_index:03d} - loss: {loss}")
            batch_index += 1
            losses.append(loss)


def evaluate_model(model):
    path = "datasets/"
    xs = "test_battles.npy"
    ys = "test_winners.npy"

    battles, winners = load_dataset(path, xs, ys)
    loss = model.evaluate(battles, winners)

    return loss


def main():
    player_count = 4
    input_shape = (29, 34)

    batch_size = 256
    epoch_count = 50
    first_epoch = 0

    model = define_model(player_count, input_shape)
    train_model(model, batch_size, epoch_count, first_epoch)
    model.save("models/model.h5")

    # model = tf.keras.models.load_model("models/model.h5")
    # evaluation = evaluate_model(model)
    # print(f"Evaluation: {evaluation}")


if __name__ == '__main__':
    main()
