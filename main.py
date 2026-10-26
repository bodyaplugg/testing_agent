import os
import json

import google.genai as genai
from google.genai import types
from play_test import run_questions

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set")

client = genai.Client(api_key=api_key)

def search_info(topic: str) -> str:
    knowledge = {
        "Python": "Python — об'єктно-орієнтована мова програмування високого рівня.",
        "SQL": "SQL — декларативна мова програмування для взаємодії з реляційними базами даних.",
        "JavaScript": "JavaScript — динамічна мова програмування, яку широко використовують для створення інтерактивних вебсторінок і серверних застосунків.",
        "HTML": "HTML — мова розмітки, що визначає структуру та зміст вебсторінки.",
        "CSS": "CSS — мова стилів для опису зовнішнього вигляду HTML-документів.",
        "API": "API — програмний інтерфейс, через який різні програми обмінюються даними та викликають функції одна одної.",
        "JSON": "JSON — текстовий формат обміну структурованими даними, побудований на об'єктах і масивах.",
        "Git": "Git — розподілена система контролю версій для відстеження змін у файлах і спільної роботи над кодом.",
        "Алгоритм": "Алгоритм — точна послідовність дій для розв'язання задачі.",
        "База даних": "База даних — організована сукупність даних, яку можна зберігати, змінювати та запитувати.",
        "Реляційна база даних": "Реляційна база даних зберігає дані у пов'язаних таблицях, що складаються з рядків і стовпців.",
        "Машинне навчання": "Машинне навчання — метод штучного інтелекту, за якого модель виявляє закономірності в даних і використовує їх для прогнозування.",
        "Штучний інтелект": "Штучний інтелект — галузь інформатики, що створює системи, здатні виконувати завдання, які зазвичай потребують людського інтелекту."
    }
    return knowledge.get(topic, "Інформацію не знайдено. Спирайся на власні знання моделі.")

def _parse_test(test_content: str) -> dict | None:
    try:
        test = json.loads(test_content)
    except json.JSONDecodeError:
        return None

    if (
        not isinstance(test, dict)
        or set(test) != {"questions"}
        or not isinstance(test["questions"], list)
        or not test["questions"]
        or any(
            not isinstance(question, dict)
            or set(question) != {"name", "options", "answer"}
            or not isinstance(question["name"], str)
            or not isinstance(question["options"], list)
            or not question["options"]
            or not all(isinstance(option, str) for option in question["options"])
            or not isinstance(question["answer"], str)
            or question["answer"] not in question["options"]
            for question in test["questions"]
        )
    ):
        return None
    return test

def save_test(test_content: str) -> str:
    test = _parse_test(test_content)
    if test is None:
        return (
            "Помилка: тест має мати формат "
            "{'questions': [{'name': '...', 'options': ['...'], "
            "'answer': '...'}]}."
        )

    tests_dir = "tests"
    os.makedirs(tests_dir, exist_ok=True)

    index = 1
    filename = os.path.join(tests_dir, f"test_{index}.json")
    while os.path.exists(filename):
        index += 1
        filename = os.path.join(tests_dir, f"test_{index}.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(test, f, ensure_ascii=False, indent=2)
    return f"Успіх: Тест збережено у {filename}"

def run_test(test_content: str) -> str:
    test = _parse_test(test_content)
    if test is None:
        return (
            "Помилка: тест має мати формат "
            "{'questions': [{'name': '...', 'options': ['...'], "
            "'answer': '...'}]}."
        )

    try:
        return run_questions(test["questions"])
    except EOFError:
        return "Тестування перервано."

context = """
Ти — асистент, який допомагає користувачам з програмуванням, в тебе є знання з різних мов програмування, баз даних, 
комп'ютерних мереж та штучного інтелекту. Ти можеш надавати пояснення, приклади коду та допомагати вирішувати проблеми. 
Якщо користувач запитує про конкретну тему, ти можеш скористатися інструментом search_info для отримання додаткової 
інформації. Якщо користувач хоче зберегти тест, ти можеш скористатися інструментом save_test.
Відповідай на запити користувача українською мовою.
Інструкція:
- Якщо користувач запитує про конкретну тему, скористайся інструментом search_info для отримання додаткової інформації.
- Якщо користувач хоче зберегти тест, скористайся інструментом save_test.
- Якщо користувач хоче пройти тест без збереження, скористайся інструментом
  run_test і передай йому JSON-рядок із тестом. Цей інструмент не створює файл. 
  Якщо використовуєш run_test, то не потрібно ще кидати цей тест у чат, можеш щось написати на рахунок нього.
- Для save_test та run_test передавай один JSON-об'єкт у вигляді рядка рівно з трьома
  полями: {"questions": [{"name": "...", "options": ["...", "..."], "answer": "..."}...]}.
- Поле name — питання, options — список варіантів відповідей, answer —
  правильна відповідь, яка обов'язково має бути в options.
- Не додавай інші поля у JSON, крім зазначених вище.
- Не обгортуй жодні відповіді у Markdown-блок коду.
- Відповідай на запити користувача українською мовою.
"""

chat = client.chats.create(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        tools=[search_info, save_test, run_test],
        system_instruction=context
    ),
)

print("Чат запущено. Введіть exit або quit для завершення.")

while True:
    try:
        prompt = input("Ви: ").strip()
    except EOFError:
        print()
        break

    if prompt.lower() in {"exit", "quit"}:
        break
    if not prompt:
        continue

    response = chat.send_message(prompt)
    print(f"Асистент: {response.text}")