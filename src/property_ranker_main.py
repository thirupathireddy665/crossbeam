import logging
import numpy as np
import pandas as pd
from bustle_generated_properties import *
from utils import *
from datetime import datetime
import os
import sys

if __name__ == "__main__":

    start_range = 1
    end_range = 1

    property_ranks_file = config_directory+"property_ranks.csv"

    if len(sys.argv) == 2:
        slurm_task_id = int(sys.argv[1])
        start_range = slurm_task_id
        end_range = start_range
        logging.basicConfig(filename=logs_directory+"property_ranker.log",
                            filemode='a',
                            format="[Task: " + str(slurm_task_id) + "] " + '%(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(filename=logs_directory+"property_ranker.log",
                            filemode='a',
                            format='%(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    logging.info("start range: " + str(start_range))
    logging.info("end range: " + str(end_range))

    number_of_properties = len(InputStringOutputStringProperties)
    ranks_sum = list(range(0, number_of_properties))
    for property_index in range(0, number_of_properties):
        ranks_sum[property_index] = 0

    begin_time = datetime.now()

    for file_index in range(start_range, end_range + 1):
        property_filename = property_data_directory+"property_data_" + str(file_index) + ".csv"
        if os.path.exists(property_filename):
            dataFrame = pd.read_csv(property_filename)
            logging.info("property file is: "+str(property_filename))
            logging.info("dataFrame shape before removing duplicates: " + str(dataFrame.shape))
            dataFrame = dataFrame.drop_duplicates()
            logging.info("dataFrame shape after removing duplicates: " + str(dataFrame.shape))
            dataFrame = dataFrame.drop(columns='program')
            logging.info("columns: " + str(list(dataFrame.columns)))

            properties_indices = list(range(0, number_of_properties))
            properties_ranked = []

            for property_number in range(0, number_of_properties):

                max_number_of_distinct_pairs = 0
                property_selected = None

                for property_index in properties_indices:

                    properties_group = ["prop" + str(index) for index in properties_ranked]
                    properties_group.append("prop" + str(property_index))
                    grouped_dataframe = dataFrame.groupby(properties_group)
                    group_counts = []

                    for key, values in grouped_dataframe:
                        group_counts.append(values.shape[0])

                    number_of_distinct_pairs = 0

                    for first_group_index in range(0, len(group_counts)):
                        for second_group_index in range(first_group_index + 1, len(group_counts)):
                            number_of_distinct_pairs += group_counts[first_group_index] * group_counts[
                                second_group_index]

                    if number_of_distinct_pairs > max_number_of_distinct_pairs:
                        max_number_of_distinct_pairs = number_of_distinct_pairs
                        property_selected = property_index

                properties_ranked.append(property_selected)
                properties_indices.remove(property_selected)

                logging.info("properties ranked: " + str(properties_ranked))
                logging.info("properties indices: " + str(properties_indices))

            for rank, property_index in enumerate(properties_ranked):
                ranks_sum[property_index] += rank

            logging.info("ranks so far: "+str(ranks_sum))

    logging.info("final ranks sum: " + str(ranks_sum))
    logging.info("Time taken: " + str(datetime.now() - begin_time))

    ranks_sum_list = []
    ranks_sum_dict = {}
    for property_index in range(0, number_of_properties):
        ranks_sum_dict["prop_"+str(property_index)+"_rank"] = ranks_sum[property_index]
    ranks_sum_list.append(ranks_sum_dict)

    dataFrame = pd.DataFrame(ranks_sum_list)
    logging.info("Saving the ranks sum list to csv file...")
    dataFrame.to_csv(property_ranks_file, index=False, mode='a',
                     header=not os.path.exists(property_ranks_file))

    ranked_indices = list(np.argsort(ranks_sum))
    logging.info("final order of properties: "+str(ranked_indices))
