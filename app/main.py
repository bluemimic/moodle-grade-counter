import csv
import os
import re
import statistics
from datetime import datetime

import pyautogui
import pyuca


DEFAULT_GRADES_DIR = "grades"
DEFAULT_CLASSES_DIR = "classes"

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True


def get_valid_integer() -> int:
    """
    Prompt the user to enter a valid integer. Repeats until a valid integer is entered.

    Returns:
        int: The valid integer entered by the user.
    """
    while True:
        try:
            return int(input())
        except ValueError:
            print("Please enter a valid integer.")


def check_path_exists(path: str, error_message: str) -> None:
    """
    Check if a given path exists. Raises a FileNotFoundError if it does not.

    Args:
        path (str): The path to check.
        error_message (str): The error message to display if the path does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(error_message)


def check_directory_not_empty(directory: str, error_message: str) -> None:
    """
    Check if a given directory is not empty. Raises a FileNotFoundError if it is empty.

    Args:
        directory (str): The directory to check.
        error_message (str): The error message to display if the directory is empty.
    """
    if not os.listdir(directory):
        raise FileNotFoundError(error_message)


def get_all_classes() -> list:
    """
    Retrieve all class names from the classes directory.

    Returns:
        list: A list of class names.
    """
    classes = []

    check_path_exists(
        DEFAULT_CLASSES_DIR,
        "Classes directory not found. Consider creating a /classes directory in the root directory of the program.",
    )
    check_directory_not_empty(
        DEFAULT_CLASSES_DIR,
        "No class files found. Consider creating a file with the class name in the /classes directory in the root directory of the program.",
    )

    for file in os.listdir(DEFAULT_CLASSES_DIR):
        if file.endswith(".txt"):
            classes.append(file[:-4])

    return classes


def choose_class() -> str:
    """
    Prompt the user to select a class from the available classes.

    Returns:
        str: The name of the selected class.
    """
    classes = get_all_classes()

    print("Please select a class for this session:")

    for i, class_name in enumerate(classes, 1):
        print(f"{i}) {class_name}")

    while True:
        class_index = get_valid_integer()

        if class_index < 1 or class_index > len(classes):
            print(
                f"Please enter a valid class index. It should be between 1 and {len(classes)}."
            )

            continue

        return classes[class_index - 1]


def retrieve_student_names(class_name: str) -> list:
    """
    Retrieve the names of students in a given class.

    Args:
        class_name (str): The name of the class.

    Returns:
        list: A list of student names.
    """
    names = []

    class_file_path = os.path.join(DEFAULT_CLASSES_DIR, f"{class_name}.txt")
    check_path_exists(
        class_file_path,
        f"Class file {class_name}.txt not found. Consider creating a file with the class name in the /classes directory in the root directory of the program.",
    )

    with open(class_file_path, newline="", encoding="utf-8") as file:
        for line in file:
            names.append(line.strip())

    return names


def fetch_all_grade_files() -> list:
    """
    Retrieve all grade files from the grades directory.

    Returns:
        list: A list of grade file names.
    """
    grade_files = []

    check_path_exists(
        DEFAULT_GRADES_DIR,
        "Grades directory not found. Consider creating a /grades directory in the root directory of the program.",
    )
    check_directory_not_empty(DEFAULT_GRADES_DIR, "No grade files found.")

    for file in os.listdir(DEFAULT_GRADES_DIR):
        if file.endswith(".csv"):
            grade_files.append(file)

    return grade_files


def round_grade(grade: float) -> int:
    """
    Round a grade to the nearest integer.

    Args:
        grade (float): The grade to round.

    Returns:
        int: The rounded grade.
    """
    return int(round(grade, 0))


def evaluate_grades(grade_file: str, names: list) -> dict:
    """
    Evaluate the grades of students from a given grade file.

    Args:
        grade_file (str): The name of the grade file.
        names (list): A list of student names.

    Returns:
        dict: A dictionary with student names as keys and their evaluated grades as values.
    """
    evaluated_grades = dict.fromkeys(names, 0)
    submission_status = dict.fromkeys(names, False)

    grade_file_path = os.path.join(DEFAULT_GRADES_DIR, grade_file)
    check_path_exists(
        grade_file_path,
        f"Grade file {grade_file} not found. Consider creating a file with the grade name in the /grades directory in the root directory of the program.",
    )

    with open(grade_file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        grade_pattern = re.compile(r"Grade/\d+\.\d+")

        for row in reader:
            if row["Surname"] == "Overall average":
                break

            student_name = f"{row['Surname']} {row['First name']}"
            has_finished = row["State"] == "Finished"
            in_progress = row["State"] == "In progress"

            try:
                evaluated_grades[student_name]

            except KeyError as exc:
                raise ValueError(
                    f"Student {student_name} not found in the class file. Perhaps you've chosen the wrong class."
                ) from exc

            if not has_finished and submission_status[student_name]:
                continue

            if has_finished:
                grade_key = next((key for key in row if grade_pattern.match(key)), None)
                evaluated_grades[student_name] = round_grade(float(row[grade_key]))
                submission_status[student_name] = True

            if in_progress:
                grade = 0

                for key in row:
                    if key.startswith("Q. ") and row[key] != "-":
                        grade += float(row[key])

                if grade > evaluated_grades[student_name]:
                    evaluated_grades[student_name] = round_grade(grade)

    return evaluated_grades


def get_task_date(grade_file: str) -> str:
    """
    Extract the task date from the grade file.

    Args:
        grade_file (str): The name of the grade file.

    Returns:
        str: The task date in a formatted string.
    """
    grade_file_path = os.path.join(DEFAULT_GRADES_DIR, grade_file)
    check_path_exists(
        grade_file_path,
        f"Grade file {grade_file} not found.",
    )

    with open(grade_file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        dates = []

        for row in reader:
            if row["Surname"] == "Overall average":
                break

            if row["State"] == "Finished" or row["State"] == "In progress":
                try:
                    date = datetime.strptime(row["Started on"], "%d %B %Y %I:%M %p")
                    dates.append(date)
                except ValueError:
                    continue

        if dates:
            return min(dates).strftime("%d %B %Y")

        else:
            return "No valid dates found"


def input_grades_to_journal(grades: dict, is_gepd: bool) -> None:
    """
    Input grades into the journaling system using pyautogui.

    Args:
        grades (dict): A dictionary with student names as keys and their grades as values.
    """
    print("\n> Starting to input grades into the journaling system...")

    pyautogui.hotkey("alt", "tab")

    for grade in grades.values():
        to_write = str(grade) + "%" if is_gepd else str(grade)
        pyautogui.typewrite(to_write)
        pyautogui.press("tab")
        
    print("> Finished inputting grades into the journaling system.")


def prompt_grade_input_or_continue(grades: dict) -> None:
    """
    Ask the user if they want to input grades into the journaling system or to continue.

    Args:
        grades (dict): A dictionary with student names as keys and their grades as values.
    """
    while True:
        response = (
            input(
                "\nDo you want to input these grades into the journaling system (1) or to continue (Enter)? "
            )
            .strip()
            .lower()
        )
        if response == "1":
            is_gepd = input("Is this a GEPD? (1/0): ").strip().lower() == "1"
            input_grades_to_journal(grades, is_gepd)
            break

        elif response == "":
            break

        else:
            print("Please enter '1' or 'Enter'.")


def show_grades_summary(
    grades: dict, grade_file: str, school_class: str, task_date: str
) -> None:
    """
    Display a summary of grades for a given grade file and class.

    Args:
        grades (dict): A dictionary with student names as keys and their grades as values.
        grade_file (str): The name of the grade file.
        school_class (str): The name of the class.
        task_date (str): The date of the task.
    """
    task_name = grade_file.split("-")[2]

    print(f"\n{'#' * 10} {grade_file} {'#' * 10}")
    print(f"Class: {school_class}")
    print(f"Task: {task_name}")
    print(f"Date: {task_date}\n")

    grade_values = [grade for grade in grades.values() if grade != 0]
    average_grade = statistics.mean(grade_values)
    median_grade = statistics.median(grade_values)
    mode_grade = statistics.mode(grade_values)
    std_dev_grade = statistics.stdev(grade_values)

    for name, grade in grades.items():
        print(f"{grade: <3} {name}")

    print(f"\nAverage Grade: {average_grade:.2f}")
    print(f"Median Grade: {median_grade:.2f}")
    print(f"Mode Grade: {mode_grade:.2f}")
    print(f"Standard Deviation: {std_dev_grade:.2f}")


if __name__ == "__main__":
    collator = pyuca.Collator()

    school_class = choose_class()
    names = sorted(retrieve_student_names(school_class), key=collator.sort_key)

    for grade_file in fetch_all_grade_files():
        grades = evaluate_grades(grade_file, names)
        date = get_task_date(grade_file)

        show_grades_summary(grades, grade_file, school_class, date)

        prompt_grade_input_or_continue(grades)
