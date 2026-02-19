# Мультиагентная система обработки старотатарского текста

Система использует архитектуру на основе **LangGraph** для координации работы двух ИИ-агентов:
1. **OCR агент** - распознавание текста с помощью YOLOv8
2. **LLM агент** - исправление ошибок и лексический анализ

## Архитектура

```
┌─────────────┐
│  Изображение │
└──────┬───────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│ OCR Agent   │─────▶│ LLM Agent    │─────▶│  Результаты │
│ (YOLOv8)    │      │ (tweety-tatar│      │             │
└─────────────┘      │  -base)       │      └─────────────┘
                     └──────────────┘
```

## Компоненты

### 1. OCR Agent (`agents/ocr_agent.py`)

Агент для оптического распознавания символов на основе YOLOv8.

**Функции:**
- Детекция текстовых регионов на изображении
- Извлечение текста из обнаруженных регионов
- Сортировка регионов по позиции (сверху вниз, слева направо)

**Вход:** Путь к изображению  
**Выход:** Распознанный текст, координаты регионов, уверенность

### 2. LLM Correction Agent (`agents/llm_correction_agent.py`)

Агент для исправления ошибок распознавания и лексического анализа.

**Поддерживаемые модели:**
- `neurotatarlar/tweety-tatar-base` - LLM на основе Mistral-7B-Instruct-v0.2 (рекомендуется)
- `ai-forever/mGPT-1.3B-tatar` - модель на основе mGPT-XL
- Любая модель через HuggingFace Transformers
- Модели через Ollama (если установлен)

**Функции:**
- Исправление ошибок OCR
- Нормализация орфографии старотатарского языка
- Лексический анализ (токены, части речи)
- Оценка уверенности коррекции

**Вход:** Распознанный текст от OCR агента  
**Выход:** Исправленный текст, список исправлений, лексический анализ

### 3. Multi-Agent Orchestrator (`agents/multi_agent_orchestrator.py`)

Оркестратор, управляющий потоком данных между агентами через LangGraph.

**Функции:**
- Координация работы агентов
- Управление состоянием пайплайна
- Обработка ошибок
- Формирование финальных результатов

## Установка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Установка LLM модели (опционально)

#### Вариант A: Использование HuggingFace модели

Модель будет автоматически загружена при первом использовании:

```python
# Модель tweety-tatar-base будет загружена автоматически
llm_agent = LLMCorrectionAgent(
    model_name="neurotatarlar/tweety-tatar-base",
    model_type="huggingface"
)
```

#### Вариант B: Использование Ollama

1. Установите Ollama: https://ollama.ai
2. Загрузите модель:
```bash
ollama pull mistral  # или другая модель
```
3. Используйте в коде:
```python
llm_agent = LLMCorrectionAgent(
    model_name="mistral",
    model_type="ollama"
)
```

## Использование

### Базовое использование

```bash
python main_pipeline.py --image path/to/image.jpg
```

### С настройками

```bash
python main_pipeline.py \
    --image path/to/image.jpg \
    --ocr-model runs/detect/old_tatar_yolov8/weights/best.pt \
    --ocr-conf 0.25 \
    --llm-model neurotatarlar/tweety-tatar-base \
    --llm-type huggingface \
    --output results.json
```

### Использование в Python коде

```python
from agents.multi_agent_orchestrator import MultiAgentOrchestrator

# Инициализация оркестратора
orchestrator = MultiAgentOrchestrator(
    ocr_model_path="runs/detect/old_tatar_yolov8/weights/best.pt",
    llm_model_name="neurotatarlar/tweety-tatar-base",
    llm_model_type="huggingface"
)

# Обработка изображения
result = orchestrator.process("path/to/image.jpg")

# Получение результатов
print(f"Исходный текст: {result['raw_text']}")
print(f"Исправленный текст: {result['corrected_text']}")
print(f"Лексический анализ: {result['lexical_analysis']}")
```

