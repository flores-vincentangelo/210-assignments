import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpmax, fpgrowth, association_rules

dataset = [['Milk', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
           ['Dill', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
           ['Milk', 'Apple', 'Kidney Beans', 'Eggs'],
           ['Milk', 'Unicorn', 'Corn', 'Kidney Beans', 'Yogurt'],
           ['Corn', 'Onion', 'Onion', 'Kidney Beans', 'Ice cream', 'Eggs']]

dataset2 = [
    ['A', 'C', 'D'],
    ['B', 'C', 'E'],
    ['A', 'B', 'C', 'E'],
    ['B', 'E']
]

dataset3 = [
    [1, 2, 3, 4],
    [2, 5],
    [1,2,3,5],
    [2,5]
]

def aprioriAssociationRules(dataset, min_support, confidence_threshold):
    te = TransactionEncoder()
    te_ary = te.fit(dataset).transform(dataset)
    df = pd.DataFrame(te_ary, columns = te.columns_)
    # print(df)
    frequent_itemsets = apriori(df, min_support, use_colnames=True)
    print(frequent_itemsets)
    print("\n")
    print(association_rules(frequent_itemsets, metric="confidence", min_threshold=confidence_threshold, return_metrics=['certainty']))
    print("\n")
    
aprioriAssociationRules(dataset2, 0.5, 0.7)
aprioriAssociationRules(dataset3, 0.5, 0.8)