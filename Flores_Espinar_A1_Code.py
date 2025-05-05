""" 
How to run the code

1. Install packages `pip install -r requirements.txt`
2. Setup DB `python3 setupDb.py`
3. run the analysis `python3 Flores_espinar_A2_code.py`

 """

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dataETL.dataModel import Respondents, attribute_column_dict
from tabulate import tabulate
from scipy import stats
from scipy.stats import chi2_contingency
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, select, inspect, func
from sqlalchemy.orm import Session

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=False)

def get_data(engine, numerical_attribute_list):

    numerical_attribute_dict = {}

    for item in numerical_attribute_list:
        numerical_attribute_dict[item] = []

    # use sqlalchemy ORM to run query
    with Session(engine) as session:
        # selecting all respondents
        query = select(Respondents)
        for respondent in session.scalars(query):
            numerical_attribute_dict["age"].append(respondent.age)
            numerical_attribute_dict["household_size"].append(respondent.household_size)
            numerical_attribute_dict["budget_eat_out"].append(respondent.budget_eat_out)
            numerical_attribute_dict["budget_takeout_delivery"].append(respondent.budget_takeout_delivery)
            numerical_attribute_dict["grocery_cost"].append(respondent.grocery_cost)
    return numerical_attribute_dict

def pearsons_correlation(data_dict):
    numerical_attribute_dict = data_dict
    
    # this dictionary is to log which pair of analyses have been done
    pearsons_dict = {}

    # list of all analyses
    pearsons_list = []

    # loop through twice to get each pair of correlation
    for attr1 in numerical_attribute_dict.keys():
        pearsons_dict[attr1] = {}
        for attr2 in numerical_attribute_dict.keys():
            # skip getting of correlation when attributes are the same
            if attr1 == attr2:
                continue
            
            # this condition is to prevent computing the same pair of attributes twice.
            # ex. age household_size <==> household_size age
            elif attr2 in pearsons_dict:
                continue;
            
            # get pearson correlation using scipy library
            res = stats.pearsonr(numerical_attribute_dict[attr1], numerical_attribute_dict[attr2])
            pearsons_dict[attr1][attr2] = round(res.statistic, 2)
            pearsons_list.append({
                "attributes": [{
                    "name": attr1,
                    "values": data_dict[attr1]
                }, {
                    "name": attr2,
                    "values": data_dict[attr2]
                }],
                "statistic": round(res.statistic, 2)
            })

    return pearsons_list

def get_cat_attr_combinations(engine, categorical_attributes_list):

    # This method assembles the dictionary for all combinations of categorical attributes
    # and the set of all categorical values used in each of the columns.
    # The method returns a dictionary of all combinations of categorical attributes and their values 
    # and initializes their counts to 0. 
    # An example using "gender" and "relationship_status" is shown below:
    """ 
    {
        "gender": {
            "relationship_status": {
                "Female": {
                    "Married": 0,
                    "Married but not living together": 0,
                    "Single": 0
                },
                "Male": {
                    "Married": 0,
                    "Married but not living together": 0,
                    "Single": 0
                }
            },
            "employment_status": {...},
            "pet_ownership": {...},
            ...
        },
        "relationship_status": {...},
        ...  
    }
     """
    categorical_attr_dict = {}
    column_attr_values_dict = {}

    # get metadata of "Respondents" table
    mapper = inspect(Respondents)

    # get all unique categorical value found for each attribute/column of the table
    # this is done by selecting the columnn and grouping by itself, therefore getting all unique values.
    # "mapper.attrs" gets all column entities of the "Respondents" table
    for column_attr in mapper.attrs:
        if column_attr.key not in categorical_attributes_list:
            continue

        column_attr_values_dict[column_attr.key] = []

        with Session(engine) as session:
            # grouping query
            query = select(column_attr).group_by(column_attr)
            for result_tuple in session.execute(query):
                column_attr_values_dict[column_attr.key].append(result_tuple[0])
    
    # assembly of categorical attribute dictionary
    for attr1 in column_attr_values_dict.keys():
        categorical_attr_dict[attr1] = {}
        for attr2 in column_attr_values_dict.keys():
            
            # skip getting of correlation when attributes are the same
            if attr1 == attr2:
                continue

            # this condition is to prevent computing the same pair of attributes twice.
            # ex. "gender" "relationship_status" <==> "relationship_status" "gender" 
            if attr2 in categorical_attr_dict:
                continue

            categorical_attr_dict[attr1][attr2] = {}

            for value1 in column_attr_values_dict[attr1]:
                categorical_attr_dict[attr1][attr2][value1] = {}
                for value2 in column_attr_values_dict[attr2]:
                    categorical_attr_dict[attr1][attr2][value1][value2] = 0

    return categorical_attr_dict

