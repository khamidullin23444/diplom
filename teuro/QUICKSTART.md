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

## 2. Загрузка датасета

```bash
# Установите переменную окружения с API ключом Roboflow
# Windows PowerShell:
$env:ROBOFLOW_API_KEY="ваш_api_ключ"

# Windows CMD:
set ROBOFLOW_API_KEY=ваш_api_ключ

# Linux/macOS:
export ROBOFLOW_API_KEY="ваш_api_ключ"

# Загрузка датасета
python download_dataset.py
```

## 3. Обучение модели

```bash
# Базовое обучение (начните с nano модели для быстрого теста)
python train.py
```

Для настройки параметров откройте `train.py` и измените значения в функции `train_model()`.

## 4. Распознавание текста

### Вариант A: Standalone OCR (только распознавание)

```bash
# Распознавание на одном изображении
python inference.py --source path/to/image.jpg

# Распознавание на папке с изображениями
python inference.py --source path/to/images/
```

### Вариант B: Мультиагентная система (OCR + LLM коррекция) ⭐

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

