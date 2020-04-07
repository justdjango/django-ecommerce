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
    :return: customer churn prediction (numpy array) - Yes: the customer will leave, No: customer will remain
    '''
    df = pd.DataFrame([dict])

    dt = joblib.load("dtree_classifier2")

    print('Is the customer going to churn: ' + dt.predict(df))
    print(dt.predict(df)[-1])
