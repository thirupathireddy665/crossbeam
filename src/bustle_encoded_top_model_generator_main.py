import numpy as np
import pandas as pd
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential

from bustle_generated_properties import *
from utils import *

if __name__ == "__main__":

    total_number_of_properties = len(InputStringOutputStringProperties)
    properties_to_discard = SubModularPropertyRankings[properties_considered_count:]
    signature_start_indices = [57, 57 + total_number_of_properties,
                               57 + (2 * total_number_of_properties),
                               57 + (3 * total_number_of_properties) + 29]
    encoding_size = 4

    dataFrame = pd.read_csv(config_directory+"sygus_bustle_encoded_training_data.csv", dtype=np.byte)
    for property_to_discard in properties_to_discard:
        for start_index in signature_start_indices:
            column = "prop" + str(property_to_discard + start_index)
            for encoding_index in range(0, encoding_size):
                dataFrame = dataFrame.drop(columns=column + "_" + str(encoding_index))

    number_of_properties = 4*(85+4*total_number_of_properties) - (4 * len(properties_to_discard) * encoding_size)

    X = dataFrame.iloc[:, :number_of_properties]
    y = dataFrame.iloc[:, number_of_properties:]
    print("X shape: ", X.shape)
    print("y shape: ", y.shape)

    BustleModel = Sequential()
    BustleModel.add(Dense((number_of_properties*3)/2, input_dim=X.shape[1], activation="relu"))
    BustleModel.add(Dense(y.shape[1], activation="sigmoid"))
    BustleModel.compile(loss="binary_crossentropy", optimizer="adam", metrics=['accuracy'])
    BustleModel.summary()
    BustleModel.fit(X, y, verbose=1, epochs=10, batch_size=64)
    BustleModel.evaluate(X, y)
    BustleModel.save(models_directory+"EncodedRankedTopBustleModelForPS.hdf5")
