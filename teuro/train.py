"""
Скрипт для обучения модели YOLOv8 на датасете Old Tatar
"""
import os
import torch
from ultralytics import YOLO
from pathlib import Path

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
    epochs=100,
    imgsz=640,
    batch=16,
    device=None,
    model_size="n",  # n, s, m, l, x
    project="runs/detect",
    name="old_tatar_yolov8"
):
    """
    Обучает модель YOLOv8 на датасете Old Tatar
    
    Args:
        data_yaml: Путь к файлу data.yaml с конфигурацией датасета
        epochs: Количество эпох обучения
        imgsz: Размер изображений для обучения
        batch: Размер батча
        device: Устройство для обучения (None = auto, 0 = GPU, 'cpu' = CPU)
        model_size: Размер модели YOLOv8 (n=nano, s=small, m=medium, l=large, x=xlarge)
        project: Папка для сохранения результатов
        name: Имя эксперимента
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
    # Настройки обучения
    # Можно изменить эти параметры в зависимости от ваших потребностей
    
    # Для RTX 5060 Ti рекомендуется batch=16-32 в зависимости от размера модели
    train_model(
        data_yaml="dataset/data.yaml",  # Путь к конфигурации датасета
        epochs=100,  # Количество эпох
        imgsz=640,  # Размер изображений (640 - стандартный для YOLOv8)
        batch=16,  # Размер батча (уменьшите если не хватает памяти)
        model_size="n",  # Начните с 'n' (nano) для быстрого тестирования, затем 's' или 'm'
        # device=0,  # Раскомментируйте для принудительного использования GPU 0
    )

