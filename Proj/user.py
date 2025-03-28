import sqlite3
from config import db_name


def create_table() -> None:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    request = """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        role TEXT NOT NULL
    )
    """
    cursor.execute(request)
    conn.commit()
    conn.close()


create_table()


class User:
    def __init__(self, user_id, role):
        self.user_id: int = user_id
        self.role: str = role

    def add_user(user_id: int, role: str):
        """
        Функция добавления пользователя в бд, принимает user_id и role,
        возвращает объект класса, либо None при ошибке
        """
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            request = "INSERT INTO users (user_id, role) VALUES (?, ?)"
            cursor.execute(
                request,
                (
                    user_id,
                    role,
                ),
            )
            conn.commit()

            return f"User(user_id={user_id}, role={role})"
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    @staticmethod
    def get_user(user_id: int) -> tuple[int, str]:
        """
        Функция получает на вход user_id пользователя и выводит его роль,
        либо None при отутствии в бд
        """
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            request = "SELECT user_id, role FROM users WHERE user_id = ?"
            cursor.execute(request, (user_id,))
            result = cursor.fetchone()

            return result if result else None
        except sqlite3.OperationalError:
            return "Ошибка подключения к бд"
        finally:
            conn.close()
