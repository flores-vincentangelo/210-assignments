import os
from collections import Counter
import pandas as pd
import numpy as np

from sqlalchemy import create_engine, select, inspect, func
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents, attribute_column_dict

from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.naive_bayes import CategoricalNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def get_data(engine):
    feature_data = []
    label_data = []

    query = select(Respondents.budget_takeout_delivery, Respondents.budget_eat_out, Respondents.relationship_status, Respondents.housing_type, Respondents.preferred_dining)
    with Session(engine) as session:
        for tuple in session.execute(query):
            feature_data.append([tuple[0], tuple[1], tuple[2], tuple[3], tuple[4]])    
            label_data.append(tuple[4])

    columns = ["budget_takeout", "budget_eat_out", "relationship_status", "housing_type", "preffered_dining"]
    df = pd.DataFrame(feature_data, columns=columns)
    # print (df)
    # print(label_data)
    return df, label_data

def bin_numerical_data(X):
    bins = [-np.inf, 375, 750, 1125, 1500]
    labels = ["small", "medium", "large", "very large"]
    X["budget_eat_out"] = pd.cut(X["budget_eat_out"], bins=bins, labels=labels)
    X["budget_takeout"] = pd.cut(X["budget_takeout"], bins=bins, labels=labels)

    X = X[X["budget_eat_out"] != "very large"]
    X = X[X["budget_takeout"] != "very large"]
    return X

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=False)
df, y = get_data(engine)
X_binned = bin_numerical_data(df)

X = X_binned.drop(columns=["preffered_dining"])
y = X_binned['preffered_dining']

label_encoder = LabelEncoder()
feature_encoder = OrdinalEncoder()
X_encoded = feature_encoder.fit_transform(X_binned)
y_encoded = label_encoder.fit_transform(y)
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y_encoded, test_size=0.5)

# X_train_encoded = feature_encoder.transform(X_train)
# X_test_encoded = feature_encoder.transform(X_test)

model = CategoricalNB()
model.fit(X_train, y_train)

if(X_train.shape[1] == X_test.shape[1]):
    # X_test_encoded_list = X_test_encoded.tolist()

    # print(X_test_encoded_list)
    # list = X_test.tolist()
    # list2 = list[0:9]
    # print(list2)
    # print(feature_encoder.inverse_transform(list2))
    y_pred = model.predict(X_test)
    print(y_pred)
    print(y_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
