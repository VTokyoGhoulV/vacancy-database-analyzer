import json
from pathlib import Path


def find_project_root(marker_files: str | tuple = ("pyproject.toml", ".git", "requirements.txt")) -> Path:
    """
    Ищет корневую директорию проекта, поднимаясь по дереву папок,
    пока не найдет один из маркерных файлов/папок.
    """
    current_path = Path.cwd()  # Начинаем с текущей рабочей директории

    for parent in [current_path] + list(current_path.parents):
        for marker in marker_files:
            if (parent / marker).exists():
                return parent

    raise RuntimeError("Не удалось найти корень проекта. Убедитесь, что один из маркерных файлов присутствует.")


def get_data_from_file(file_name: str) -> dict:
    """
    Возвращает данные из JSON файла в виде Python объекта
    """

    with open(f"{find_project_root()}/data/{file_name}", "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    return dict(data)
