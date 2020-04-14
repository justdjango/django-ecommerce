import pandas as pd
import numpy as np
from .normalise_user_item_matrix import linebreak
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors


matrix_new = pd.read_csv('user_item_matrix_normalised.csv')

drop_columns_all_except_name_new = [i for i in range(linebreak[0],linebreak[5]+1)]
drop_list_new = matrix_new.columns[drop_columns_all_except_name_new].tolist()
name_matrix_new = matrix_new.drop(drop_list_new,axis=1)
name_dict_new = dict(name_matrix_new.values)

drop_columns_new = [i for i in range(1,linebreak[1]+1)]
drop_list_new = matrix_new.columns[drop_columns_new].tolist()
taxonomy_matrix_new = matrix_new.drop(drop_list_new,axis=1)

drop_taxonomys_new = [i for i in range(linebreak[2],linebreak[5] + 1)]
drop_taxonomys_names_new = matrix_new.columns[drop_taxonomys_new].tolist()
classes_matrix_new = matrix_new.drop(drop_taxonomys_names_new, axis=1)

X_new = taxonomy_matrix_new.drop('ID',axis=1)
y_new = pd.DataFrame(taxonomy_matrix_new['ID'])


knn_new = NearestNeighbors(n_neighbors=3,algorithm='brute',metric='cosine')
knn_new.fit(X_new)


def new_user_recommendation_new(user_taste_profile):
    X_test_new = pd.DataFrame(np.array(user_taste_profile).reshape(1,12), columns=X_new.columns)
    neighbours_new = knn_new.kneighbors(X_test_new,return_distance=False)

    neighbour_1_posn_new = neighbours_new[0][0]
    neighbour_1_ID_new = y_new.iloc[neighbours_new[0][0]].values[0]
    neighbour_1_name_new = name_dict_new[neighbour_1_ID_new]
    neighbour_2_posn_new = neighbours_new[0][1]
    neighbour_2_ID_new = y_new.iloc[neighbours_new[0][1]].values[0]
    neighbour_2_name_new = name_dict_new[neighbour_2_ID_new]
    neighbour_3_posn_new = neighbours_new[0][2]
    neighbour_3_ID_new = y_new.iloc[neighbours_new[0][2]].values[0]
    neighbour_3_name_new = name_dict_new[neighbour_3_ID_new]

    target_new = X_test_new.to_numpy().reshape(1,12)

    top_sim_new = round(cosine_similarity(target_new,X_new.iloc[neighbour_1_posn_new].to_numpy().reshape(1,12))[0][0],3)
    second_sim_new = round(cosine_similarity(target_new,X_new.iloc[neighbour_2_posn_new].to_numpy().reshape(1,12))[0][0],3)
    third_sim_new = round(cosine_similarity(target_new,X_new.iloc[neighbour_3_posn_new].to_numpy().reshape(1,12))[0][0],3)

    neighbours_similarity_dict_new = {
        neighbour_1_name_new:top_sim_new,
        neighbour_2_name_new:second_sim_new,
        neighbour_3_name_new:third_sim_new
    }

    class_names_new = classes_matrix_new.columns.tolist()

    neighbour_1_contribution_new = classes_matrix_new.iloc[neighbour_1_posn_new]
    neighbour_2_contribution_new = classes_matrix_new.iloc[neighbour_2_posn_new]
    neighbour_3_contribution_new = classes_matrix_new.iloc[neighbour_3_posn_new]

    recommended_classes_matrix_new = pd.Series(index=class_names_new, dtype=object)
    recommended_classes_matrix_new.fillna(0.0, inplace=True)

    for i in range(2,len(recommended_classes_matrix_new.index)):
        recommended_classes_matrix_new.iloc[i] += neighbour_1_contribution_new.iloc[i] * neighbours_similarity_dict_new[neighbour_1_name_new]
        recommended_classes_matrix_new.iloc[i] += neighbour_2_contribution_new.iloc[i] * neighbours_similarity_dict_new[neighbour_2_name_new]
        recommended_classes_matrix_new.iloc[i] += neighbour_3_contribution_new.iloc[i] * neighbours_similarity_dict_new[neighbour_3_name_new]

    recommended_classes_matrix_new.sort_values(ascending=False,inplace=True,kind='heapsort')
    top_3_new = [recommended_classes_matrix_new.index[0],recommended_classes_matrix_new.index[1],recommended_classes_matrix_new.index[2]]
    print("The people with the most aligned goals to you were: ")
    print(neighbours_similarity_dict_new)
    # print(top_3_new)

    return top_3_new


# sample_prefs_new = [2,4,3,1,5,5,1,2,2,4,4,1]
# new_user_recommendation_new(sample_prefs_new)
