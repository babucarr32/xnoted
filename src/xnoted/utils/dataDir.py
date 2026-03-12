from pathlib import Path
from platformdirs import user_data_dir


def get_data_dir() -> Path:
    """Get the appropriate data directory for xnoted."""
    app_dir = Path(user_data_dir("xnoted"))
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


XNOTED_PATH = get_data_dir() / "database.db"
DB_NAME = str(XNOTED_PATH)
