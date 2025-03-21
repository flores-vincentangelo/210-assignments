import re

f = open("dataset-cleaned.csv", "r")
line = f.readline()
# for line in f:
#     print(line)

pattern = r',(?=(?:[^"]*"[^"]*")*[^"]*$)'
result = re.split(pattern, line)

print(result)
