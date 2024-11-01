import csv
from collections import OrderedDict
import pyuca

GRADE_FILE = 'PRG10S8-25-Zarošanās-grades.csv'
CLASS = '10.8'


collator = pyuca.Collator(r".venv\Lib\site-packages\pyuca\allkeys-10.0.0.txt")

names = []
grades = {}

with open("classes/" + CLASS + '.txt', newline='', encoding='utf-8') as f:
    for line in f:
        names.append(line.strip())

names = sorted(names, key=collator.sort_key)

for name in names:
    grades[name] = 0

with open("grades/" + GRADE_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    
    for row in reader:
        name = row[0] + ' ' + row[1]
        finished = row[3] == 'Finished'
        in_progress = row[3] == 'In progress'
        
        if finished:
            grades[name] = int(round(float(row[7]),0))
            
        if in_progress:
            for i in range(7, len(row)):
                if row[i] != '-':
                    grades[name] += float(row[i])
            
            grades[name] = int(round(grades[name], 0))
            
            
for name, grade in grades.items():
    print(grade, name)