# Распознавание старотатарского текста с использованием YOLOv8

Проект для распознавания старотатарского текста на основе методов компьютерного зрения и нейронных сетей YOLOv8.

> 📖 **Для быстрого старта см. [QUICKSTART.md](QUICKSTART.md)**  
> 🤖 **Для мультиагентной системы см. [AGENTS_README.md](AGENTS_README.md)**

## Описание

Этот проект реализует систему оптического распознавания символов (OCR) для старотатарского языка, использующего арабскую письменность. Ядро системы — каскад из трёх моделей YOLOv8 (строки → слова → символы), согласованный с архитектурой из статьи Валишина И.А.

### ✨ Новое: Мультиагентная система

Проект теперь включает **мультиагентную архитектуру** на основе **LangGraph**, которая объединяет:
1. **OCR агент** - распознавание текста с помощью YOLOv8
2. **LLM агент** - исправление ошибок и лексический анализ с использованием моделей `tweety-tatar-base` или `mGPT-1.3B-tatar`

Подробнее см. [AGENTS_README.md](AGENTS_README.md)

## Требования

- **ОС**: Windows 10/11, Linux или macOS
- **Python**: 3.8 или выше
- **Видеокарта**: NVIDIA с поддержкой CUDA (рекомендуется)
  - Для данного проекта: NVIDIA GeForce RTX 5060 Ti
- **CUDA**: версия 11.8 или выше
- **cuDNN**: версия 8.6 или выше

## Установка

### 1. Установка CUDA и cuDNN

#### Для Windows:

1. Скачайте и установите CUDA Toolkit 11.8 или выше:
   - https://developer.nvidia.com/cuda-downloads

2. Скачайте и установите cuDNN:
   - https://developer.nvidia.com/cudnn
   - Распакуйте архив и скопируйте файлы в папку установки CUDA

3. Убедитесь, что CUDA добавлена в PATH:
   - Добавьте `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin` в PATH

#### Проверка установки CUDA:

```bash
nvcc --version
nvidia-smi
```

### 2. Установка Python зависимостей

1. Создайте виртуальное окружение (рекомендуется):

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

2. Установите PyTorch с поддержкой CUDA:

