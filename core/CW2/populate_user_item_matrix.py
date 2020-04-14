import pandas as pd
from .load_usage_data import full_table
from .load_user_item_matrix import data_matrix
from .constants import *


for i in range(full_table.shape[0]):
    person = full_table['Name'].iloc[i]

    class_attended = full_table['Class'].iloc[i]
    category_attended = full_table['Category'].iloc[i]
    plan_attended = full_table['Plan'].iloc[i]

    index_number = data_matrix.loc[data_matrix['Name'] == person].index

    data_matrix.loc[index_number,class_attended] += CLASS_VALUE
    data_matrix.loc[index_number,category_attended] += CATEGORY_VALUE
    data_matrix.loc[index_number,plan_attended] += PLAN_VALUE

data_matrix.to_csv('user_item_matrix.csv',index=False)

zeros = 0
non_zeros = 0

for i in range(data_matrix.shape[0]):
    for j in range(2,data_matrix.shape[1]):
        if data_matrix.iloc[i,j] == 0:
            zeros += 1
        else:
            non_zeros += 1

# print(non_zeros/ (zeros+non_zeros))
# print(data_matrix.columns)
