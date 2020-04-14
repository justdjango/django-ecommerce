import pandas as pd
from core.CW2.normalise_user_item_matrix import linebreak
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

matrix = pd.read_csv('user_item_matrix_normalised.csv')

drop_columns_all_except_name = [i for i in range(linebreak[0],linebreak[5]+1)]
drop_list = matrix.columns[drop_columns_all_except_name].tolist()
name_matrix = matrix.drop(drop_list,axis=1)
name_dict = dict(name_matrix.values)

drop_columns = [i for i in range(1,linebreak[1]+1)]
drop_list = matrix.columns[drop_columns].tolist()
taxonomy_matrix = matrix.drop(drop_list,axis=1)

drop_taxonomys = [i for i in range(linebreak[2],linebreak[5] + 1)]
drop_taxonomys_names = matrix.columns[drop_taxonomys].tolist()
classes_matrix = matrix.drop(drop_taxonomys_names, axis=1)

X = taxonomy_matrix.drop('ID',axis=1)
y = pd.DataFrame(taxonomy_matrix['ID'])

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=1,shuffle=False)

knn = NearestNeighbors(n_neighbors=3,algorithm='brute',metric='cosine')
knn.fit(X_train)

neighbours = knn.kneighbors(X_test,return_distance=False)
neighbour_1_posn = neighbours[0][0]
neighbour_1_ID = y_train.iloc[neighbours[0][0]].values[0]
neighbour_1_name = name_dict[neighbour_1_ID]
neighbour_2_posn = neighbours[0][1]
neighbour_2_ID = y_train.iloc[neighbours[0][1]].values[0]
neighbour_2_name = name_dict[neighbour_2_ID]
neighbour_3_posn = neighbours[0][2]
neighbour_3_ID = y_train.iloc[neighbours[0][2]].values[0]
neighbour_3_name = name_dict[neighbour_3_ID]

target = X_test.to_numpy().reshape(1,12)

top_sim = round(cosine_similarity(target,X.iloc[neighbour_1_posn].to_numpy().reshape(1,12))[0][0],3)
second_sim = round(cosine_similarity(target,X.iloc[neighbour_2_posn].to_numpy().reshape(1,12))[0][0],3)
third_sim = round(cosine_similarity(target,X.iloc[neighbour_3_posn].to_numpy().reshape(1,12))[0][0],3)

neighbours_similarity_dict = {
    neighbour_1_name:top_sim,
    neighbour_2_name:second_sim,
    neighbour_3_name:third_sim
}

X_test_classes = classes_matrix.iloc[8]
already_seen_indices = X_test_classes.to_numpy().nonzero()[0]

already_seen_names = list(X_test_classes.index[i] for i in already_seen_indices)
class_names = classes_matrix.columns.tolist()
class_names_only = [class_names[i] for i in range(2,len(class_names))]

neighbour_1_contribution = classes_matrix.iloc[neighbour_1_posn]
neighbour_2_contribution = classes_matrix.iloc[neighbour_2_posn]
neighbour_3_contribution = classes_matrix.iloc[neighbour_3_posn]

recommended_classes_matrix = pd.Series(index=class_names, dtype=object)
recommended_classes_matrix['ID'] = matrix.iloc[8,0]
recommended_classes_matrix['Name'] = matrix.iloc[8,1]
recommended_classes_matrix.fillna(0.0, inplace=True)

for i in range(2,len(recommended_classes_matrix.index)):
    recommended_classes_matrix.iloc[i] += neighbour_1_contribution.iloc[i] * neighbours_similarity_dict[neighbour_1_name]
    recommended_classes_matrix.iloc[i] += neighbour_2_contribution.iloc[i] * neighbours_similarity_dict[neighbour_2_name]
    recommended_classes_matrix.iloc[i] += neighbour_3_contribution.iloc[i] * neighbours_similarity_dict[neighbour_3_name]

recommended_classes_matrix.drop(already_seen_names, inplace=True)
recommended_classes_matrix.sort_values(ascending=False,inplace=True,kind='heapsort')
top_3 = [recommended_classes_matrix.index[0],recommended_classes_matrix.index[1],recommended_classes_matrix.index[2]]

# print(X_test,y_test)
# print(name_dict[y_test.values[0][0]])
# print(neighbours_similarity_dict)
# print(top_3)
