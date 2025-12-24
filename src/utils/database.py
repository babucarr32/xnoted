import sqlite3
from src.utils.helpers import slugify
from typing import Any, Dict, List

DB_NAME = "database.db"


def get_create_table(project_name: str):
    return f"CREATE TABLE IF NOT EXISTS {project_name}(id TEXT PRIMARY KEY, title TEXT, content TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)"


def get_insert_data(project_name: str):
    return f"INSERT INTO {project_name}(id, title, content) VALUES(?, ?, ?)"


def get_query_all_data(project_name: str):
    return (
        f"SELECT id, title, content, createdAt FROM {project_name} ORDER BY createdAt"
    )


CREATE_PROJECT_TABLE = "CREATE TABLE IF NOT EXISTS project(id TEXT PRIMARY KEY, title TEXT, description TEXT, type TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)"
INSERT_PROJECT_DATA = (
    "INSERT INTO project(id, title, description, type) VALUES(?, ?, ?, ?)"
)
UPDATE_PROJECT_DATA = (
    "UPDATE project SET title = ?, description = ?, type = ? WHERE id = ?"
)
QUERY_ALL_PROJECT_DATA = (
    "SELECT id, title, description, type, createdAt FROM project ORDER BY createdAt"
)
QUERY_ONE_PROJECT_DATA = (
    "SELECT id, title, description, type, createdAt FROM project WHERE id = ?"
)


class Database:
    def __init__(self):
        self.path = DB_NAME
        self.project_name = "task"
        self.con = sqlite3.connect(DB_NAME)
        self.cur = self.con.cursor()
        self.cur.execute(get_create_table(self.project_name))
        self.cur.execute(CREATE_PROJECT_TABLE)
        self.con.commit()

    def save(self, data: Dict[str, Any]):
        try:
            self.cur.execute(
                get_insert_data(self.project_name),
                (data["id"], data["title"], data["content"]),
            )
            self.con.commit()
        except Exception as e:
            print(f"Error saving data: {e}")

    def save_project(self, data: Dict[str, Any]):
        try:
            self.cur.execute(
                INSERT_PROJECT_DATA,
                (data["id"], data["title"], data["description"], data["type"]),
            )
            self.con.commit()
            # Create new table for the project
            self.cur.execute(get_create_table(slugify(data["title"])))
        except Exception as e:
            print(f"Error saving data: {e}")

    def update_project(self, project_id: str, data: Dict[str, Any]):
        try:
            self.cur.execute(
                UPDATE_PROJECT_DATA,
                (data["title"], data["description"], data["type"], project_id),
            )
            self.con.commit()
        except Exception as e:
            print(f"Error updating project: {e}")

    def load(self) -> List[Dict[str, Any]]:
        try:
            res = self.cur.execute(get_query_all_data(self.project_name))
            rows = res.fetchall()
            return [
                {"id": row[0], "title": row[1], "content": row[2], "createdAt": row[3]}
                for row in rows
            ]
        except Exception as e:
            print(f"Error loading data: {e}")
            return []

    def load_projects(self) -> List[Dict[str, Any]]:
        try:
            res = self.cur.execute(QUERY_ALL_PROJECT_DATA)
            rows = res.fetchall()
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "type": row[3],
                    "createdAt": row[4],
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error loading data: {e}")
            return []

    def get_project(self, project_id: str) -> Dict[str, Any]:
        try:
            self.cur.execute(QUERY_ONE_PROJECT_DATA, (project_id,))
            (id, title, description, project_type, createdAt) = self.cur.fetchone()
            return {
                "id": id,
                "title": title,
                "description": description,
                "type": project_type,
                "createdAt": createdAt,
            }
        except Exception as e:
            print(f"Error loading data: {e}")

    def append(self, data: Dict[str, Any]):
        self.save(data)  # Same as save

    def update(self, data: List[Dict[str, Any]]):
        try:
            values = [(d["id"], d["title"], d["content"]) for d in data]
            self.cur.executemany(get_insert_data(self.project_name), values)
            self.con.commit()
        except Exception as e:
            print(f"Error updating data: {e}")

    def is_storage_exist(self) -> bool:
        return isinstance(self.load(), list)

    def get_last_id(self) -> str:
        todos = self.load()
        if todos:
            return todos[-1]["id"]
        return "0"

    def __del__(self):
        if hasattr(self, "con"):
            self.con.close()
