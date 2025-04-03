import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# function to compute correlation coefficient
def compute_correlation(csv_file):
    try:
    	# import the csv file
        df = pd.read_csv(csv_file, skiprows=0, usecols=[2, 9, 12])

        # compute the pearson correlation coefficient
        correlation = df.corr(method='pearson')

        correlation1 = correlation.iloc[0, 1] # correlation of age and household size
        correlation2 = correlation.iloc[0, 2] # correlation of age and average budget per person when eating out

        print(correlation1)
        print(correlation2)

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
# compute_correlation('Flores_Espinar_FactorsInfluencingDiningChoice_Cleaned.csv')
clustered_data = display_clusters('Flores_Espinar_FactorsInfluencingDiningChoice.csv', n_clusters=6)