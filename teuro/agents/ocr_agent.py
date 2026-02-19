"""
OCR агент на основе YOLOv8 для распознавания старотатарского текста
"""
import os
import cv2
import torch
import numpy as np
from typing import TypedDict, List, Dict, Any
from ultralytics import YOLO
from langgraph.graph import StateGraph, START, END


class OCRState(TypedDict):
    """Состояние OCR агента"""
    image_path: str
    detected_regions: List[Dict[str, Any]]
    raw_text: str
    confidence_scores: List[float]
    error: str


class OCRAgent:
    """
    Агент для оптического распознавания символов на основе YOLOv8
    """
    
    def __init__(self, model_path: str = "runs/detect/old_tatar_yolov8/weights/best.pt", 
                 conf_threshold: float = 0.25):
        """
        Инициализация OCR агента
        
        Args:
            model_path: Путь к обученной модели YOLOv8
            conf_threshold: Порог уверенности для детекций
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.device = 0 if torch.cuda.is_available() else 'cpu'
        
        # Загрузка модели
        if os.path.exists(model_path):
            self.model = YOLO(model_path)
            print(f"✓ OCR модель загружена: {model_path}")
        else:
            print(f"⚠ Модель не найдена: {model_path}")
            print("Используется предобученная модель YOLOv8n")
            self.model = YOLO("yolov8n.pt")
    
    def detect_and_extract(self, state: OCRState) -> OCRState:
        """
        Детекция текстовых регионов и извлечение текста
        
        Args:
            state: Состояние агента
            
        Returns:
            Обновленное состояние с распознанным текстом
        """
        try:
            image_path = state.get("image_path", "")
            
            if not os.path.exists(image_path):
                state["error"] = f"Изображение не найдено: {image_path}"
                return state
            
            # Загрузка изображения
            image = cv2.imread(image_path)
            if image is None:
                state["error"] = f"Не удалось загрузить изображение: {image_path}"
                return state
            
            # Детекция с помощью YOLOv8
            results = self.model.predict(
                source=image_path,
                conf=self.conf_threshold,
                device=self.device,
                verbose=False
            )
            
            detected_regions = []
            raw_text_parts = []
            confidence_scores = []
            
            # Обработка результатов детекции
            for result in results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    # Сортировка по координатам (сверху вниз, слева направо)
                    sorted_indices = self._sort_boxes_by_position(boxes)
                    
                    for idx in sorted_indices:
                        box = boxes[idx]
                        
                        # Координаты bounding box
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # Класс и уверенность
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = self.model.names[cls] if cls < len(self.model.names) else f"class_{cls}"
                        
                        # Извлечение региона изображения
                        region = image[y1:y2, x1:x2]
                        
                        detected_regions.append({
                            'bbox': [x1, y1, x2, y2],
                            'class': class_name,
                            'class_id': cls,
                            'confidence': conf,
                            'region_image': region.tolist()  # Для сериализации
                        })
                        
                        raw_text_parts.append(f"[{class_name}]")
                        confidence_scores.append(conf)
            
            # Объединение текста
            raw_text = " ".join(raw_text_parts)
            
            state["detected_regions"] = detected_regions
            state["raw_text"] = raw_text
            state["confidence_scores"] = confidence_scores
            state["error"] = ""
            
            print(f"✓ OCR: обнаружено {len(detected_regions)} регионов текста")
            
        except Exception as e:
            state["error"] = f"Ошибка при распознавании: {str(e)}"
            import traceback
            traceback.print_exc()
        
        return state
    
    def _sort_boxes_by_position(self, boxes) -> List[int]:
        """
        Сортировка bounding boxes по позиции (сверху вниз, слева направо)
        
        Args:
            boxes: Объект boxes от YOLO
            
        Returns:
            Отсортированные индексы
        """
        positions = []
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes[i].xyxy[0].cpu().numpy()
            center_y = (y1 + y2) / 2
            center_x = (x1 + x2) / 2
            positions.append((center_y, center_x, i))
        
        # Сортировка: сначала по Y (сверху вниз), затем по X (слева направо)
        positions.sort(key=lambda x: (x[0] // 50, x[1]))  # Группировка по строкам
        
        return [pos[2] for pos in positions]


def create_ocr_agent(model_path: str = "runs/detect/old_tatar_yolov8/weights/best.pt",
                     conf_threshold: float = 0.25) -> StateGraph:
    """
    Создание графа OCR агента с использованием LangGraph
    
    Args:
        model_path: Путь к модели YOLOv8
        conf_threshold: Порог уверенности
        
    Returns:
        Скомпилированный граф агента
    """
    ocr = OCRAgent(model_path=model_path, conf_threshold=conf_threshold)
    
    # Создание графа
    workflow = StateGraph(OCRState)
    
    # Добавление узла обработки
    workflow.add_node("ocr_detection", ocr.detect_and_extract)
    
    # Определение потока
    workflow.add_edge(START, "ocr_detection")
    workflow.add_edge("ocr_detection", END)
    
    return workflow.compile()

