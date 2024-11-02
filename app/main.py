import csv
import pyuca
import os


DEFAULT_GRADES_DIR = 'grades'
DEFAULT_CLASSES_DIR = 'classes'


def get_valid_integer() -> int:
    while True:
        try:
            return int(input())
        except ValueError:
            print("Please enter a valid integer.")

def get_all_classes() -> list:
    classes = []
    
    if not os.path.exists(DEFAULT_CLASSES_DIR):
        raise FileNotFoundError("Classes directory not found. Consider creating a /classes directory in the root directory of the program.")
    
    if not os.listdir(DEFAULT_CLASSES_DIR):
        raise FileNotFoundError("No class files found. Consider creating a file with the class name in the /classes directory in the root directory of the program.")
    
    for file in os.listdir(DEFAULT_CLASSES_DIR):
        if file.endswith(".txt"):
            classes.append(file[:-4])

    return classes

def choose_class() -> str:
    classes = get_all_classes()

    print("Please select a class for this session:")

    for i, class_name in enumerate(classes, 1):
        print(f"{i}) {class_name}")

    while True:
        class_index = get_valid_integer()

        if class_index < 1 or class_index > len(classes):
            print(f"Please enter a valid class index. It should be between 1 and {len(classes)}.")

            continue

        return classes[class_index - 1]
    
def retrieve_student_names(class_name: str) -> list:
    names = []
    
    if not os.path.exists(DEFAULT_CLASSES_DIR + "/" + class_name + '.txt'):
        raise FileNotFoundError(f"Class file {class_name}.txt not found. Consider creating a file with the class name in the /classes directory in the root directory of the program.")
    
    if not os.listdir(DEFAULT_CLASSES_DIR):
        raise FileNotFoundError("No class files found in the /classes directory. Consider creating a file with the class name in the /classes directory in the root directory of the program.")
    
    with open(DEFAULT_CLASSES_DIR + "/" + class_name + '.txt', newline='', encoding='utf-8') as file:
        for line in file:
            names.append(line.strip())
    
    return names

def fetch_all_grade_files() -> list:
    grade_files = []
    
    if not os.path.exists(DEFAULT_GRADES_DIR):
        raise FileNotFoundError("Grades directory not found. Consider creating a /grades directory in the root directory of the program.")
    
    if not os.listdir(DEFAULT_GRADES_DIR):
        raise FileNotFoundError("No grade files found.")
    
    for file in os.listdir(DEFAULT_GRADES_DIR):
        if file.endswith(".csv"):
            grade_files.append(file)

    return grade_files

def round_grade(grade: float) -> int:
    return int(round(grade, 0))

def evaluate_grades(grade_file: str, names: list) -> dict:
    eval_grades = dict.fromkeys(names, 0.0)
    
    if not os.path.exists(DEFAULT_GRADES_DIR + "/" + grade_file):
        raise FileNotFoundError(f"Grade file {grade_file} not found. Consider creating a file with the grade name in the /grades directory in the root directory of the program.")
    
    print(os.listdir(DEFAULT_GRADES_DIR))
    if not os.listdir(DEFAULT_GRADES_DIR):
        raise FileNotFoundError("No grade files found in the /grades directory.")
    
    with open(DEFAULT_GRADES_DIR + "/" + grade_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        
        next(reader)
        
        for row in reader:
            if row[0] == 'Overall average':
                break
            
            name        = f"{row[0]} {row[1]}"
            finished    = row[3] == 'Finished'
            in_progress = row[3] == 'In progress'
            
            try:
                eval_grades[name]
            except KeyError:
                raise ValueError(f"Student {name} not found in the class file. Perhaps you've chosen the wrong class.")
            
            if not finished and eval_grades[name] != 0.0:
                continue
            
            if finished:
                eval_grades[name] = round_grade(float(row[7]))
                
            if in_progress:
                for i in range(7, len(row)):
                    if row[i] != '-':
                        eval_grades[name] += float(row[i])
                    
                eval_grades[name] = round_grade(eval_grades[name])

    return eval_grades

def show_grades_summary(grades: dict, grade_file: str, school_class: str) -> None:
    print(f"{'#' * 10} {grade_file} {'#' * 10}")
    print(f"Class: {school_class}\n")
    
    for name, grade in grades.items():
        print(f"{grade: <3} {name}")

def ask_to_continue() -> None:
    print("\n> Press enter to continue...")
    input()


if __name__ == "__main__":
    collator = pyuca.Collator()

    school_class = choose_class()
    names = sorted(retrieve_student_names(school_class), key=collator.sort_key)

    for grade_file in fetch_all_grade_files():
        grades = evaluate_grades(grade_file, names)

        show_grades_summary(grades, grade_file, school_class)

        ask_to_continue()
