import os
from contextlib import closing

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def create_db_if_not_exist(conn_params: dict) -> None:
    """
    Создает базу данных если ее не существует
    """

    try:
        with closing(psycopg2.connect(**conn_params)):
            pass

    except UnicodeDecodeError:

        password = os.getenv("DB_PASSWORD")

        with closing(
            psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password=password,
            )
        ) as base_conn:
            base_conn.autocommit = True

            with base_conn.cursor() as cursor:
                cursor.execute("CREATE DATABASE vacancies")


def create_tables_if_not_exist(conn_params: dict) -> None:
    """
    Создает таблицы если их не существует
    """

    with (
        closing(psycopg2.connect(**conn_params)) as conn,
        conn,
        conn.cursor() as cursor,
    ):
        cursor.execute("""CREATE TABLE IF NOT EXISTS vacancies (
        id int PRIMARY KEY,
        name text,
        published_at date,
        created_at date,
        archived int,
        alternate_url text,
        area_id int,
        area_name text,
        salary_from int,
        salary_to int,
        salary_currency text,
        salary_gross int,
        type_id text,
        type_name text,
        requirement text,
        responsibility text,
        experience_id text,
        experience_name text,
        employment_id text,
        employment_name text,
        schedule_id text,
        schedule_name text
        )""")
        conn.commit()

        cursor.execute("""CREATE TABLE IF NOT EXISTS employers (
        vacancy_id int PRIMARY KEY,
        id int,
        name text,
        alternate_url text,
        trusted int,

        CONSTRAINT employers_vacancy_fk
        FOREIGN KEY (vacancy_id)
        REFERENCES vacancies(id)
        ON DELETE CASCADE
        )""")
        conn.commit()


def add_data_to_db(data: dict, conn_params: dict) -> None:
    """
    Заносит в базу данных вакансии
    """

    with (
        closing(psycopg2.connect(**conn_params)) as conn,
        conn.cursor() as cursor,
    ):
        for vac in data["items"]:
            with conn:
                area = vac.get("area") or {}
                salary = vac.get("salary") or {}
                type_ = vac.get("type") or {}
                snippet = vac.get("snippet") or {}
                experience = vac.get("experience") or {}
                employment = vac.get("employment") or {}
                schedule = vac.get("schedule") or {}
                employer = vac.get("employer")

                cursor.execute(
                    """
                    INSERT INTO vacancies (
                        id,
                        name,
                        published_at,
                        created_at,
                        archived,
                        alternate_url,
                        area_id,
                        area_name,
                        salary_from,
                        salary_to,
                        salary_currency,
                        salary_gross,
                        type_id,
                        type_name,
                        requirement,
                        responsibility,
                        experience_id,
                        experience_name,
                        employment_id,
                        employment_name,
                        schedule_id,
                        schedule_name
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        published_at = EXCLUDED.published_at,
                        created_at = EXCLUDED.created_at,
                        archived = EXCLUDED.archived,
                        alternate_url = EXCLUDED.alternate_url,
                        area_id = EXCLUDED.area_id,
                        area_name = EXCLUDED.area_name,
                        salary_from = EXCLUDED.salary_from,
                        salary_to = EXCLUDED.salary_to,
                        salary_currency = EXCLUDED.salary_currency,
                        salary_gross = EXCLUDED.salary_gross,
                        type_id = EXCLUDED.type_id,
                        type_name = EXCLUDED.type_name,
                        requirement = EXCLUDED.requirement,
                        responsibility = EXCLUDED.responsibility,
                        experience_id = EXCLUDED.experience_id,
                        experience_name = EXCLUDED.experience_name,
                        employment_id = EXCLUDED.employment_id,
                        employment_name = EXCLUDED.employment_name,
                        schedule_id = EXCLUDED.schedule_id,
                        schedule_name = EXCLUDED.schedule_name
                    """,
                    (
                        int(vac["id"]),
                        vac["name"],
                        vac.get("published_at"),
                        vac.get("created_at"),
                        int(vac.get("archived", 0)),
                        vac.get("alternate_url"),
                        int(area["id"]),
                        area.get("name"),
                        int(salary["from"]),
                        int(salary["to"]),
                        salary.get("currency"),
                        int(salary["gross"]),
                        type_.get("id"),
                        type_.get("name"),
                        snippet.get("requirement"),
                        snippet.get("responsibility"),
                        experience.get("id"),
                        experience.get("name"),
                        employment.get("id"),
                        employment.get("name"),
                        schedule.get("id"),
                        schedule.get("name"),
                    ),
                )

                if employer is not None:
                    cursor.execute(
                        """
                        INSERT INTO employers (
                        vacancy_id,
                        id,
                        name,
                        alternate_url,
                        trusted
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (vacancy_id)
                        DO UPDATE SET
                        id = EXCLUDED.id,
                        name = EXCLUDED.name,
                        alternate_url = EXCLUDED.alternate_url,
                        trusted = EXCLUDED.trusted
                        """,
                        (
                            int(vac["id"]),
                            int(employer["id"]),
                            employer["name"],
                            employer.get("alternate_url"),
                            int(employer["trusted"]),
                        ),
                    )
