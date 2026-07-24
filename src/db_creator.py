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
        alternate_url text
        )""")

        conn.commit()

        cursor.execute("""CREATE TABLE IF NOT EXISTS area (
        vacancy_id int PRIMARY KEY,
        id int,
        name text,

        CONSTRAINT area_vacancy_fk
        FOREIGN KEY (vacancy_id)
        REFERENCES vacancies(id)
        ON DELETE CASCADE
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS salary (
        vacancy_id int PRIMARY KEY,
        salary_from int,
        salary_to int,
        currency text,
        gross int,

        CONSTRAINT salary_vacancy_fk
        FOREIGN KEY (vacancy_id)
        REFERENCES vacancies(id)
        ON DELETE CASCADE
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS type (
        vacancy_id int PRIMARY KEY,
        id text,
        name text,

        CONSTRAINT type_vacancy_fk
        FOREIGN KEY (vacancy_id)
        REFERENCES vacancies(id)
        ON DELETE CASCADE
        )""")

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

        cursor.execute("""CREATE TABLE IF NOT EXISTS snippet (
        vacancy_id int PRIMARY KEY,
        requirement text,
        responsibility text,

        CONSTRAINT snippet_vacancy_fk
        FOREIGN KEY (vacancy_id)
        REFERENCES vacancies(id)
        ON DELETE CASCADE
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS experience (
        vacancy_id int PRIMARY KEY,
        id text,
        name text,

        CONSTRAINT experience_vacancy_fk
        FOREIGN KEY (vacancy_id)
        REFERENCES vacancies(id)
        ON DELETE CASCADE
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS employment (
        vacancy_id int PRIMARY KEY,
        id text,
        name text,

        CONSTRAINT employment_vacancy_fk
        FOREIGN KEY (vacancy_id)
        REFERENCES vacancies(id)
        ON DELETE CASCADE
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS schedule (
        vacancy_id int PRIMARY KEY,
        id text,
        name text,

        CONSTRAINT schedule_vacancy_fk
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
                cursor.execute(
                    """
                    INSERT INTO vacancies (
                        id,
                        name,
                        published_at,
                        created_at,
                        archived,
                        alternate_url
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        published_at = EXCLUDED.published_at,
                        created_at = EXCLUDED.created_at,
                        archived = EXCLUDED.archived,
                        alternate_url = EXCLUDED.alternate_url
                    """,
                    (
                        int(vac["id"]),
                        vac["name"],
                        vac.get("published_at"),
                        vac.get("created_at"),
                        int(vac.get("archived", 0)),
                        vac.get("alternate_url"),
                    ),
                )

                area = vac.get("area")

                if area is not None:
                    cursor.execute(
                        """
                        INSERT INTO area (
                            vacancy_id,
                            id,
                            name
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT (vacancy_id)
                        DO UPDATE SET
                            id = EXCLUDED.id,
                            name = EXCLUDED.name
                        """,
                        (
                            int(vac["id"]),
                            int(area["id"]),
                            area["name"],
                        ),
                    )

                salary = vac.get("salary")

                if salary is not None:
                    cursor.execute(
                        """
                        INSERT INTO salary (
                            vacancy_id,
                            salary_from,
                            salary_to,
                            currency,
                            gross
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (vacancy_id)
                        DO UPDATE SET
                            salary_from = EXCLUDED.salary_from,
                            salary_to = EXCLUDED.salary_to,
                            currency = EXCLUDED.currency,
                            gross = EXCLUDED.gross
                        """,
                        (
                            int(vac["id"]),
                            salary.get("from"),
                            salary.get("to"),
                            salary.get("currency"),
                            int(salary.get("gross")),
                        ),
                    )

                type_ = vac.get("type")

                if type_ is not None:
                    cursor.execute(
                        """
                        INSERT INTO type (
                            vacancy_id,
                            id,
                            name
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT (vacancy_id)
                        DO UPDATE SET
                            id = EXCLUDED.id,
                            name = EXCLUDED.name
                        """,
                        (int(vac["id"]), type_["id"], type_["name"]),
                    )

                employee = vac.get("employer")

                if employee is not None:
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
                            int(employee["id"]),
                            employee["name"],
                            employee["alternate_url"],
                            int(employee["trusted"]),
                        ),
                    )

                snippet = vac.get("snippet")

                if snippet is not None:
                    cursor.execute(
                        """
                        INSERT INTO snippet (
                        vacancy_id,
                        requirement,
                        responsibility
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT (vacancy_id)
                        DO UPDATE SET
                        requirement = EXCLUDED.requirement,
                        responsibility = EXCLUDED.responsibility
                        """,
                        (int(vac["id"]), snippet["requirement"], snippet["responsibility"]),
                    )

                experience = vac.get("experience")

                if experience is not None:
                    cursor.execute(
                        """
                        INSERT INTO experience (
                        vacancy_id,
                        id,
                        name
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT (vacancy_id)
                        DO UPDATE SET
                        id = EXCLUDED.id,
                        name = EXCLUDED.name
                        """,
                        (int(vac["id"]), experience["id"], experience["name"]),
                    )

                employment = vac.get("employment")

                if employment is not None:
                    cursor.execute(
                        """
                        INSERT INTO employment (
                        vacancy_id,
                        id,
                        name
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT (vacancy_id)
                        DO UPDATE SET
                        id = EXCLUDED.id,
                        name = EXCLUDED.name
                        """,
                        (int(vac["id"]), employment["id"], employment["name"]),
                    )

                schedule = vac.get("schedule")

                if schedule is not None:
                    cursor.execute(
                        """
                        INSERT INTO schedule (
                        vacancy_id,
                        id,
                        name
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT (vacancy_id)
                        DO UPDATE SET
                        id = EXCLUDED.id,
                        name = EXCLUDED.name
                        """,
                        (int(vac["id"]), schedule["id"], schedule["name"]),
                    )
