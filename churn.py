import pandas as pd


# TODO: fill the method below and in case create other method for the churn.
#  For now: It takes the dictionary with the answers (yes/no) and transforms
#  the dictionary in a pandas dataframe.

def churn(dict):
    '''
    :param dict: dictionary with all the answers from the user about the form
    :return: now it prints the dataframe, but in the future it should return the results
    from the churn model
    '''
    df = pd.DataFrame([dict])
    print("\nMove data in a pandas dataframe:\n\n")
    print(df)
    print("\n\nMoved data in pandas dataframe")
