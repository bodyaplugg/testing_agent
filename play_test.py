import json
import sys
from pathlib import Path


TESTS_DIR = Path(__file__).parent / "tests"
TEST_PATTERN = "test_*.json"


def run_questions(questions: list[dict]) -> str:
    correct = 0
    for question_number, question in enumerate(questions, start=1):
        try:
            name = question["name"]
            options = question["options"]
            answer = question["answer"]
            if (
                not isinstance(name, str)
                or not isinstance(options, list)
                or not options
                or not all(isinstance(option, str) for option in options)
                or not isinstance(answer, str)
                or answer not in options
            ):
                raise TypeError("invalid question fields")
        except (KeyError, TypeError):
            print(f"FAIL: invalid question {question_number}")
            continue

        print(f"\n{question_number}. {name}")
        for index, option in enumerate(options, start=1):
            print(f"  {index}. {option}")

        answer_input = input("Ваша відповідь: ").strip()
        if answer_input.isdigit() and 1 <= int(answer_input) <= len(options):
            selected_answer = options[int(answer_input) - 1]
        else:
            selected_answer = answer_input

        if selected_answer == answer:
            print("ПРАВИЛЬНО")
            correct += 1
        else:
            print(f"НЕПРАВИЛЬНО (correct answer: {answer})")

    result = f"Результат: {correct} правильних відповідей з {len(questions)}"
    print(f"\n{result}")
    return result


def run_test(test_path: Path) -> str:
    try:
        with test_path.open(encoding="utf-8") as test_file:
            test = json.load(test_file)

        questions = test["questions"]
        if not isinstance(questions, list) or not questions:
            raise TypeError("'questions' must be a non-empty list")
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"FAIL {test_path.name}: invalid test ({error})")
        return "Тест має некоректний формат."

    return run_questions(questions)


def main() -> int:
    if not TESTS_DIR.is_dir():
        print(f"Tests directory not found: {TESTS_DIR}")
        return 1

    test_paths = sorted(TESTS_DIR.glob(TEST_PATTERN))
    if not test_paths:
        print(f"No tests found in {TESTS_DIR}")
        return 1

    print(f"Знайдено {len(test_paths)} тестів в {TESTS_DIR}")
    try:
        test_number = input("Введіть номер тесту: ").strip()
        if not test_number.isdigit():
            print("Номер тесту має бути цілим числом.")
            return 1

        test_path = TESTS_DIR / f"test_{test_number}.json"
        if not test_path.is_file():
            print(f"Тест не знайдено: {test_path}")
            return 1

        run_test(test_path)
    except EOFError:
        print("\nTest run interrupted.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