```bash
# Для CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Или для CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

3. Установите остальные зависимости:

```bash
pip install -r requirements.txt
```

### 3. Проверка установки

Запустите Python и проверьте доступность CUDA:

```python
import torch
print(f"CUDA доступна: {torch.cuda.is_available()}")
print(f"Устройство: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
```

## Подготовка датасета

### 1. Получение API ключа Roboflow

1. Зарегистрируйтесь на https://roboflow.com
2. Перейдите в Settings -> API
3. Скопируйте ваш API ключ

### 2. Загрузка датасетов

#### Вариант 1: Использование переменной окружения (рекомендуется)

```bash
# Windows PowerShell
$env:ROBOFLOW_API_KEY="ваш_api_ключ"

# Windows CMD
set ROBOFLOW_API_KEY=ваш_api_ключ

# Linux/macOS
export ROBOFLOW_API_KEY="ваш_api_ключ"

# Общий датасет (старое поведение)
python download_dataset.py --task generic

# Три специализированных датасета: строки, слова, символы
python download_dataset.py --task all
```

## Обучение модели

### Вариант A: Универсальное обучение (одна модель, старое поведение)

```bash
python train.py --task generic \
    --data_yaml dataset/data.yaml \
    --epochs 100 \
    --imgsz 640 \
    --batch 16 \
    --model_size n
```

### Вариант B: Каскад из трёх моделей (как в статье)

`train.py` содержит пресеты для трёх задач:

- `lines`   — модель строк (YOLOv8n);
- `words`   — модель слов (YOLOv8n);
- `symbols` — модель символов (YOLOv8x).

Обучение всех трёх моделей подряд:

```bash
python train.py --task all
```

Обучение только одной задачи (пример для строк):

```bash
python train.py --task lines
```

### Рекомендации по параметрам для RTX 5060 Ti

| Размер модели | Batch size | Память GPU | Скорость обучения |
|--------------|------------|------------|-------------------|
| nano (n)     | 32-64      | ~2-3 GB    | Быстро            |
| small (s)    | 16-32      | ~4-5 GB    | Средне            |
| medium (m)   | 8-16       | ~6-8 GB    | Медленно          |
| large (l)    | 4-8        | ~10-12 GB  | Очень медленно    |
| xlarge (x)   | 2-4        | ~14+ GB    | Крайне медленно   |

**Рекомендация**: Начните с модели `nano` для быстрого тестирования, затем переходите к `small` или `medium` для лучшей точности.

### Мониторинг обучения

Во время обучения результаты сохраняются в подпапках `runs/...` в зависимости от задачи:

- `runs/detect/old_tatar_yolov8/` — для режима `generic`;
- `runs/lines/lines_yolov8n/` — модель строк;
- `runs/words/words_yolov8n/` — модель слов;
- `runs/symbols/symbols_yolov8x/` — модель символов.

Каждый эксперимент содержит:

- `weights/best.pt` - лучшая модель;
- `weights/last.pt` - последний чекпоинт;
- `results.png` - графики метрик
- `confusion_matrix.png` - матрица ошибок
- `train_batch*.jpg` - примеры батчей обучения
- `val_batch*.jpg` - примеры валидации

### Продолжение обучения

Если обучение было прервано, можно продолжить с последнего чекпоинта:

```python
from ultralytics import YOLO

model = YOLO("runs/detect/old_tatar_yolov8/weights/last.pt")
model.train(resume=True)
```

## Использование обученной модели

### Вариант 1: Standalone OCR (только распознавание одной моделью)

```bash
python inference.py --source path/to/image.jpg --model runs/symbols/symbols_yolov8x/weights/best.pt
```

### Вариант 2: Каскад строк → слов → символов (как в статье)

```bash
python cascade_inference.py --image path/to/image.jpg
```

При необходимости можно явно указать пути к трём моделям каскада:

```bash
python cascade_inference.py \
    --image path/to/image.jpg \
    --lines-model runs/lines/lines_yolov8n/weights/best.pt \
    --words-model runs/words/words_yolov8n/weights/best.pt \
    --symbols-model runs/symbols/symbols_yolov8x/weights/best.pt
```

### Вариант 3: Мультиагентная система (OCR + LLM коррекция + транслитерация) ⭐ Рекомендуется

```bash
python main_pipeline.py --image path/to/image.jpg
```

Мультиагентная система автоматически:
1. Распознает текст с помощью OCR;
2. Исправляет ошибки с помощью LLM;
3. Проводит лексический анализ;
4. Выполняет транслитерацию распознанного текста;
5. Выводит детальные результаты.

Подробнее см. [AGENTS_README.md](AGENTS_README.md)

### Распознавание на папке с изображениями

```bash
python inference.py --source path/to/images/ --model runs/detect/old_tatar_yolov8/weights/best.pt
```

### Параметры инференса

```bash
python inference.py \
    --source path/to/image.jpg \
    --model runs/detect/old_tatar_yolov8/weights/best.pt \
    --conf 0.25 \
    --output results
```

Параметры:
- `--source`: Путь к изображению или папке с изображениями
- `--model`: Путь к обученной модели (.pt файл)
- `--conf`: Порог уверенности (0.0-1.0, по умолчанию 0.25)
- `--output`: Папка для сохранения результатов

### Валидация модели

Проверка качества модели на тестовом наборе:

```bash
python validate.py --model runs/detect/old_tatar_yolov8/weights/best.pt
```

Параметры:
- `--model`: Путь к обученной модели
- `--data`: Путь к файлу data.yaml (по умолчанию dataset/data.yaml)
- `--conf`: Порог уверенности для валидации

### Экспорт модели

Экспорт модели в другие форматы (ONNX, TorchScript, TensorRT и др.):

```bash
# Экспорт в ONNX
python export_model.py --model runs/detect/old_tatar_yolov8/weights/best.pt --formats onnx

# Экспорт в несколько форматов
python export_model.py --model runs/detect/old_tatar_yolov8/weights/best.pt --formats onnx torchscript
```

Параметры:
- `--model`: Путь к обученной модели
- `--formats`: Форматы для экспорта (onnx, torchscript, engine, coreml, tflite и др.)
- `--imgsz`: Размер изображений для экспорта

### Использование в Python коде

```python
from ultralytics import YOLO

# Загрузка модели
model = YOLO("runs/detect/old_tatar_yolov8/weights/best.pt")

# Распознавание
results = model.predict("path/to/image.jpg", conf=0.25)

# Обработка результатов
for result in results:
    boxes = result.boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names[cls]
        print(f"Класс: {class_name}, Уверенность: {conf:.2%}")
```

Более подробные примеры использования можно найти в файле `example_usage.py`.

## Структура проекта

```
teuro/
├── download_dataset.py    # Скрипт загрузки датасета
├── train.py               # Скрипт обучения модели
├── inference.py           # Скрипт распознавания (standalone)
├── cascade_inference.py   # Каскад строк → слов → символов
├── main_pipeline.py       # Главный файл мультиагентной системы
├── validate.py            # Скрипт валидации модели
├── export_model.py        # Скрипт экспорта модели
├── example_usage.py       # Примеры использования
├── requirements.txt       # Python зависимости
├── README.md             # Основная документация
├── AGENTS_README.md      # Документация по мультиагентной системе
├── QUICKSTART.md         # Быстрый старт
├── .gitignore            # Git ignore файл
├── agents/               # Модуль агентов
│   ├── __init__.py
│   ├── ocr_agent.py               # OCR агент (YOLOv8)
│   ├── llm_correction_agent.py    # LLM агент коррекции
│   ├── transliteration_agent.py   # Агент транслитерации
│   └── multi_agent_orchestrator.py  # Оркестратор LangGraph
├── config/               # Конфигурация
│   └── settings.py
├── dataset/              # Датасет (создается после загрузки)
│   ├── data.yaml
│   ├── train/
│   ├── val/
│   └── test/
├── runs/                 # Результаты обучения
│   └── detect/
│       └── old_tatar_yolov8/
│           ├── weights/
│           │   ├── best.pt
│           │   └── last.pt
│           └── ...
└── results/              # Результаты распознавания
    └── predictions/
```

## Устранение проблем

### Проблема: CUDA недоступна

1. Убедитесь, что установлены правильные версии CUDA и cuDNN
2. Проверьте, что PyTorch установлен с поддержкой CUDA:
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
3. Проверьте драйверы NVIDIA: `nvidia-smi`

### Проблема: Out of Memory (OOM)

Уменьшите размер батча в `train.py`:
```python
batch=8  # или даже 4
```

Или уменьшите размер изображений:
```python
imgsz=416  # вместо 640
```

### Проблема: Медленное обучение

1. Убедитесь, что используется GPU, а не CPU
2. Увеличьте размер батча (если позволяет память)
3. Используйте меньшую модель (nano или small)

### Проблема: Низкая точность

1. Увеличьте количество эпох обучения
2. Используйте большую модель (small, medium)
3. Проверьте качество датасета
4. Попробуйте аугментации данных

## Дополнительные ресурсы

- [Документация YOLOv8](https://docs.ultralytics.com/)
- [Roboflow Universe](https://universe.roboflow.com/)
- [PyTorch CUDA Installation](https://pytorch.org/get-started/locally/)
- [Статья-источник](https://kpfu.ru//staff_files/F_1714774402/852_Tekst_stati_1392_1_10_20240905.pdf)

## Лицензия

Проект создан в образовательных целях на основе исследования Валишина И.А.

## Автор

Проект основан на статье:
**Валишин И.А.** Применение методов компьютерного зрения к распознаванию старотатарского текста // Электронные библиотеки. 2024. Т. 27. № 4

