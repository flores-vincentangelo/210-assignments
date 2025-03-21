import json

f = open("dataset.csv", "rt")

# for x in f:
#     print(x)

tuple_str = f.readline()
data = json.loads(tuple_str)
print(data)

f.close()

""" 
Health Consciousness: 

1 = Very health conscious
2 = Somewhat health conscious
3 = Not health conscious
"""