# Moodle automatic grading system

This is a simple automatic grading system for Moodle. It is designed to be used with the Moodle generated CSV grading files. The system is written in Python and uses the ```csv``` library to manipulate the data.

## How to use

### 1. Download the grading file from Moodle
1. Go to the Moodle course
2. Click on the assignment
3. Click on the "Results/Grades" link
4. Click on the "Download table data as CSV" button

### 2. Download the grading system
1. Clone the repository
2. Create a virtual environment and install the requirements
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
3. Create a folders "grades" and "classes" in the root of the project
4. Create a .txt file with the students' names and save it in the "classes" folder. For example, "10.b.txt":
```
Alice Smith
Bob Brown
Charlie Green
```
5. Move the downloaded grading file to the "grades" folder

### 3. Run the grading system
6. Run the app:
```cmd
python app/main.py
```
7. Follow the instructions