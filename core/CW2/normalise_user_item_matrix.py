import pandas as pd
from .populate_user_item_matrix import data_matrix
from .constants import *


"""
Each person must have an overall score, and can normalise their values by using the ratios at each level to change
their score for a particular class,category or plan. We'll set the total score for a person to be 17.5, with 10 coming
from classes, 5 coming from categorys and 2.5 coming from plans, the exact same ratio as the decay propogation we 
sent through when allocating raw points to each sector in <i>populate_user_item_matrix.py</i>
"""


"""
linebreak tells us:
Column 2  - 19  :   Class
Column 20 - 27  :   Category
Column 28 - 31  :   Plan
"""

linebreak = [2,len(data_matrix.columns) -1]

for i in range(2,len(data_matrix.columns)-1):
    if data_matrix.columns[i].lower() > data_matrix.columns[i+1].lower():
        linebreak.append(i)
        linebreak.append(i+1)

linebreak.sort()

empty_matrix = pd.read_csv('./empty_user_item_matrix.csv')

for i in range(data_matrix.shape[0]):
    sum_classes = data_matrix.iloc[i, [i for i in range(linebreak[0], linebreak[1] + 1)]].sum()
    sum_categorys = data_matrix.iloc[i, [i for i in range(linebreak[2], linebreak[3] + 1)]].sum()
    sum_plans = data_matrix.iloc[i, [i for i in range(linebreak[4], linebreak[5] + 1)]].sum()

    for j in range(linebreak[0],linebreak[1]+1):
        value = round((data_matrix.iloc[i,j] / sum_classes)*CLASS_VALUE,2)
        empty_matrix.iloc[i,j] = value
    for j in range(linebreak[2],linebreak[3]+1):
        value = round((data_matrix.iloc[i, j] / sum_categorys) * CATEGORY_VALUE, 2)
        empty_matrix.iloc[i, j] = value
    for j in range(linebreak[4],linebreak[5]+1):
        value = round((data_matrix.iloc[i, j] / sum_plans) * PLAN_VALUE, 2)
        empty_matrix.iloc[i, j] = value

empty_matrix.to_csv('user_item_matrix_normalised.csv',index=False)
print(empty_matrix)