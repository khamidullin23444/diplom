"""
Скрипт для обучения моделей YOLOv8 для задачи распознавания старотатарского текста.

Поддерживаются два режима работы:
1) Универсальный (generic) — обучение одной модели YOLOv8 на произвольном датасете.
2) Специализированные пресеты из статьи:
   - lines   — модель YOLOv8n для распознавания строк;
   - words   — модель YOLOv8n для распознавания слов;
   - symbols — модель YOLOv8x для распознавания арабских (старотатарских) символов.
"""
import os
import argparse
import torch
from ultralytics import YOLO
from pathlib import Path


# Пресеты, соответствующие трём моделям из статьи
TASK_PRESETS = {
    # Модель распознавания строк (YOLOv8n, ~30 эпох, ~736x736)
    "lines": {
        "data_yaml": "datalines/data.yaml",
        "epochs": 30,
        "imgsz": 736,
        "batch": 8,
        "model_size": "n",
        "project": "runs/lines",
        "name": "lines_yolov8n",
    },
    # Модель распознавания слов (YOLOv8n, ~50 эпох, ~640x640)
    "words": {
        "data_yaml": "datawords/data.yaml",
        "epochs": 50,
        "imgsz": 640,
        "batch": 8,
        "model_size": "n",
        "project": "runs/words",
        "name": "words_yolov8n",
    },
    # Модель распознавания символов (YOLOv8x, ~40 эпох, ~320x320)
    "symbols": {
        "data_yaml": "dataset/data.yaml",
        "epochs": 40,
        "imgsz": 320,
        "batch": 8,
        "model_size": "x",
        "project": "runs/symbols",
        "name": "symbols_yolov8x",
    },
}

def check_cuda():
    """Проверяет доступность CUDA"""
    if torch.cuda.is_available():
        print(f"✓ CUDA доступна!")
        print(f"  Устройство: {torch.cuda.get_device_name(0)}")
        print(f"  Версия CUDA: {torch.version.cuda}")
        print(f"  Версия cuDNN: {torch.backends.cudnn.version()}")
        return True
    else:
        print("✗ CUDA недоступна. Обучение будет выполняться на CPU (медленно!)")
        return False

