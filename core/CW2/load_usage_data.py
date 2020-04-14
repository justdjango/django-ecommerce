import pandas as pd


datasets = \
    {
        'users':'users_modified.xlsx',
        'items':'items_modified.xlsx',
        'users_items':'user_item_reduced.xlsx'
    }

userlist = pd.read_excel(datasets['users'])
itemlist = pd.read_excel(datasets['items'])
user_item_list = pd.read_excel(datasets['users_items'])

two_tables_joined = pd.merge(user_item_list, itemlist, on='Class')
full_table = pd.merge(two_tables_joined,userlist, on='ID')[['ID','Name','Class','Category','Plan']]
