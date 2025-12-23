import sqlite3
from typing import Any, Dict, List

DB_NAME = "database.db"
CREATE_TABLE = "CREATE TABLE IF NOT EXISTS task(id TEXT PRIMARY KEY, title TEXT, content TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)"
INSERT_DATA = "INSERT INTO task(id, title, content) VALUES(?, ?, ?)"
QUERY_ALL_DATA = "SELECT id, title, content, createdAt FROM task ORDER BY createdAt"

class Database:
    def __init__(self):
        self.path = DB_NAME
        self.con = sqlite3.connect(DB_NAME)
        self.cur = self.con.cursor()
        self.cur.execute(CREATE_TABLE)
        self.con.commit()

    def save(self, data: Dict[str, Any]):
        try:
            self.cur.execute(INSERT_DATA, (data["id"], data["title"], data["content"]))
            self.con.commit()
        except Exception as e:
            print(f"Error saving data: {e}")

    def load(self) -> List[Dict[str, Any]]:
        try:
            res = self.cur.execute(QUERY_ALL_DATA)
            rows = res.fetchall()
            return [
                {"id": row[0], "title": row[1], "content": row[2], "createdAt": row[3]}
                for row in rows
            ]
        except Exception as e:
            print(f"Error loading data: {e}")
            return []

    def append(self, data: Dict[str, Any]):
        self.save(data)  # Same as save

    def update(self, data: List[Dict[str, Any]]):
        try:
            values = [(d["id"], d["title"], d["content"]) for d in data]
            self.cur.executemany(INSERT_DATA, values)
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