def train_model(
    data_yaml="dataset/data.yaml",
    epochs=50,
    imgsz=640,
    batch=8,
    device=None,
    model_size="n",  # n, s, m, l, x
    project="runs/detect",
    name="old_tatar_yolov8",
):
    """
    Обучает модель YOLOv8.

    Args:
        data_yaml: Путь к файлу data.yaml с конфигурацией датасета.
        epochs: Количество эпох обучения.
        imgsz: Размер изображений для обучения.
        batch: Размер батча.
        device: Устройство для обучения (None = auto, 0 = GPU, 'cpu' = CPU).
        model_size: Размер модели YOLOv8 (n=nano, s=small, m=medium, l=large, x=xlarge).
        project: Папка для сохранения результатов.
        name: Имя эксперимента.
    """
    print("=" * 60)
    print("ОБУЧЕНИЕ МОДЕЛИ YOLOv8 ДЛЯ РАСПОЗНАВАНИЯ СТАРОТАТАРСКОГО ТЕКСТА")
    print("=" * 60)
    
    # Проверка CUDA
    cuda_available = check_cuda()
    
    # Автоматический выбор устройства
    if device is None:
        device = 0 if cuda_available else 'cpu'
    
    # Проверка существования файла конфигурации
    if not os.path.exists(data_yaml):
        print(f"\n✗ Ошибка: Файл {data_yaml} не найден!")
        print("Пожалуйста, сначала загрузите датасет используя download_dataset.py")
        return None
    
    # Загрузка модели YOLOv8
    model_name = f"yolov8{model_size}.pt"
    print(f"\nЗагрузка модели: {model_name}")
    model = YOLO(model_name)
    
    # Параметры обучения
    print(f"\nПараметры обучения:")
    print(f"  Датасет: {data_yaml}")
    print(f"  Эпохи: {epochs}")
    print(f"  Размер изображений: {imgsz}")
    print(f"  Размер батча: {batch}")
    print(f"  Устройство: {device}")
    print(f"  Модель: {model_name}")
    
    # Обучение
    print(f"\n{'=' * 60}")
    print("НАЧАЛО ОБУЧЕНИЯ")
    print(f"{'=' * 60}\n")
    
    try:
        results = model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            device=device,
            project=project,
            name=name,
            patience=50,  # Early stopping patience
            save=True,
            save_period=10,  # Сохранять чекпоинт каждые 10 эпох
            plots=True,  # Генерировать графики
            val=True,  # Валидация во время обучения
            # Дополнительные параметры для оптимизации
            optimizer='AdamW',
            lr0=0.01,  # Начальная скорость обучения
            lrf=0.01,  # Финальная скорость обучения (lr0 * lrf)
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
            warmup_momentum=0.8,
            warmup_bias_lr=0.1,
            box=7.5,  # Вес loss для bounding box
            cls=0.5,  # Вес loss для классификации
            dfl=1.5,  # Вес loss для distribution focal loss
        )
        
        print(f"\n{'=' * 60}")
        print("ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print(f"{'=' * 60}")
        
        # Путь к лучшей модели
        best_model_path = os.path.join(project, name, "weights", "best.pt")
        print(f"\nЛучшая модель сохранена в: {best_model_path}")
        
        return model, results
        
    except Exception as e:
        print(f"\n✗ Ошибка во время обучения: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Обучение моделей YOLOv8 для распознавания старотатарского текста.\n"
            "Режимы: generic (произвольный датасет), "
            "lines/words/symbols (пресеты из статьи), all (все три модели по очереди)."
        )
    )

    parser.add_argument(
        "--task",
        type=str,
        choices=["generic", "lines", "words", "symbols", "all"],
        default="generic",
        help=(
            "Что обучать: "
            "'generic' — один датасет (как раньше), "
            "'lines' — модель строк (YOLOv8n), "
            "'words' — модель слов (YOLOv8n), "
            "'symbols' — модель символов (YOLOv8x), "
            "'all' — последовательно все три."
        ),
    )

    # Параметры для режима generic (совместимы с исходной версией скрипта)
    parser.add_argument(
        "--data_yaml",
        type=str,
        default="dataset/data.yaml",
        help="Путь к data.yaml (используется в режиме generic).",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Количество эпох (режим generic).",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Размер изображений (режим generic).",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Размер батча (режим generic).",
    )
    parser.add_argument(
        "--model_size",
        type=str,
        default="n",
        help="Размер модели YOLOv8: n/s/m/l/x (режим generic).",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Устройство: None (auto), '0', '1', 'cpu' и т.п.",
    )

    args = parser.parse_args()

    if args.task == "generic":
        # Поведение, максимально близкое к исходному train.py
        train_model(
            data_yaml=args.data_yaml,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            model_size=args.model_size,
            device=args.device,
        )
    elif args.task == "all":
        for task_name in ["lines", "words", "symbols"]:
            preset = TASK_PRESETS[task_name]
            print(f"\n=== Обучение модели для задачи: {task_name} ===")
            train_model(
                data_yaml=preset["data_yaml"],
                epochs=preset["epochs"],
                imgsz=preset["imgsz"],
                batch=preset["batch"],
                model_size=preset["model_size"],
                project=preset["project"],
                name=preset["name"],
                device=args.device,
            )
    else:
        # Один из специализированных пресетов: lines / words / symbols
        preset = TASK_PRESETS[args.task]
        train_model(
            data_yaml=preset["data_yaml"],
            epochs=preset["epochs"],
            imgsz=preset["imgsz"],
            batch=preset["batch"],
            model_size=preset["model_size"],
            project=preset["project"],
            name=preset["name"],
            device=args.device,
        )

