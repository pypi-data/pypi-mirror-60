import os.path
from tensorflow.python import keras
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras import losses
from tensorflow.python.keras import layers
from .dataset_model import DatasetModel
from tensorflow.python.keras.datasets import mnist
from datetime import datetime


class LeNet5(DatasetModel, Sequential):
    def __init__(self, weight_path=None):
        super().__init__()

        # Load dataset as train and test sets
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        # Set numeric type to float32 from uint8
        x_train = x_train.astype("float32")
        x_test = x_test.astype("float32")

        # Normalize value to [0, 1]
        x_train /= 255
        x_test /= 255

        # Transform lables to one-hot encoding
        y_train = keras.utils.to_categorical(y_train, 10)
        y_test = keras.utils.to_categorical(y_test, 10)

        # Reshape the dataset into 4D array
        x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
        x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)

        self.dataset = (x_train, y_train), (x_test, y_test)

        # Define model architecture
        self.add(layers.Conv2D(6, kernel_size=(5, 5), strides=(1, 1),
                               activation="tanh", input_shape=(28, 28, 1),
                               padding="same"))
        self.add(layers.AveragePooling2D(pool_size=(
            2, 2), strides=(2, 2), padding="valid"))
        self.add(layers.Conv2D(16, kernel_size=(5, 5), strides=(
            1, 1), activation="tanh", padding="valid"))
        self.add(layers.AveragePooling2D(pool_size=(
            2, 2), strides=(2, 2), padding="valid"))

        self.add(layers.Flatten())
        self.add(layers.Dense(units=120, activation="tanh"))
        self.add(layers.Flatten())

        self.add(layers.Dense(84, activation="tanh"))
        self.add(layers.Dense(10, activation="softmax"))

        self.compile(loss=losses.categorical_crossentropy,
                     optimizer="SGD", metrics=["accuracy"])
        # self.summary()

        if not weight_path:
            weight_path="data/lenet5.h5"

        if os.path.isfile(weight_path):
            self.load_weights(weight_path)
            print(
                f"Weights of LeNet5 successfully loaded from file '{weight_path}'!")
        else:
            print(f"Unable to load weights! Use method 'train()' to train LeNet5")

    def train(self, epochs=10):
        # Define the Keras TensorBoard callback.
        (x_train, y_train), (x_test, y_test)=self.dataset
        self.fit(x=x_train, y=y_train, epochs=epochs, batch_size=128,
                 validation_data=(x_test, y_test), verbose=1)

    def save_custom(self, weight_path=None):
        if not weight_path:
            weight_path="data/lenet5.h5"
        self.save_weights(weight_path)

    def eval(self):
        _, (x_test, y_test)=self.dataset
        print(x_test.shape)
        test_score=self.evaluate(x_test, y_test)
        print("LeNet5: loss: {:.4f}, accuracy: {:.4f}".format(
            test_score[0], test_score[1]))

    def get_dataset(self):
        return self.dataset
