import pandas as pd
import joblib

import warnings
# warnings.filterwarnings("ignore")

# TODO: fill the method below and in case create other method for the churn.
#  For now: It takes the dictionary with the answers (yes/no) and transforms
#  the dictionary in a pandas dataframe.


def churn(dict):
    '''
    :param dict: dictionary with all the answers from the user about the form
    :return: now it prints the dataframe, but in the future it should return the results
    from the churn model
    '''
#     df = pd.DataFrame([dict])
#     resized_df = df.drop('capacity', axis=1)

    sample = list(dict.values())
    sample.pop(3)

    cols = ['Classes_per_week', 'Happy_with_instructors', 'Happy_with_class_duration', 'Happy_with_class_timings',
            'Happy_with_class_size', 'Happy_with_facilities', 'Happy_with_price']

    sample1 = pd.DataFrame([sample], columns=cols)

    sample2 = [2, 'No', 'Yes', 'No', 'No', 'Yes', 'No']
    sample2 = pd.DataFrame([sample2], columns=cols)

    dt = joblib.load("dtree_classifier2")

    print('Sample2 churn: ' + dt.predict(sample2))

    # print('Sample churn: ' + dt.predict(sample1))
