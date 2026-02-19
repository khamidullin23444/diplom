"""
Примеры использования мультиагентной системы
"""
import json
from agents.multi_agent_orchestrator import MultiAgentOrchestrator
from agents.ocr_agent import create_ocr_agent
from agents.llm_correction_agent import create_llm_agent


def example_basic_pipeline():
    """Пример 1: Базовое использование мультиагентной системы"""
    print("="*70)
    print("ПРИМЕР 1: Базовое использование")
    print("="*70)
    
    # Инициализация оркестратора
    orchestrator = MultiAgentOrchestrator(
        ocr_model_path="runs/detect/old_tatar_yolov8/weights/best.pt",
        llm_model_name="neurotatarlar/tweety-tatar-base",
        llm_model_type="huggingface"
    )
    
    # Обработка изображения
    result = orchestrator.process("path/to/image.jpg")
    
    # Вывод результатов
    print(f"\nИсходный текст (OCR): {result['raw_text']}")
    print(f"Исправленный текст: {result['corrected_text']}")
    print(f"Уверенность: {result['confidence_score']:.2%}")


def example_custom_agents():
    """Пример 2: Использование отдельных агентов"""
    print("\n" + "="*70)
    print("ПРИМЕР 2: Использование отдельных агентов")
    print("="*70)
    
    # Создание OCR агента
    ocr_agent = create_ocr_agent(
        model_path="runs/detect/old_tatar_yolov8/weights/best.pt",
        conf_threshold=0.25
    )
    
    # Запуск OCR
    ocr_state = {
        "image_path": "path/to/image.jpg",
        "detected_regions": [],
        "raw_text": "",
        "confidence_scores": [],
        "error": ""
    }
    ocr_result = ocr_agent.invoke(ocr_state)
    
    print(f"OCR результат: {ocr_result['raw_text']}")
    
    # Создание LLM агента
    llm_agent = create_llm_agent(
        model_name="neurotatarlar/tweety-tatar-base",
        model_type="huggingface"
    )
    
    # Запуск LLM коррекции
    llm_state = {
        "raw_text": ocr_result['raw_text'],
        "corrected_text": "",
        "corrections": [],
        "lexical_analysis": {},
        "confidence_score": 0.0,
        "error": ""
    }
    llm_result = llm_agent.invoke(llm_state)
    
    print(f"LLM результат: {llm_result['corrected_text']}")


def example_with_ollama():
    """Пример 3: Использование Ollama вместо HuggingFace"""
    print("\n" + "="*70)
    print("ПРИМЕР 3: Использование Ollama")
    print("="*70)
    
    orchestrator = MultiAgentOrchestrator(
        ocr_model_path="runs/detect/old_tatar_yolov8/weights/best.pt",
        llm_model_name="mistral",  # Или другая модель в Ollama
        llm_model_type="ollama"
    )
    
    result = orchestrator.process("path/to/image.jpg")
    print(f"Результат: {result['corrected_text']}")


def example_batch_processing():
    """Пример 4: Пакетная обработка нескольких изображений"""
    print("\n" + "="*70)
    print("ПРИМЕР 4: Пакетная обработка")
    print("="*70)
    
    orchestrator = MultiAgentOrchestrator(
        ocr_model_path="runs/detect/old_tatar_yolov8/weights/best.pt",
        llm_model_name="neurotatarlar/tweety-tatar-base"
    )
    
    image_paths = [
        "path/to/image1.jpg",
        "path/to/image2.jpg",
        "path/to/image3.jpg"
    ]
    
    results = []
    for image_path in image_paths:
        print(f"\nОбработка: {image_path}")
        result = orchestrator.process(image_path)
        results.append({
            "image": image_path,
            "corrected_text": result['corrected_text'],
            "confidence": result['confidence_score']
        })
    
    # Сохранение результатов
    with open("batch_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nОбработано {len(results)} изображений. Результаты сохранены в batch_results.json")


def example_custom_configuration():
    """Пример 5: Кастомная конфигурация"""
    print("\n" + "="*70)
    print("ПРИМЕР 5: Кастомная конфигурация")
    print("="*70)
    
    orchestrator = MultiAgentOrchestrator(
        ocr_model_path="runs/detect/old_tatar_yolov8/weights/best.pt",
        ocr_conf_threshold=0.3,  # Более строгий порог
        llm_model_name="neurotatarlar/tweety-tatar-base",
        llm_model_type="huggingface",
        llm_device="cuda"  # Принудительное использование GPU
    )
    
    result = orchestrator.process("path/to/image.jpg")
    
    # Детальный вывод
    print("\nДетальные результаты:")
    print(json.dumps(result['final_result'], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    print("Примеры использования мультиагентной системы")
    print("\nПримечание: Раскомментируйте нужный пример для запуска")
    
    # Раскомментируйте нужный пример:
    # example_basic_pipeline()
    # example_custom_agents()
    # example_with_ollama()
    # example_batch_processing()
    # example_custom_configuration()

