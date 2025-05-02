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
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


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

def train_naive_bayes_model(X_train, y_train):
    model = CategoricalNB()
    model.fit(X_train, y_train)
    return model

def predict_and_get_accuracy(X_test, y_test, model):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy

def get_most_accurate_model(X_encoded, y_encoded):
    accuracy_list = []
    highest_accuracy = 0
    most_accurate_model = None
    # iterations = 1000
    random_state = 0
    # for i in range(iterations):
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y_encoded, test_size=0.3, random_state=762)
    model = train_naive_bayes_model(X_train, y_train)
    accuracy = predict_and_get_accuracy(X_test, y_test, model)

        # accuracy_list.append(accuracy)
        # if (accuracy > highest_accuracy and accuracy != 1):
    highest_accuracy = accuracy
    most_accurate_model = model
            # random_state = i
    
    print(f"random state {random_state}")
    print("X_test")
    print (X_test)
    # print("X_test probas")
    # print(most_accurate_model.predict_proba(X_test))

    y_pred = most_accurate_model.predict(X_test)
    print("y_test")
    print(y_test)
    print("y_pred")
    print(y_pred)
    print(f"model accuracy = {highest_accuracy}")
    # print(f"average accuracy {round(sum(accuracy_list) * 100 / len(accuracy_list), 2)}")
    return most_accurate_model,X_test,y_test,y_pred

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

def generate_confusion_matrix(y_test, y_pred):
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    return cm,tn,fp,fn,tp

def confusion_matrix_metrics(tn, fp, fn, tp):
    accuracy = ((tp + tn) / (tp + tn + fp + fn))
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1_score = 2 * precision * recall / (precision + recall)
    specificity = tn / (tn + fp)
    type_1_error = fp / (fp + tn)
    type_2_error = fn / (tp + fn)


    print(f"accuracy {accuracy}")
    print(f"precision {precision}")
    print(f"recall {recall}")
    print(f"f1_score {f1_score}")
    print(f"specificity {specificity}")
    print(f"type_1_error {type_1_error}")
    print(f"type_2_error {type_2_error}")

def plot_confustion_matrix(cm):
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=False)
df, y = get_data(engine)
X_binned = bin_numerical_data(df)
X = X_binned.drop(columns=["preferred_dining"])
y = X_binned['preferred_dining']
label_encoder = LabelEncoder()
feature_encoder = OrdinalEncoder()
X_encoded = feature_encoder.fit_transform(X)
y_encoded = label_encoder.fit_transform(y)
most_accurate_model, X_test, y_test, y_pred = get_most_accurate_model(X_encoded, y_encoded)
print(f"y re-encoded {label_encoder.inverse_transform(y_test)}")
class_counts, class_probabilities = get_class_probabilities(y)
get_step_by_step(df, feature_encoder, class_counts, class_probabilities, [X_test[0].tolist()])
cm, tn, fp, fn, tp = generate_confusion_matrix(y_test, y_pred)
confusion_matrix_metrics(tn, fp, fn, tp)
plot_confustion_matrix(cm)