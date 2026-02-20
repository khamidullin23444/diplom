"""
Каскадное распознавание старотатарского текста:
1) Модель строк (YOLOv8n) — находит строки на полной странице.
2) Модель слов (YOLOv8n) — находит слова внутри каждой строки.
3) Модель символов (YOLOv8x) — находит арабские символы внутри слов.

Ожидается, что модели обучены и лежат по путям:
- runs/lines/lines_yolov8n/weights/best.pt
- runs/words/words_yolov8n/weights/best.pt
- runs/symbols/symbols_yolov8x/weights/best.pt

и соответствующие data.yaml/структуры совпадают с логикой обучения из train.py.
"""

import os
import argparse
from pathlib import Path
from typing import List, Dict, Any

import cv2
import numpy as np
import torch
from ultralytics import YOLO


def _load_model(path: str) -> YOLO:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Модель не найдена: {path}")
    return YOLO(path)


def _sort_boxes_top_down_left_right(boxes) -> List[int]:
    """Сортировка боксов: сверху вниз, слева направо (как в статье)."""
    positions = []
    for i in range(len(boxes)):
        x1, y1, x2, y2 = boxes[i].xyxy[0].cpu().numpy()
        center_y = (y1 + y2) / 2
        center_x = (x1 + x2) / 2
        positions.append((center_y, center_x, i))
    positions.sort(key=lambda x: (x[0] // 50, x[1]))
    return [p[2] for p in positions]


def cascade_recognize(
    image_path: str,
    lines_model_path: str = "runs/lines/lines_yolov8n/weights/best.pt",
    words_model_path: str = "runs/words/words_yolov8n/weights/best.pt",
    symbols_model_path: str = "runs/symbols/symbols_yolov8x/weights/best.pt",
    conf_lines: float = 0.25,
    conf_words: float = 0.25,
    conf_symbols: float = 0.25,
) -> Dict[str, Any]:
    """
    Полный каскад: строка -> слово -> символ.

    Returns:
        Структура с координатами и распознанными символами по строкам/словам.
    """
    device = 0 if torch.cuda.is_available() else "cpu"

    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Изображение не найдено: {img_path}")

    image = cv2.imread(str(img_path))
    if image is None:
        raise RuntimeError(f"Не удалось загрузить изображение: {img_path}")

    print(f"✓ Загрузка моделей каскада...")
    lines_model = _load_model(lines_model_path)
    words_model = _load_model(words_model_path)
    symbols_model = _load_model(symbols_model_path)

    print(f"\nШаг 1: детекция строк...")
    lines_res = lines_model.predict(
        source=image,
        conf=conf_lines,
        device=device,
        verbose=False,
    )[0]

    lines_boxes = lines_res.boxes
    if lines_boxes is None or len(lines_boxes) == 0:
        print("Строки не найдены.")
        return {"lines": [], "raw_symbols_sequence": "", "image_path": str(img_path)}

    line_indices = _sort_boxes_top_down_left_right(lines_boxes)
    all_lines: List[Dict[str, Any]] = []
    global_symbols: List[str] = []

    for li, idx in enumerate(line_indices, 1):
        box = lines_boxes[idx]
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        line_img = image[y1:y2, x1:x2]

        print(f"\nШаг 2: детекция слов в строке {li}...")
        words_res = words_model.predict(
            source=line_img,
            conf=conf_words,
            device=device,
            verbose=False,
        )[0]

        words_boxes = words_res.boxes
        line_data: Dict[str, Any] = {
            "bbox": [x1, y1, x2, y2],
            "words": [],
        }

        if words_boxes is None or len(words_boxes) == 0:
            print("  Слова не найдены в строке.")
            all_lines.append(line_data)
            continue

        word_indices = _sort_boxes_top_down_left_right(words_boxes)

        for wi, w_idx in enumerate(word_indices, 1):
            w_box = words_boxes[w_idx]
            wx1, wy1, wx2, wy2 = w_box.xyxy[0].cpu().numpy()
            wx1, wy1, wx2, wy2 = int(wx1), int(wy1), int(wx2), int(wy2)
            word_img = line_img[wy1:wy2, wx1:wx2]

            print(f"  Шаг 3: детекция символов в слове {wi}...")
            symbols_res = symbols_model.predict(
                source=word_img,
                conf=conf_symbols,
                device=device,
                verbose=False,
            )[0]

            symbols_boxes = symbols_res.boxes
            word_symbols: List[Dict[str, Any]] = []

            if symbols_boxes is not None and len(symbols_boxes) > 0:
                sym_indices = _sort_boxes_top_down_left_right(symbols_boxes)
                for s_idx in sym_indices:
                    s_box = symbols_boxes[s_idx]
                    sx1, sy1, sx2, sy2 = s_box.xyxy[0].cpu().numpy()
                    sx1, sy1, sx2, sy2 = int(sx1), int(sy1), int(sx2), int(sy2)
                    cls = int(s_box.cls[0])
                    conf = float(s_box.conf[0])
                    class_name = symbols_model.names[cls] if cls < len(symbols_model.names) else f"class_{cls}"

                    word_symbols.append(
                        {
                            "bbox": [sx1, sy1, sx2, sy2],
                            "class": class_name,
                            "class_id": cls,
                            "confidence": conf,
                        }
                    )
                    global_symbols.append(class_name)

            line_data["words"].append(
                {
                    "bbox": [wx1, wy1, wx2, wy2],
                    "symbols": word_symbols,
                }
            )

        all_lines.append(line_data)

    return {
        "image_path": str(img_path),
        "lines": all_lines,
        "raw_symbols_sequence": " ".join(global_symbols),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Каскадное распознавание старотатарского текста (строки → слова → символы)"
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Путь к изображению со старотатарским текстом",
    )
    parser.add_argument(
        "--lines-model",
        type=str,
        default="runs/lines/lines_yolov8n/weights/best.pt",
        help="Путь к модели распознавания строк",
    )
    parser.add_argument(
        "--words-model",
        type=str,
        default="runs/words/words_yolov8n/weights/best.pt",
        help="Путь к модели распознавания слов",
    )
    parser.add_argument(
        "--symbols-model",
        type=str,
        default="runs/symbols/symbols_yolov8x/weights/best.pt",
        help="Путь к модели распознавания символов",
    )
    parser.add_argument(
        "--conf-lines",
        type=float,
        default=0.25,
        help="Порог уверенности для модели строк",
    )
    parser.add_argument(
        "--conf-words",
        type=float,
        default=0.25,
        help="Порог уверенности для модели слов",
    )
    parser.add_argument(
        "--conf-symbols",
        type=float,
        default=0.25,
        help="Порог уверенности для модели символов",
    )

    args = parser.parse_args()

    result = cascade_recognize(
        image_path=args.image,
        lines_model_path=args.lines_model,
        words_model_path=args.words_model,
        symbols_model_path=args.symbols_model,
        conf_lines=args.conf_lines,
        conf_words=args.conf_words,
        conf_symbols=args.conf_symbols,
    )

    print("\n=== Итоговая структура каскада ===")
    print(f"Изображение: {result['image_path']}")
    print(f"Всего строк: {len(result['lines'])}")
    total_words = sum(len(l['words']) for l in result['lines'])
    print(f"Всего слов: {total_words}")
    print(f"Последовательность символов (классы):")
    print(result["raw_symbols_sequence"])

