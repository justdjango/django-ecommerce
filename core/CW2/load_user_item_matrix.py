import pandas as pd
import numpy as np
from .load_usage_data import full_table


unique_users = full_table.groupby('Name').size().__len__()
unique_classes = full_table.groupby('Class').size().__len__()
unique_categorys = full_table.groupby('Category').size().__len__()
unique_plans = full_table.groupby('Plan').size().__len__()
unique_ccp = unique_classes + unique_categorys + unique_plans

users_list_names = pd.DataFrame(full_table.groupby('ID')['Name'].unique().values)
users_list_ids = pd.DataFrame(full_table.groupby('ID')['Name'].unique().index)

feature_list_classes = pd.Series(full_table.groupby('Class').size().index)
feature_list_categorys = pd.Series(full_table.groupby('Category').size().index)
feature_list_plans = pd.Series(full_table.groupby('Plan').size().index)
feature_list_ccp = pd.concat([feature_list_classes,feature_list_categorys,feature_list_plans], ignore_index=True)

zero_table = np.zeros(shape=(unique_users,unique_ccp))
data_matrix = pd.DataFrame(data=zero_table,columns=feature_list_ccp)

data_matrix.insert(0,column='ID',value=users_list_ids)
data_matrix.insert(1,column='Name',value=users_list_names)

data_matrix['Name'] = data_matrix['Name'].str.get(0)

data_matrix.to_csv('empty_user_item_matrix.csv',index=False)
