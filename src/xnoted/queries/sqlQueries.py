CREATE_TASK_TABLE = """
CREATE TABLE IF NOT EXISTS task(
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT,
    content TEXT,
    is_protected INTEGER DEFAULT 0,
    status INTEGER DEFAULT 0,
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id)
)
"""

CREATE_ACCOUNT_TABLE = """
CREATE TABLE IF NOT EXISTS account(
    id INTEGER PRIMARY KEY CHECK (id = 1),
    password TEXT NOT NULL,
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

INSERT_TASK_DATA = "INSERT INTO task(id, project_id, title, content, is_protected, status) VALUES(?, ?, ?, ?, ?, ?)"

INSERT_ACCOUNT_DATA = """
INSERT INTO account(id, password)
VALUES(1, ?)
ON CONFLICT(id)
DO UPDATE SET password=excluded.password
"""

GET_PASSWORD = "SELECT password FROM account WHERE id = 1"

UPDATE_TASK_DATA = (
    "UPDATE task SET title = ?, content = ?, is_protected = ?, status = ? WHERE id = ?"
)

QUERY_TASKS_BY_PROJECT = """
SELECT id, title, content, is_protected, status, createdAt 
FROM task 
WHERE project_id = ? 
ORDER BY createdAt
"""

QUERY_ONE_TASKS_BY_ID = """
SELECT id, title, content, is_protected, status, createdAt 
FROM task 
WHERE id = ? 
"""

CREATE_PROJECT_TABLE = """
CREATE TABLE IF NOT EXISTS project(
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    type TEXT,
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

INSERT_PROJECT_DATA = (
    "INSERT INTO project(id, title, description, type) VALUES(?, ?, ?, ?)"
)

UPDATE_PROJECT_DATA = (
    "UPDATE project SET title = ?, description = ?, type = ? WHERE id = ?"
)

QUERY_ALL_PROJECT_DATA = """
SELECT id, title, description, type, createdAt 
FROM project 
ORDER BY createdAt
"""

UPDATE_TASK_COLUMN = "ALTER TABLE task ADD COLUMN is_protected INTEGER DEFAULT 0"

QUERY_ONE_PROJECT_DATA = """
SELECT id, title, description, type, createdAt 
FROM project 
WHERE id = ?
"""

DELETE_PROJECT_DATA = "DELETE FROM project WHERE id = ?"

DELETE_PROJECT_TASKS = "DELETE FROM task WHERE project_id = ?"

DELETE_TASK = "DELETE FROM task WHERE id = ?"

