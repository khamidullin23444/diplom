"""
Скрипт для загрузки датасетов Old Tatar с Roboflow.

Поддерживает режимы:
- generic — один общий датасет (старое поведение);
- lines   — датасет строк;
- words   — датасет слов;
- symbols — датасет символов;
- all     — загрузка всех трёх специализированных датасетов.
"""
import os
import argparse
from roboflow import Roboflow
from dotenv import load_dotenv


TASK_PROJECTS = {
    "generic": {
        "workspace": "lab-ovmmc",
        "project": "old-tatar-new",
        "version": 2,
        "target_dir": "dataset",
    },
    "lines": {
        "workspace": "lab-ovmmc",
        "project": "old-tatar-crop-lines",
        "version": 3,
        "target_dir": "dataset/lines",
    },
    "words": {
        "workspace": "lab-ovmmc",
        "project": "old-tatar-words",
        "version": 2,
        "target_dir": "dataset/words",
    },
    # "symbols": {
    #     "workspace": "lab-ovmmc",
    #     "project": "old-tatar-symbols",
    #     "version": 1,
    #     "target_dir": "dataset/symbols",
    # },
}


def ensure_api_key(api_key: str | None) -> str | None:
    """Получение API ключа Roboflow из аргумента или окружения."""
    if api_key is not None:
        return api_key

    key = os.getenv("ROBOFLOW_API_KEY")
    if key is None:
        print("ВНИМАНИЕ: API ключ не найден!")
        print("Пожалуйста, установите переменную окружения ROBOFLOW_API_KEY")
        print("или передайте api_key через аргумент --api-key.")
        print("\nДля получения API ключа:")
        print("1. Зарегистрируйтесь на https://roboflow.com")
        print("2. Перейдите в Settings -> API")
        print("3. Скопируйте ваш API ключ")
        return None
    return key


def download_single_dataset(
    api_key: str,
    workspace: str,
    project: str,
    version: int,
    target_dir: str,
):
    """Скачивает один датасет Roboflow (YOLOv8) и выводит пути к данным."""
    print(f"\nИнициализация Roboflow для проекта: {workspace}/{project} (v{version})")
    rf = Roboflow(api_key=api_key)
    project_obj = rf.workspace(workspace).project(project)
    dataset = project_obj.version(version).download("yolov8")

    print(f"  Датасет загружен в: {dataset.location}")
    print(f"  data.yaml: {os.path.join(dataset.location, 'data.yaml')}")
    print(f"  Рекомендуемая целевая папка для train.py: {target_dir}")

    return dataset


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Загрузка датасетов Old Tatar с Roboflow.\n"
            "Режимы: generic (один датасет), lines/words/symbols (специализированные), all (все три)."
        )
    )
    parser.add_argument(
        "--task",
        type=str,
        choices=["generic", "lines", "words", "symbols", "all"],
        default="generic",
        help=(
            "Какой датасет скачать: "
            "'generic' — общий, "
            "'lines' — строки, "
            "'words' — слова, "
            "'symbols' — символы, "
            "'all' — все три специализированных."
        ),
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API ключ Roboflow (по умолчанию берётся из ROBOFLOW_API_KEY).",
    )

    args = parser.parse_args()

    load_dotenv()
    api_key = ensure_api_key(args.api_key)
    if api_key is None:
        return

    if args.task == "all":
        for t in ["lines", "words", "symbols"]:
            cfg = TASK_PROJECTS[t]
            download_single_dataset(
                api_key=api_key,
                workspace=cfg["workspace"],
                project=cfg["project"],
                version=cfg["version"],
                target_dir=cfg["target_dir"],
            )
    else:
        cfg = TASK_PROJECTS[args.task]
        download_single_dataset(
            api_key=api_key,
            workspace=cfg["workspace"],
            project=cfg["project"],
            version=cfg["version"],
            target_dir=cfg["target_dir"],
        )


if __name__ == "__main__":
    main()

