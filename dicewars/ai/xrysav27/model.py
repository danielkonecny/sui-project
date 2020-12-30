import tensorflow as tf
import numpy as np

from .dataset import Dataset


class Model:
    def __init__(self):
        self.dataset = Dataset()
        self.batch_size = 256
        self.model = tf.keras.Sequential()
        self.model.add(tf.keras.layers.Dense(1024, activation='relu', input_dim=self.dataset.data_shape))
        self.model.add(tf.keras.layers.Dropout(0.4))
        self.model.add(tf.keras.layers.Dense(1024, activation='relu'))
        self.model.add(tf.keras.layers.Dropout(0.4))
        self.model.add(tf.keras.layers.Dense(self.dataset.player_count, activation='softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    def train(self, epoch_count=5):
        self.dataset.load()

        for epoch_index in range(epoch_count):
            print(f"Epoch {epoch_index:04d}")
            batch_index = 0
            for batch_battles, batch_winners in self.dataset.provide_batch(self.batch_size):
                loss = self.model.train_on_batch(batch_battles, batch_winners)
                print(f"- Batch {batch_index:03d} - loss: {loss}")
                batch_index += 1
            self.model.save_weights(f'weights/model_weights{epoch_index:04d}.h5')

    def save(self):
        self.model.save(f'model.h5')

    def load(self):
        try:
            self.model = tf.keras.models.load_model(f'model.h5')
        except Exception as e:
            print(e)

    def evaluate(self):
        epoch_index = 10
        self.model.load_weights(f'weights/model_weights{epoch_index:04d}.h5')
        self.model.evaluate(self.dataset.test_xs, self.dataset.test_ys)

    def predict_board(self, board, turn):
        threshold = 50
        index = 0
        model_input = np.zeros(552)
        for key, area in board.areas.items():
            for adjacent_index in area.neighbours:
                if (adjacent_index - 1) > (int(key) - 1):
                    model_input[index - (int(key) - 1) + adjacent_index - 2] = 1
            index += (29 - 1 - (int(key) - 1))
            model_input[int(key) - 1 + 406] = area.dice/8
            model_input[4*(int(key) - 1) - 1 + 435 + area.owner_name] = 1
            if turn > threshold:
                model_input[551] = 0
            else:
                model_input[551] = 1 - turn / threshold

        model_input = np.expand_dims(model_input, 0)
        return np.squeeze(self.model.predict(model_input))

    def predict(self):
        epoch_index = 10
        self.model.load_weights(f'weights/model_weights{epoch_index:04d}.h5')
        prediction = self.model.predict(self.dataset.test_xs[:15000:1000])
        for i, j in zip(range(0, 15000, 1000), range(15)):
            print(f"{self.dataset.test_ys[i]} - {prediction[j]}")


if __name__ == '__main__':
    epoch_count = 10

    model = Model()
    model.dataset.reload()
    model.train(epoch_count)
    model.save()