def get_counts(engine, categorical_attributes_list, categorical_attr_dict):
    
    # this method gets the values for each combination of values for each combination of attributes
    # assembling the dictionary must be done first because the query below omits groupings where their value is 0

    mapper = inspect(Respondents)
    for column_attr in mapper.attrs:
        for column_attr2 in mapper.attrs:
            if column_attr.key not in categorical_attributes_list or column_attr2.key not in categorical_attributes_list:
                continue
            
            if column_attr.key == column_attr2.key:
                continue

            if column_attr2.key not in categorical_attr_dict[column_attr.key]:
                continue

            group_by_query = select(column_attr, column_attr2, func.count(column_attr).label("count")).group_by(column_attr).group_by(column_attr2)
            with Session(engine) as session:
                for result_tuple in session.execute(group_by_query):
                    categorical_attr_dict[column_attr.key][column_attr2.key][result_tuple[0]][result_tuple[1]] = result_tuple[2]
    
    return categorical_attr_dict

def chi_square(array):
    critical_value_dict = {
        1:3.841  ,
        2:  5.991,
        3:  7.815,
        4:  9.488,
        5: 11.070,
        6: 12.592,
        7: 14.067,
        8: 15.507,
        9: 16.919,
        10: 18.307,
        11: 19.675,
        12: 21.026,
        13: 22.362,
        14: 23.685,
        15: 24.996,
        16: 26.296,
        17: 27.587,
        18: 28.869,
        19: 30.144,
        20: 31.410,
        21: 32.671,
        22: 33.924,
        23: 35.172,
        24: 36.415,
        25: 37.652,
        26: 38.885,
        27: 40.113,
        28: 41.337,
        29: 42.557,
        30: 43.773,
        31: 44.985,
        32: 46.194,
        33: 47.400,
        34: 48.602,
        35: 49.802,
        36: 50.998,
        37: 52.192,
        38: 53.384,
        39: 54.572,
        40: 55.758,
        41: 56.942,
        42: 58.124,
        43: 59.304,
        44: 60.481,
        45: 61.656,
        46: 62.830,
        47: 64.001,
        48: 65.171,
        49: 66.339,
        50: 67.505,
        51: 68.669,
        52: 69.832,
        53: 70.993,
        54: 72.153,
        55: 73.311,
        56: 74.468,
        57: 75.624,
        58: 76.778,
        59: 77.931,
        60: 79.082,
        61: 80.232,
        62: 81.381,
        63: 82.529,
        64: 83.675,
        65: 84.821,
        66: 85.965,
        67: 87.108,
        68: 88.250,
        69: 89.391,
        70: 90.531,
        71: 91.670,
        72: 92.808,
        73: 93.945,
        74: 95.081,
        75: 96.217,
        76: 97.351,
        77: 98.484,
        78: 99.617,
        79:100.749,
        80:101.879,
        81:103.010,
        82:104.139,
        83:105.267,
        84:106.395,
        85:107.522,
        86:108.648,
        87:109.773,
        88:110.898,
        89:112.022,
        90:113.145,
        91:114.268,
        92:115.390,
        93:116.511,
        94:117.632,
        95:118.752,
        96:119.871,
        97:120.990,
        98:122.108,
        99:123.225,
        100:124.342, 
    }

    obs = np.array(array)
    res = chi2_contingency(obs, correction=False)
    res.pvalue
    res.expected_freq
    null_hypothesis = ''
    if res.statistic > critical_value_dict[res.dof]:
        null_hypothesis = 'Reject. Values related'
    else:
        null_hypothesis = 'Accept. Values unrelated'

    return tuple((
        res.statistic,
        res.dof,
        critical_value_dict[res.dof],
        null_hypothesis,
        obs,
        res.expected_freq
    ))

def chi_square_analysis(categorical_attr_dict):

    # do the chi square analysis for each pair of attributes
    attr_chi_square_list = []

    for attr1 in categorical_attr_dict.keys():  
        if len(categorical_attr_dict[attr1].keys()) == 0:
            continue
        for attr2 in categorical_attr_dict[attr1].keys():
            
            # assembling the list of lists for the chi_square method
            chi_square_list = []
            for attr1_values in categorical_attr_dict[attr1][attr2].keys():
                value2_list = []
                for attr2_values in categorical_attr_dict[attr1][attr2][attr1_values].keys():
                    value2_list.append(categorical_attr_dict[attr1][attr2][attr1_values][attr2_values])
                
                chi_square_list.append(value2_list)
            
            # chi square analysis
            (statistic, dof, critical_value, null_hypothesis, obs, expected_freq) = chi_square(chi_square_list)

            attr_chi_square_list.append({
                "attributes": [attr1, attr2],
                "dof": dof,
                "critical_value": critical_value,
                "statistic": round(statistic, 5),
                "null_hypothesis": null_hypothesis,
                "x_axis":list(categorical_attr_dict[attr1][attr2][attr1_values].keys()),
                "y_axis":list(categorical_attr_dict[attr1][attr2].keys()),
                "obs": obs.tolist(),
                "expected": expected_freq.tolist()
            })
    
    return attr_chi_square_list

