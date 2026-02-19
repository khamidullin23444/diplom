"""
Скрипт для экспорта обученной модели в различные форматы
"""
import os
import torch
from ultralytics import YOLO

def export_model(
    model_path,
    formats=['onnx', 'torchscript', 'engine'],  # engine требует TensorRT
    imgsz=640,
    device=None
):
    """
    Экспортирует обученную модель в различные форматы
    
    Args:
        model_path: Путь к обученной модели (.pt файл)
        formats: Список форматов для экспорта
                 Доступные: 'onnx', 'torchscript', 'engine', 'coreml', 'tflite', 'pb', 'paddle'
        imgsz: Размер изображений для экспорта
        device: Устройство для экспорта
    """
    print("=" * 60)
    print("ЭКСПОРТ МОДЕЛИ")
    print("=" * 60)
    
    # Проверка существования модели
    if not os.path.exists(model_path):
        print(f"\n✗ Ошибка: Модель {model_path} не найдена!")
        return None
    
    # Автоматический выбор устройства
    if device is None:
        device = 0 if torch.cuda.is_available() else 'cpu'
    
    # Загрузка модели
    print(f"\nЗагрузка модели: {model_path}")
    model = YOLO(model_path)
    
    print(f"\nПараметры экспорта:")
    print(f"  Форматы: {', '.join(formats)}")
    print(f"  Размер изображений: {imgsz}")
    print(f"  Устройство: {device}")
    
    exported_files = []
    
    for fmt in formats:
        print(f"\n{'=' * 60}")
        print(f"Экспорт в формат: {fmt.upper()}")
        print(f"{'=' * 60}")
        
        try:
            if fmt == 'engine':
                # TensorRT требует CUDA
                if not torch.cuda.is_available():
                    print("⚠ TensorRT экспорт требует CUDA. Пропускаем...")
                    continue
                result = model.export(format=fmt, imgsz=imgsz, device=device, half=True)
            else:
                result = model.export(format=fmt, imgsz=imgsz, device=device)
            
            exported_file = result if isinstance(result, str) else model_path.replace('.pt', f'.{fmt}')
            exported_files.append(exported_file)
            print(f"✓ Успешно экспортировано: {exported_file}")
            
        except Exception as e:
            print(f"✗ Ошибка при экспорте в {fmt}: {e}")
            continue
    
    print(f"\n{'=' * 60}")
    print("ЭКСПОРТ ЗАВЕРШЕН")
    print(f"{'=' * 60}")
    
    if exported_files:
        print(f"\nЭкспортированные файлы:")
        for f in exported_files:
            print(f"  - {f}")
    
    return exported_files

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Экспорт обученной модели")
    parser.add_argument(
        "--model",
        type=str,
        default="runs/detect/old_tatar_yolov8/weights/best.pt",
        help="Путь к обученной модели"
    )
    parser.add_argument(
        "--formats",
        type=str,
        nargs='+',
        default=['onnx'],
        help="Форматы для экспорта (onnx, torchscript, engine, и т.д.)"
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Размер изображений"
    )
    
    args = parser.parse_args()
    
    export_model(
        model_path=args.model,
        formats=args.formats,
        imgsz=args.imgsz
    )

