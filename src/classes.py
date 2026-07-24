from contextlib import closing
from decimal import Decimal

import psycopg2

from src.db_creator import add_data_to_db, create_db_if_not_exist, create_tables_if_not_exist
from src.utils import get_data_from_file

VacancyRow = tuple[
    str,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
    int | None,
    int | None,
    str | None,
]
CompanyVacanciesCount = tuple[str, int]
AverageSalary = tuple[Decimal | None]


class DBManager:
    """Класс работающий с базой данных"""

    def __init__(self, conn_params: dict[str, str]) -> None:
        """Функция инициализации DBManager"""

        self.conn_params = conn_params

        create_db_if_not_exist(self.conn_params)
        create_tables_if_not_exist(self.conn_params)
        add_data_to_db(get_data_from_file("hh_vacancies.json"), self.conn_params)

    def get_companies_and_vacancies_count(self) -> list[CompanyVacanciesCount]:
        """Метод возращающий названия компаний и количество вакансий который они предлагают"""

        with closing(psycopg2.connect(**self.conn_params)) as conn, conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT name, COUNT (*) AS quantity
                    FROM employers
                    GROUP BY name
                    ORDER BY quantity DESC
                    """)
                result: list[CompanyVacanciesCount] = cur.fetchall()
        return result

    def get_all_vacancies(self) -> list[VacancyRow]:
        """Метод возвращающий все вакансии"""
        with closing(psycopg2.connect(**self.conn_params)) as conn, conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                    v.name,
                    v.alternate_url,
                    a.name,
                    e.name,
                    e.alternate_url,
                    em.name,
                    s.salary_from,
                    s.salary_to,
                    sp.requirement

                    FROM vacancies as v
                    JOIN area as a
                        ON v.id = a.vacancy_id
                    JOIN employers as e
                        ON v.id = e.vacancy_id
                    JOIN employment as em
                        ON v.id = em.vacancy_id
                    JOIN salary as s
                        ON v.id = s.vacancy_id
                    JOIN snippet as sp
                        ON v.id = sp.vacancy_id
                    """)
                result: list[VacancyRow] = cur.fetchall()
        return result

    def get_avg_salary(self) -> list[AverageSalary]:
        """Метод возвращающий среднюю зарплату на рынке среди всех вакансий"""
        with closing(psycopg2.connect(**self.conn_params)) as conn, conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT AVG((salary_from + salary_to) / 2) as avg_salary
                    FROM salary
                    WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
                    """)
                result: list[AverageSalary] = cur.fetchall()
        return result

    def get_vacancies_with_higher_salary(self) -> list[VacancyRow]:
        """Метод возвращающий вакансии с зарплатой выше средней по рынку"""
        avg_salary = self.get_avg_salary()[0][0]
        if avg_salary is None:
            return []

        with closing(psycopg2.connect(**self.conn_params)) as conn, conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                    v.name,
                    v.alternate_url,
                    a.name,
                    e.name,
                    e.alternate_url,
                    em.name,
                    s.salary_from,
                    s.salary_to,
                    sp.requirement

                    FROM vacancies as v
                    JOIN area as a
                        ON v.id = a.vacancy_id
                    JOIN employers as e
                        ON v.id = e.vacancy_id
                    JOIN employment as em
                        ON v.id = em.vacancy_id
                    JOIN salary as s
                        ON v.id = s.vacancy_id
                    JOIN snippet as sp
                        ON v.id = sp.vacancy_id

                    WHERE ((s.salary_from + s.salary_to) / 2) > %s
                    ORDER BY v.id
                    """,
                    (avg_salary,),
                )
                result: list[VacancyRow] = cur.fetchall()
        return result

    def get_vacancies_with_keyword(self, key_word: str) -> list[VacancyRow]:
        """Метод показывает вакансии отсортированные по ключевому слову"""
        with closing(psycopg2.connect(**self.conn_params)) as conn, conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                    v.name,
                    v.alternate_url,
                    a.name,
                    e.name,
                    e.alternate_url,
                    em.name,
                    s.salary_from,
                    s.salary_to,
                    sp.requirement

                    FROM vacancies as v
                    JOIN area as a
                        ON v.id = a.vacancy_id
                    JOIN employers as e
                        ON v.id = e.vacancy_id
                    JOIN employment as em
                        ON v.id = em.vacancy_id
                    JOIN salary as s
                        ON v.id = s.vacancy_id
                    JOIN snippet as sp
                        ON v.id = sp.vacancy_id
                    WHERE v.name ILIKE %s
                    """,
                    (f"%{key_word}%",),
                )
                result: list[VacancyRow] = cur.fetchall()

        return result
