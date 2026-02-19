"""
Скрипт для распознавания старотатарского текста на изображениях
"""
import os
import cv2
import torch
from ultralytics import YOLO
from pathlib import Path
import argparse

def check_cuda():
    """Проверяет доступность CUDA"""
    if torch.cuda.is_available():
        print(f"✓ CUDA доступна: {torch.cuda.get_device_name(0)}")
        return True
    else:
        print("⚠ CUDA недоступна, используется CPU")
        return False

def recognize_text(
    model_path,
    image_path,
    conf_threshold=0.25,
    save_results=True,
    output_dir="results"
):
    """
    Распознает текст на изображении используя обученную модель YOLOv8
    
    Args:
        model_path: Путь к обученной модели (.pt файл)
        image_path: Путь к изображению или папке с изображениями
        conf_threshold: Порог уверенности для детекций
        save_results: Сохранять ли результаты
        output_dir: Папка для сохранения результатов
    """
    print("=" * 60)
    print("РАСПОЗНАВАНИЕ СТАРОТАТАРСКОГО ТЕКСТА")
    print("=" * 60)
    
    # Проверка CUDA
    check_cuda()
    
    # Проверка существования модели
    if not os.path.exists(model_path):
        print(f"\n✗ Ошибка: Модель {model_path} не найдена!")
        print("Пожалуйста, сначала обучите модель используя train.py")
        return None
    
    # Загрузка модели
    print(f"\nЗагрузка модели: {model_path}")
    model = YOLO(model_path)
    
    # Определение устройства
    device = 0 if torch.cuda.is_available() else 'cpu'
    print(f"Используемое устройство: {device}")
    
    # Проверка существования изображения/папки
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"\n✗ Ошибка: Путь {image_path} не существует!")
        return None
    
    # Определение списка изображений
    if image_path.is_file():
        image_paths = [str(image_path)]
    else:
        # Поддерживаемые форматы изображений
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        image_paths = []
        for ext in extensions:
            image_paths.extend(list(image_path.glob(f"*{ext}")))
            image_paths.extend(list(image_path.glob(f"*{ext.upper()}")))
        image_paths = [str(p) for p in image_paths]
    
    if not image_paths:
        print(f"\n✗ Ошибка: Изображения не найдены в {image_path}")
        return None
    
    print(f"\nНайдено изображений: {len(image_paths)}")
    
    # Создание папки для результатов
    if save_results:
        os.makedirs(output_dir, exist_ok=True)
    
    # Обработка каждого изображения
    results_list = []
    for i, img_path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] Обработка: {os.path.basename(img_path)}")
        
        try:
            # Выполнение инференса
            results = model.predict(
                source=img_path,
                conf=conf_threshold,
                device=device,
                save=save_results,
                project=output_dir,
                name="predictions",
                show_labels=True,
                show_conf=True,
                line_width=2
            )
            
            results_list.append((img_path, results))
            
            # Вывод информации о детекциях
            if results and len(results) > 0:
                detections = results[0].boxes
                if detections is not None and len(detections) > 0:
                    print(f"  Найдено объектов: {len(detections)}")
                    for j, box in enumerate(detections, 1):
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = model.names[cls] if cls < len(model.names) else f"class_{cls}"
                        print(f"    {j}. {class_name}: {conf:.2%}")
                else:
                    print("  Объекты не обнаружены")
            
        except Exception as e:
            print(f"  ✗ Ошибка при обработке {img_path}: {e}")
            continue
    
    print(f"\n{'=' * 60}")
    print("ОБРАБОТКА ЗАВЕРШЕНА")
    print(f"{'=' * 60}")
    
    if save_results:
        print(f"\nРезультаты сохранены в: {output_dir}/predictions/")
    
    return results_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Распознавание старотатарского текста на изображениях")
    parser.add_argument(
        "--model",
        type=str,
        default="runs/detect/old_tatar_yolov8/weights/best.pt",
        help="Путь к обученной модели"
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Путь к изображению или папке с изображениями"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Порог уверенности (0.0-1.0)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results",
        help="Папка для сохранения результатов"
    )
    
    args = parser.parse_args()
    
    recognize_text(
        model_path=args.model,
        image_path=args.source,
        conf_threshold=args.conf,
        output_dir=args.output
    )

