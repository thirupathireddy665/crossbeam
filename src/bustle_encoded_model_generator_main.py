import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
from bustle_generated_properties import *
from utils import *

if __name__ == "__main__":
    dataFrame = pd.read_csv(config_directory+"sygus_bustle_encoded_training_data.csv", dtype=np.byte)
    input_layer_size = 4 * (85 + 4 * len(InputStringOutputStringProperties))
    X = dataFrame.iloc[:, :input_layer_size]
    y = dataFrame.iloc[:, input_layer_size:]
    print("X shape: ", X.shape)
    print("y shape: ", y.shape)

    BustleModel = Sequential()
    BustleModel.add(
        Dense((input_layer_size * 3) / 2, input_dim=X.shape[1], activation="relu"))
    BustleModel.add(Dense(y.shape[1], activation="sigmoid"))
    BustleModel.compile(loss="binary_crossentropy", optimizer="adam", metrics=['accuracy'])
    BustleModel.summary()
    BustleModel.fit(X, y, verbose=1, epochs=10, batch_size=64)
    BustleModel.evaluate(X, y)
    BustleModel.save(models_directory+"EncodedBustleModelForPS.hdf5")
