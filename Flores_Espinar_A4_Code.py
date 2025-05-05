""" 
How to run the code

1. Install packages `pip install -r requirements.txt`
2. run the analysis `python3 Flores_espinar_A3_Code.py`

 """

from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.naive_bayes import CategoricalNB
from sklearn.model_selection import train_test_split

from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt


def get_data():

    column_dict = {
        'Average budget per person when eating out': "budget_eat_out",
        'Average budget per person when ordering takeout/delivery': "budget_takeout",
        'Relationship Status': "relationship_status",
        'Housing type': "housing_type",
        'Preferred Type of Dining': "preferred_dining"
    }
    df = pd.read_csv('Flores_Espinar_FactorsInfluencingDiningChoice.csv', usecols=[*range(1, 19)])
    # df.rename(columns=column_dict, inplace=True)
    print(df.columns) 
    return df

get_data()

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

    # query data
    df= get_data()
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

def knn_classifier():
    # load csv dataset
    df = pd.read_csv('Flores_Espinar_FactorsInfluencingDiningChoice.csv', skiprows=1, header=None)

    # access columns
    relationship_col = df.iloc[:, 3]   # relationship status
    budget_col = df.iloc[:, 12]        # average budget
    dining_col = df.iloc[:, 11]        # preferred dining choice

    # encode relationship status
    relationship = relationship_col.map({'Married': 1, 'Single': 0})

    # bin the average budget into labeled categories
    budget_bins = [0, 375, 750, 1125, 1500]
    budget_labels = ['small', 'medium', 'large', 'very large']
    budget = pd.cut(budget_col, bins=budget_bins, labels=budget_labels, right=True)

    # map dining type to numeric
    dining_map = {
        'Home-Cooked Meals': 0,
        'Food Delivery': 1,
        'Eating out at Casual Dining Restaurants': 2,
        'Eating out at Fine Dining Restaurants': 3,
        'Eating out at Fast Food Restaurant': 4
    }
    dining = dining_col.map(dining_map)

    # drop rows with any missing values
    df_clean = pd.DataFrame({
        'Relationship': relationship,
        'Budget_Label': budget,
        'Dining': dining
    }).dropna()

    # convert budget labels to numeric values for model
    budget_numeric_map = {'small': 0, 'medium': 1, 'large': 2, 'very large': 3}
    df_clean['Budget_Num'] = df_clean['Budget_Label'].map(budget_numeric_map)

    # features and target
    X = df_clean[['Relationship', 'Budget_Num']]
    y = df_clean['Dining']

    # train/test split (70-30%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=142)

    # knn model
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)
    df_clean['Predicted_Dining'] = knn.predict(X)
    inv_dining_map = {v: k for k, v in dining_map.items()}
    result = df_clean.groupby(['Relationship', 'Budget_Label'])['Predicted_Dining']\
                     .agg(lambda x: x.mode()[0]).reset_index()
    result['Predicted_Dining'] = result['Predicted_Dining'].map(inv_dining_map)
    result = result.rename(columns={
        'Relationship': 'Relationship Status (0=Single, 1=Married)',
        'Budget_Label': 'Budget Range',
        'Predicted_Dining': 'Predicted Dining Type'
    })
    print(result)
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        df_clean['Relationship'],
        df_clean['Budget_Num'],
        c=df_clean['Predicted_Dining'],
        cmap='tab10',
        edgecolor='k'
    )
    for i, row in df_clean.iterrows():
        label = inv_dining_map[row['Predicted_Dining']]
        x = row['Relationship']
        y = row['Budget_Num']
        plt.text(x + 0.02, y + 0.05, label, fontsize=6)

    # visualization settings
    plt.xlabel('Relationship Status')
    plt.ylabel('Average Budget Per Person When Eating Out')
    plt.title('kNN Prediction: Dining Preference by Relationship & Budget')
    plt.xticks([0, 1], ['Single (0)', 'Married (1)'])
    plt.yticks([0, 1, 2, 3], ['Small (P0-375)', 'Medium (P376 - 750)', 'Large (P751 - 1125)', 'Very Large (P1126 - 1500)'])
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    return y_test, knn.predict(X_test)

def knn_confusion():
    # load knn test
    y_test, y_pred = knn_classifier()

    label_names = {
        0: 'Home-Cooked Meals',
        1: 'Food Delivery',
        2: 'Casual Dining',
        3: 'Fine Dining',
        4: 'Fast Food'
    }

    # compute confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    present_labels = np.unique(np.concatenate([y_test, y_pred]))
    present_names = [label_names[i] for i in present_labels]
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=present_names)
    disp.plot(xticks_rotation=45)
    plt.title("Confusion Matrix - kNN Classifier")
    plt.tight_layout()
    plt.show()

# naive_bayes_analysis()
# knn_classifier()
# knn_confusion()
