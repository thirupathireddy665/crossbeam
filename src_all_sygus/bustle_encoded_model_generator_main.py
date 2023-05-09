import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
from bustle_properties import *
from utils import *



def filter_data():
    # Read data in pandas dataframe, remove duplicates, and randomly select top 2 and a half million rows.
    df = pd.read_csv(config_directory + "sygus_bustle_encoded_training_data.csv", dtype=np.byte)
    df = df.drop_duplicates()
    return df.sample(n=2500000)

if __name__ == "__main__":
    dataFrame = filter_data()
    input_layer_size = 4 * (
            4 * len(StringProperties) +
            len(IntegerProperties) +
            len(StringProperties) +
            len(IntegerProperties) +
            len(BooleanProperties) +
            len(InputIntegerOutputStringProperties) +
            len(InputIntegerOutputIntegerProperties) +
            len(InputIntegerOutputBoolProperties) +
            4 * len(InputStringOutputStringProperties) +
            4 * len(InputStringOutputIntegerProperties) +
            4 * len(InputStringOutputBoolProperties) +
            len(BooleanProperties) +
            len(IntegerProperties) +
            len(StringProperties) +
            len(InputIntegerOutputStringProperties) +
            len(InputStringOutputStringProperties) +
            len(InputIntegerOutputIntegerProperties) +
            len(InputStringOutputIntegerProperties) +
            len(InputIntegerOutputBoolProperties) +
            len(InputStringOutputBoolProperties)
    )
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
    BustleModel.fit(X, y, verbose=1, epochs=10, batch_size=32)
    BustleModel.evaluate(X, y)
    BustleModel.save(models_directory + "AllSygusEncodedBustleModelForPS.hdf5")
