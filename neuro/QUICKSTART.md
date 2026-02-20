# Быстрый старт

Краткая инструкция для быстрого запуска проекта.

## 1. Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/macOS)
source venv/bin/activate

# Установка PyTorch с CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Установка остальных зависимостей
pip install -r requirements.txt
```

## 2. Загрузка датасетов

```bash
# Установите переменную окружения с API ключом Roboflow
# Windows PowerShell:
$env:ROBOFLOW_API_KEY="ваш_api_ключ"

# Windows CMD:
set ROBOFLOW_API_KEY=ваш_api_ключ

# Linux/macOS:
export ROBOFLOW_API_KEY="ваш_api_ключ"

# Общий датасет (generic)
python download_dataset.py --task generic

# Все три специализированных датасета (строки, слова, символы)
python download_dataset.py --task all
```

## 3. Обучение моделей

### Вариант A: Одна универсальная модель (как раньше)

```bash
python train.py --task generic
```

### Вариант B: Каскад из трёх моделей (строки → слова → символы)

```bash
python train.py --task all
```

## 4. Распознавание текста

### Вариант A: Каскад (строки → слова → символы, как в статье)

```bash
python cascade_inference.py --image path/to/image.jpg
```

### Вариант B: Standalone OCR (одна модель)

```bash
# Распознавание на одном изображении (например, модель символов)
python inference.py --source path/to/image.jpg --model runs/symbols/symbols_yolov8x/weights/best.pt

# Распознавание на папке с изображениями
python inference.py --source path/to/images/ --model runs/symbols/symbols_yolov8x/weights/best.pt
```

### Вариант C: Мультиагентная система (OCR + LLM коррекция) ⭐

```bash
# Базовое использование
python main_pipeline.py --image path/to/image.jpg

# С настройками
python main_pipeline.py \
    --image path/to/image.jpg \
    --llm-model neurotatarlar/tweety-tatar-base \
    --llm-type huggingface \
    --output results.json
```

**Преимущества мультиагентной системы:**
- Автоматическое исправление ошибок OCR
- Лексический анализ текста
- Детальные результаты с объяснениями исправлений

## 5. Валидация модели

```bash
python validate.py
```

## Полезные команды

```bash
# Проверка CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Экспорт модели в ONNX
python export_model.py --formats onnx

# Тест мультиагентной системы
python main_pipeline.py --image test_image.jpg --json-only
```

## Мультиагентная система

Для использования мультиагентной системы с LLM коррекцией:

1. **Установите дополнительные зависимости** (если еще не установлены):
```bash
pip install langgraph langchain transformers
```

2. **Выберите LLM модель:**
   - `neurotatarlar/tweety-tatar-base` (рекомендуется) - автоматически загрузится с HuggingFace
   - Или используйте Ollama: `ollama pull mistral`

3. **Запустите пайплайн:**
```bash
python main_pipeline.py --image path/to/image.jpg
```

Подробнее см. [AGENTS_README.md](AGENTS_README.md)

## Рекомендуемый порядок работы

1. ✅ Установить зависимости
2. ✅ Загрузить датасет
3. ✅ Обучить модель (начните с `model_size="n"` для быстрого теста)
4. ✅ Валидировать модель
5. ✅ Использовать для распознавания

## Проблемы?

См. раздел "Устранение проблем" в `README.md`.

