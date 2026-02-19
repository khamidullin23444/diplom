"""
Скрипт для валидации обученной модели на тестовом наборе
"""
import os
import torch
from ultralytics import YOLO
from pathlib import Path

def validate_model(
    model_path,
    data_yaml="dataset/data.yaml",
    conf_threshold=0.25,
    device=None
):
    """
    Валидирует обученную модель на тестовом наборе
    
    Args:
        model_path: Путь к обученной модели (.pt файл)
        data_yaml: Путь к файлу data.yaml с конфигурацией датасета
        conf_threshold: Порог уверенности для детекций
        device: Устройство для валидации (None = auto, 0 = GPU, 'cpu' = CPU)
    """
    print("=" * 60)
    print("ВАЛИДАЦИЯ МОДЕЛИ")
    print("=" * 60)
    
    # Проверка CUDA
    if torch.cuda.is_available():
        print(f"✓ CUDA доступна: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠ CUDA недоступна, используется CPU")
    
    # Проверка существования модели
    if not os.path.exists(model_path):
        print(f"\n✗ Ошибка: Модель {model_path} не найдена!")
        return None
    
    # Проверка существования конфигурации датасета
    if not os.path.exists(data_yaml):
        print(f"\n✗ Ошибка: Файл {data_yaml} не найден!")
        return None
    
    # Автоматический выбор устройства
    if device is None:
        device = 0 if torch.cuda.is_available() else 'cpu'
    
    # Загрузка модели
    print(f"\nЗагрузка модели: {model_path}")
    model = YOLO(model_path)
    
    print(f"\nПараметры валидации:")
    print(f"  Датасет: {data_yaml}")
    print(f"  Порог уверенности: {conf_threshold}")
    print(f"  Устройство: {device}")
    
    # Валидация
    print(f"\n{'=' * 60}")
    print("НАЧАЛО ВАЛИДАЦИИ")
    print(f"{'=' * 60}\n")
    
    try:
        results = model.val(
            data=data_yaml,
            conf=conf_threshold,
            device=device,
            plots=True,
            save_json=True,
            save_hybrid=True
        )
        
        print(f"\n{'=' * 60}")
        print("ВАЛИДАЦИЯ ЗАВЕРШЕНА")
        print(f"{'=' * 60}")
        
        # Вывод основных метрик
        if hasattr(results, 'box'):
            metrics = results.box
            print(f"\nМетрики:")
            print(f"  mAP50: {metrics.map50:.4f}")
            print(f"  mAP50-95: {metrics.map:.4f}")
            print(f"  Precision: {metrics.mp:.4f}")
            print(f"  Recall: {metrics.mr:.4f}")
        
        return results
        
    except Exception as e:
        print(f"\n✗ Ошибка во время валидации: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Валидация обученной модели")
    parser.add_argument(
        "--model",
        type=str,
        default="runs/detect/old_tatar_yolov8/weights/best.pt",
        help="Путь к обученной модели"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="dataset/data.yaml",
        help="Путь к файлу data.yaml"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Порог уверенности"
    )
    
    args = parser.parse_args()
    
    validate_model(
        model_path=args.model,
        data_yaml=args.data,
        conf_threshold=args.conf
    )

