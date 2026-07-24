import os

from dotenv import load_dotenv

from src.classes import DBManager

load_dotenv()


def main() -> None:
    """Основная функция взаимодействия с пользователем"""
    password = os.getenv("DB_PASSWORD")
    if password is None:
        raise RuntimeError("Переменная окружения DB_PASSWORD не задана")

    db_manager = DBManager(
        {
            "host": "localhost",
            "database": "vacancies",
            "user": "postgres",
            "password": password,
        }
    )

    while True:

        print()
        print("=" * 50)
        print("Меню".center(50))
        print("=" * 50)

        print("1. Показать количество предложенных вакансий каждой компанией")
        print("2. Показать все вакансии")
        print("3. Показать среднюю зарплату среди всех вакансий")
        print("4. Показать вакансии с зарплатой выше средней на рынке")
        print("5. Показать вакансии отсортированные по ключевому слову")
        print("0. Выход")

        user_input = input("Введите свой выбор >>> ")
        print()

        if user_input == "1":
            company_counts = db_manager.get_companies_and_vacancies_count()
            for tuple_ in company_counts:
                print(f"{tuple_[0]} - {tuple_[1]}")

        elif user_input == "2":
            all_vacancies = db_manager.get_all_vacancies()
            for vacancy in all_vacancies:
                print(
                    f"Работодатель: {vacancy[3]} {vacancy[4]}\n"
                    f"Вакансия: {vacancy[0]} {vacancy[1]}\n"
                    f"Зарплата: от {vacancy[6]} руб. до {vacancy[7]} руб.\n"
                    f"Местоположение работы: {vacancy[2]}\n"
                    f"Тип Занятости: {vacancy[5]}\n"
                    f"Требования: {vacancy[8]}\n"
                )

        elif user_input == "3":
            avg_salary = db_manager.get_avg_salary()[0][0]
            if avg_salary is None:
                print("Нет вакансий с указанной зарплатой")
            else:
                print(f"Средняя зарплата - {round(avg_salary, 2)} руб.")

        elif user_input == "4":
            higher_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
            for vacancy in higher_salary_vacancies:
                print(
                    f"Работодатель: {vacancy[3]} {vacancy[4]}\n"
                    f"Вакансия: {vacancy[0]} {vacancy[1]}\n"
                    f"Зарплата: от {vacancy[6]} руб. до {vacancy[7]} руб.\n"
                    f"Местоположение работы: {vacancy[2]}\n"
                    f"Тип Занятости: {vacancy[5]}\n"
                    f"Требования: {vacancy[8]}\n"
                )
        elif user_input == "5":
            key_word = input("Введите ключевое слово >>> ")
            print()
            keyword_vacancies = db_manager.get_vacancies_with_keyword(key_word)
            for vacancy in keyword_vacancies:
                print(
                    f"Работодатель: {vacancy[3]} {vacancy[4]}\n"
                    f"Вакансия: {vacancy[0]} {vacancy[1]}\n"
                    f"Зарплата: от {vacancy[6]} руб. до {vacancy[7]} руб.\n"
                    f"Местоположение работы: {vacancy[2]}\n"
                    f"Тип Занятости: {vacancy[5]}\n"
                    f"Требования: {vacancy[8]}\n"
                )

        elif user_input == "0":
            break

        else:
            print("\nНе верный ввод!!!\n")


if __name__ == "__main__":
    main()