## Доступные LLM модели

### Для старотатарского языка:

1. **tweety-tatar-base** (рекомендуется)
   - Модель: `neurotatarlar/tweety-tatar-base`
   - Основа: Mistral-7B-Instruct-v0.2
   - Специализирована для татарского языка

2. **mGPT-1.3B-tatar**
   - Модель: `ai-forever/mGPT-1.3B-tatar`
   - Основа: mGPT-XL
   - Поддержка множества тюркских языков

### Альтернативные варианты:

- Использование Ollama с любой моделью (mistral, llama2, и т.д.)
- Fine-tuned модели на вашем датасете

## Конфигурация

Настройки можно задать через переменные окружения (файл `.env`):

```env
OCR_MODEL_PATH=runs/detect/old_tatar_yolov8/weights/best.pt
OCR_CONFIDENCE_THRESHOLD=0.25
LLM_MODEL_NAME=neurotatarlar/tweety-tatar-base
LLM_MODEL_TYPE=huggingface
LLM_DEVICE=cuda
CUDA_DEVICE=0
```

Или через код:

```python
from config.settings import Settings

settings = Settings(
    LLM_MODEL_NAME="neurotatarlar/tweety-tatar-base",
    LLM_MODEL_TYPE="huggingface"
)
```

## Примеры вывода

### Успешная обработка:

```
======================================================================
РЕЗУЛЬТАТЫ ОБРАБОТКИ
======================================================================

📸 OCR РЕЗУЛЬТАТЫ:
  • Изображение: image.jpg
  • Обнаружено регионов: 15
  • Средняя уверенность OCR: 87.50%
  • Исходный текст:
    [class_0] [class_1] [class_2] ...

🤖 LLM РЕЗУЛЬТАТЫ:
  • Исправлений внесено: 3
  • Уверенность коррекции: 92.00%
  • Исправленный текст:
    Исправленный старотатарский текст здесь...

  📝 ДЕТАЛИ ИСПРАВЛЕНИЙ:
    1. 'слово1' → 'слово1_исправленное'
       Причина: исправление ошибки OCR
    2. 'слово2' → 'слово2_исправленное'
       Причина: нормализация орфографии

  📊 ЛЕКСИЧЕСКИЙ АНАЛИЗ:
    • Всего слов: 25
    • Уникальных слов: 18
    • Токены: слово1, слово2, слово3...

✅ Статус: Успешно
======================================================================
```

## Устранение проблем

### Проблема: LLM модель не загружается

1. Проверьте доступность модели на HuggingFace
2. Убедитесь, что у вас достаточно памяти (модели требуют 4-8 GB RAM)
3. Попробуйте использовать меньшую модель или Ollama

### Проблема: Медленная работа LLM

1. Используйте GPU: `--llm-device cuda`
2. Используйте квантованную модель (8-bit или 4-bit)
3. Используйте Ollama для оптимизированной инференса

### Проблема: Низкое качество коррекции

1. Попробуйте другую модель (tweety-tatar-base обычно лучше)
2. Fine-tune модель на вашем датасете
3. Улучшите качество OCR (обучите модель лучше)

## Расширение системы

### Добавление нового агента

```python
from langgraph.graph import StateGraph, START, END

class NewAgentState(TypedDict):
    # Определите состояние агента
    pass

def new_agent_step(state: PipelineState) -> PipelineState:
    # Реализуйте логику агента
    return state

# Добавьте в оркестратор
workflow.add_node("new_agent", new_agent_step)
workflow.add_edge("llm_step", "new_agent")
workflow.add_edge("new_agent", "finalize")
```

## Дополнительные ресурсы

- [LangGraph документация](https://langchain-ai.github.io/langgraph/)
- [tweety-tatar-base на HuggingFace](https://huggingface.co/neurotatarlar/tweety-tatar-base)
- [Awesome Tatar репозиторий](https://github.com/neurotatarlar/awesome-tatar)

