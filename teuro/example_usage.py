"""
Пример использования обученной модели для распознавания старотатарского текста
"""
from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

def example_basic_usage():
    """Базовый пример использования модели"""
    print("Пример 1: Базовое распознавание")
    print("-" * 60)
    
    # Загрузка модели
    model = YOLO("runs/detect/old_tatar_yolov8/weights/best.pt")
    
    # Распознавание на изображении
    results = model.predict("path/to/image.jpg", conf=0.25)
    
    # Вывод результатов
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            print(f"Найдено объектов: {len(boxes)}")
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls]
                print(f"  - {class_name}: {conf:.2%}")

def example_batch_processing():
    """Пример пакетной обработки изображений"""
    print("\nПример 2: Пакетная обработка")
    print("-" * 60)
    
    model = YOLO("runs/detect/old_tatar_yolov8/weights/best.pt")
    
    # Список изображений
    image_paths = [
        "path/to/image1.jpg",
        "path/to/image2.jpg",
        "path/to/image3.jpg"
    ]
    
    # Обработка всех изображений
    for img_path in image_paths:
        results = model.predict(img_path, conf=0.25, save=True)
        print(f"Обработано: {img_path}")

def example_custom_visualization():
    """Пример с кастомной визуализацией"""
    print("\nПример 3: Кастомная визуализация")
    print("-" * 60)
    
    model = YOLO("runs/detect/old_tatar_yolov8/weights/best.pt")
    
    # Загрузка изображения
    image_path = "path/to/image.jpg"
    image = cv2.imread(image_path)
    
    # Распознавание
    results = model.predict(image, conf=0.25)
    
    # Визуализация результатов
    annotated_image = results[0].plot()
    
    # Сохранение результата
    cv2.imwrite("result_annotated.jpg", annotated_image)
    print("Результат сохранен в result_annotated.jpg")

def example_extract_text_regions():
    """Пример извлечения регионов с текстом"""
    print("\nПример 4: Извлечение регионов текста")
    print("-" * 60)
    
    model = YOLO("runs/detect/old_tatar_yolov8/weights/best.pt")
    
    image_path = "path/to/image.jpg"
    image = cv2.imread(image_path)
    
    results = model.predict(image, conf=0.25)
    
    # Извлечение bounding boxes
    text_regions = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Координаты bounding box
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Извлечение региона
                region = image[y1:y2, x1:x2]
                text_regions.append(region)
                
                # Класс и уверенность
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls]
                
                print(f"Регион: {class_name} ({conf:.2%}) - [{x1}, {y1}, {x2}, {y2}]")
    
    # Сохранение регионов
    for i, region in enumerate(text_regions):
        cv2.imwrite(f"text_region_{i}.jpg", region)
    
    print(f"Извлечено {len(text_regions)} регионов текста")

def example_video_processing():
    """Пример обработки видео"""
    print("\nПример 5: Обработка видео")
    print("-" * 60)
    
    model = YOLO("runs/detect/old_tatar_yolov8/weights/best.pt")
    
    # Обработка видео
    video_path = "path/to/video.mp4"
    results = model.predict(
        source=video_path,
        conf=0.25,
        save=True,
        save_txt=True
    )
    
    print("Видео обработано и сохранено")

if __name__ == "__main__":
    print("=" * 60)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ МОДЕЛИ")
    print("=" * 60)
    
    # Раскомментируйте нужный пример
    # example_basic_usage()
    # example_batch_processing()
    # example_custom_visualization()
    # example_extract_text_regions()
    # example_video_processing()
    
    print("\nПримечание: Раскомментируйте нужные примеры в коде для запуска")

