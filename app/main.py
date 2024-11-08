import csv
import os
import pyuca


DEFAULT_GRADES_DIR = "grades"
DEFAULT_CLASSES_DIR = "classes"


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
    eval_grades = dict.fromkeys(names, 0.0)
    is_finished = dict.fromkeys(names, False)

    grade_file_path = os.path.join(DEFAULT_GRADES_DIR, grade_file)
    check_path_exists(
        grade_file_path,
        f"Grade file {grade_file} not found. Consider creating a file with the grade name in the /grades directory in the root directory of the program.",
    )

    with open(grade_file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)

        next(reader)

        for row in reader:
            if row[0] == "Overall average":
                break

            name = f"{row[0]} {row[1]}"
            finished = row[3] == "Finished"
            in_progress = row[3] == "In progress"

            try:
                eval_grades[name]
            except KeyError as exc:
                raise ValueError(
                    f"Student {name} not found in the class file. Perhaps you've chosen the wrong class."
                ) from exc

            if not finished and is_finished[name]:
                continue

            if finished:
                eval_grades[name] = round_grade(float(row[7]))
                is_finished[name] = True

            if in_progress:
                grade = 0.0

                for i in range(7, len(row)):
                    if row[i] != "-":
                        grade += float(row[i])

                if grade > eval_grades[name]:
                    eval_grades[name] = round_grade(grade)

    return eval_grades


def show_grades_summary(grades: dict, grade_file: str, school_class: str) -> None:
    """
    Display a summary of grades for a given grade file and class.

    Args:
        grades (dict): A dictionary with student names as keys and their grades as values.
        grade_file (str): The name of the grade file.
        school_class (str): The name of the class.
    """
    print(f"{'#' * 10} {grade_file} {'#' * 10}")
    print(f"Class: {school_class}\n")

    for name, grade in grades.items():
        print(f"{grade: <3} {name}")


def ask_to_continue() -> None:
    """
    Prompt the user to press enter to continue.
    """
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
