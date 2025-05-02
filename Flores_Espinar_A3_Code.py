import os
from collections import Counter
import pandas as pd
import numpy as np

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents

from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.naive_bayes import CategoricalNB
from sklearn.model_selection import train_test_split


def get_data(engine):
    feature_data = []
    label_data = []

    query = select(Respondents.budget_takeout_delivery, Respondents.budget_eat_out, Respondents.relationship_status, Respondents.housing_type, Respondents.preferred_dining)
    with Session(engine) as session:
        for tuple in session.execute(query):
            feature_data.append([tuple[0], tuple[1], tuple[2], tuple[3], tuple[4]])    
            label_data.append(tuple[4])

    columns = ["budget_takeout", "budget_eat_out", "relationship_status", "housing_type", "preferred_dining"]
    df = pd.DataFrame(feature_data, columns=columns)
    return df, label_data

def bin_and_remove_outliers(X):
    bins = [-np.inf, 375, 750, 1125, 1500]
    labels = ["small", "medium", "large", "very large"]
    X["budget_eat_out"] = pd.cut(X["budget_eat_out"], bins=bins, labels=labels)
    X["budget_takeout"] = pd.cut(X["budget_takeout"], bins=bins, labels=labels)

    X = X[X["budget_eat_out"] != "very large"]
    X = X[X["budget_takeout"] != "very large"]
    return X

def train_naive_bayes_model(X_train, y_train):
    model = CategoricalNB()
    model.fit(X_train, y_train)
    return model

def get_class_probabilities(y):
    counts = Counter(y)
    total_count = len(y)
    class_probabilities = {value: count / total_count for value, count in counts.items()}
    return counts, class_probabilities 

def get_step_by_step(df, feature_encoder, class_counts, class_probabilities, array):
    test_array = feature_encoder.inverse_transform(array)
    print(array[0])
    print(f"Test {test_array[0]}")
    column_dict = {
        0: "budget_takeout", 
        1: "budget_eat_out", 
        2: "relationship_status", 
        3: "housing_type"
    }
    prob_dict = {}
    for value, class_count in class_counts.items():
        print(f"{value} {class_count} {round(class_probabilities[value], 2)}")
        p_x_c = 1
        for index, feature in enumerate(test_array[0]):
            feature_count = df[ (df['preferred_dining'] == value) & (df[column_dict[index]] == feature)]['preferred_dining'].count()
            feature_prob = feature_count / class_count
            print(f"preffered dining is {value} and {column_dict[index]} is {feature} count is {feature_count} probability {round(feature_prob, 2)}")
            p_x_c *= feature_prob
        
        print (f"p_x_c {round(p_x_c, 5)}")
        prob = class_probabilities[value] * p_x_c
        print(f"probability of {value} given {array} {round(prob, 5)}\n")
        prob_dict[value] = prob
    print(f"highest probability {max(prob_dict.values())}")

def naive_bayes_analysis():

    # create sqlalchemy orm engine for querying data
    engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=False)
    # query data
    df, y = get_data(engine)
    # bin data and remove outliers
    X_binned = bin_and_remove_outliers(df)
    # remove class column from dataset
    X = X_binned.drop(columns=["preferred_dining"])
    y = X_binned['preferred_dining']
    # initialize encoders to encode categorical data
    label_encoder = LabelEncoder()
    feature_encoder = OrdinalEncoder()
    X_encoded = feature_encoder.fit_transform(X)
    y_encoded = label_encoder.fit_transform(y)
    # split the data for training and testing
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y_encoded, test_size=0.3, random_state=762)
    # train the model
    model = train_naive_bayes_model(X_train, y_train)
    y_pred = model.predict(X_test)
    class_counts, class_probabilities = get_class_probabilities(y)
    
    # uncomment below to get individual probabilities for one of the test results
    # get_step_by_step(df, feature_encoder, class_counts, class_probabilities, [X_test[0].tolist()])

naive_bayes_analysis()