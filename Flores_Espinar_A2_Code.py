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
from dataETL.dataModel import Respondents
from tabulate import tabulate
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=False)
analysis_path = "analysis/pearsons"
if not os.path.exists(analysis_path):
    os.makedirs(analysis_path)

def get_data(engine):

    numerical_attribute_dict = {
        "age": [],
        "household_size": [],
        "budget_eat_out": [],
        "budget_takeout_delivery": [],
        "grocery_cost": [],
    }

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
            # ex. age household_size <==> household_size age pair 
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

def pretty_print(pearsons_list, to_csv=False):
    f = open(f"{analysis_path}/pearsons_list.csv", "w") if to_csv else None
    table = []
    table.append(["Attribute 1","Attribute 2","Correlation Coefficient","Rank"])
    if to_csv:
        f.write(f"Attribute 1,Attribute 2,Correlation Coefficient,Rank\n")
    count = 1
    for obj in pearsons_list:
        attr1 = obj["attributes"][0]
        attr2 = obj["attributes"][1]
        if to_csv:
            f.write(f"{attr1["name"]},{attr2["name"]},{obj["statistic"]},{count}\n")
        table.append([attr1["name"],attr2["name"],obj["statistic"],count])
        count += 1
    print("\n\n================ PEARSON'S CORRELATION ANALYSIS ================\n")
    print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))
    if to_csv:
        f.close()

def sorting_function(obj):
    return obj["statistic"]




# function to compute correlation coefficient
def compute_correlation(engine, csv_file):
    try:

        # read data from database
        numerical_data_dict = get_data(engine)
        # compute correlations
        pearsons_list = pearsons_correlation(numerical_data_dict)
        # sort attribute pairs according to correlation, rank 1 being the largest correlation factor
        pearsons_list.sort(key=sorting_function, reverse=True)
        # print to console
        pretty_print(pearsons_list)





    	# import the csv file
        # df = pd.read_csv(csv_file, skiprows=0, usecols=[2, 9, 12])

        # compute the pearson correlation coefficient
        # correlation = df.corr(method='pearson')

        # correlation1 = correlation.iloc[0, 1] # correlation of age and household size
        # correlation2 = correlation.iloc[0, 2] # correlation of age and average budget per person when eating out

        # print(correlation1)
        # print(correlation2)

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def display_clusters(csv_file, n_clusters=3):
    # Load dataset
    df = pd.read_csv(csv_file, skiprows=0, usecols=[2, 9, 12, 13, 14])
    
    # Compute the correlation matrix
    corr_matrix = df.corr(method='pearson')  # Use absolute values for correlation
    np.fill_diagonal(corr_matrix.values, 0)  # Remove self-correlation

    # Display correlation values
    # print("\n=== Correlation Matrix ===")
    short_names = {col: col[:5] for col in df.columns}
    corr_matrix.rename(index=short_names, columns=short_names, inplace=True)

    # Display correlation matrix
    print(corr_matrix)
    
    # Get the most correlated pair
    strongest_pair = np.unravel_index(np.argmax(corr_matrix.values), corr_matrix.shape)
    attr1, attr2 = df.columns[list(strongest_pair)]
    
    print(f"Using attributes: {attr1} and {attr2} for k-Means clustering.")
    
    # Select the two attributes
    data = df[[attr1, attr2]].dropna()
    
    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    # Perform k-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, n_init=10)
    data['Cluster'] = kmeans.fit_predict(scaled_data)
    
    # Visualize the clusters
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=data[attr1], y=data[attr2], hue=data['Cluster'], palette='viridis')
    plt.xlabel(attr1)
    plt.ylabel(attr2)
    plt.title('k-Means Clustering')
    plt.show()
    
    return data

# Example usage
compute_correlation(engine, 'Flores_Espinar_FactorsInfluencingDiningChoice_Cleaned.csv')
# clustered_data = display_clusters('Flores_Espinar_FactorsInfluencingDiningChoice.csv', n_clusters=6)