def pretty_print_pearsons(pearsons_list, to_csv=False, filepath=None):
    f = open(filepath, "w") if to_csv else None
    table = []
    header_list = ["Attribute 1","Attribute 2","Correlation Coefficient","Rank"]
    table.append(header_list)
    if to_csv:
        f.write(f"{','.join(header_list)}\n")
    count = 1
    for obj in pearsons_list:
        attr1 = obj["attributes"][0]
        attr2 = obj["attributes"][1]
        row = [attribute_column_dict[attr1["name"]],attribute_column_dict[attr2["name"]],obj["statistic"],count]
        table.append(row)
        if to_csv:
            f.write(f"{','.join(str(x) for x in row)}\n")
        count += 1
    print("\n\n================ PEARSON'S CORRELATION ANALYSIS ================\n")
    print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))
    if to_csv:
        f.close()

def pretty_print_chi_square(chi_square_list, to_csv=False):
    f = open("chi_square_list.csv", "w") if to_csv else None
    table = []
    header_list = ["Attribute 1","Attribute 2","Degrees of Freedom","Critical Value","Correlation Coefficient","Null Hypothesis"]
    table.append(header_list)
    if to_csv:
        f.write(f"{','.join(header_list)}\n")
    for obj in chi_square_list:
        attr1 = obj["attributes"][0]
        attr2 = obj["attributes"][1]
        row = [attribute_column_dict[attr1], attribute_column_dict[attr2], obj["dof"], obj["critical_value"], obj["statistic"], obj["null_hypothesis"]]
        table.append(row)
        if to_csv:
            f.write(f"{','.join(row)}\n")
    print("\n\n================ CHI SQUARE CORRELATION ANALYSIS ================\n")
    print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))
    if to_csv:
        f.close()

def sort_by_statistic(obj):
    return obj["statistic"]

def sort_by_statistic_abs(obj):
    return abs(obj["statistic"])

def sort_by_null_hypothesis(obj):
    return obj["null_hypothesis"]

# function to compute correlation coefficients
def compute_correlation(engine):
    categorical_attributes_list = [
            "gender",
            "relationship_status",
            "employment_status",
            "pet_ownership",
            "housing_type",
            "primary_cook",
            "preferred_dining",
        ]

    numerical_attribute_list = [
        "age",
        "household_size",
        "budget_eat_out",
        "budget_takeout_delivery",
        "grocery_cost",
    ]

    try:

        # read numerical attribute data from database
        numerical_data_dict = get_data(engine, numerical_attribute_list)
        # compute correlations
        pearsons_list = pearsons_correlation(numerical_data_dict)
        # sort attribute pairs according to correlation, rank 1 being the largest correlation factor
        pearsons_list.sort(key=sort_by_statistic_abs, reverse=True)
        # print to console
        pretty_print_pearsons(pearsons_list)

        # prepare dictionary of combinations of categorical attribute values 
        # and corresponding combination of values
        categorical_attr_dict = get_cat_attr_combinations(engine, categorical_attributes_list)
        # get counts for each combination
        categorical_attr_dict = get_counts(engine, categorical_attributes_list, categorical_attr_dict)
        # compute correlation
        chi_square_list = chi_square_analysis(categorical_attr_dict)
        # sort by statistic then sort by null hypothesis
        chi_square_list.sort(key=sort_by_statistic, reverse=True)
        chi_square_list.sort(key=sort_by_null_hypothesis, reverse=True)
        # print to console
        pretty_print_chi_square(chi_square_list)

    except Exception as e:
        print(f"An error occurred: {e}")

# perform k-means clustering 
def display_clusters(csv_file, n_clusters=3):
    # load dataset, consider only numerical columns
    df = pd.read_csv(csv_file, skiprows=0, usecols=[2, 9, 12, 13, 14]) 

    corr_matrix = df.corr(method='pearson')  # compute correlation matrix
    np.fill_diagonal(corr_matrix.values, 0)  # remove self-correlation

    # display correlation values
    short_names = {col: col[:5] for col in df.columns} # shorten column names
    corr_matrix.rename(index=short_names, columns=short_names, inplace=True)
    print(corr_matrix)
    
    # get the most correlated pair
    strongest_pair = np.unravel_index(np.argmax(corr_matrix.values), corr_matrix.shape)
    attr1, attr2 = df.columns[list(strongest_pair)]
    print(f"Using attributes: {attr1} and {attr2} for k-Means clustering.")
    data = df[[attr1, attr2]].dropna()
    
    # standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    # perform clustering
    kmeans = KMeans(n_clusters=n_clusters, n_init=10)
    data['Cluster'] = kmeans.fit_predict(scaled_data)
    
    # visualize the clusters
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=data[attr1], y=data[attr2], hue=data['Cluster'], palette='viridis')
    plt.xlabel(attr1)
    plt.ylabel(attr2)
    plt.title('k-Means Clustering')
    plt.show()
    
    return data

compute_correlation(engine)
# perform k-means clustering 
# display_clusters('Flores_Espinar_FactorsInfluencingDiningChoice.csv', n_clusters=3)