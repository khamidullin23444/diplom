"""
Главный файл для запуска мультиагентной системы обработки старотатарского текста
"""
import os
import json
import argparse
from pathlib import Path
from agents.multi_agent_orchestrator import MultiAgentOrchestrator


def print_results(result: dict):
    """
    Красивый вывод результатов обработки
    
    Args:
        result: Словарь с результатами обработки
    """
    print("\n" + "="*70)
    print("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
    print("="*70)
    
    if result.get("summary", {}).get("error"):
        print(f"\n❌ ОШИБКА: {result['summary']['error']}")
        return
    
    # OCR результаты
    ocr_results = result.get("ocr_results", {})
    print(f"\n📸 OCR РЕЗУЛЬТАТЫ:")
    print(f"  • Изображение: {result.get('source_image', 'N/A')}")
    print(f"  • Обнаружено регионов: {ocr_results.get('detected_regions_count', 0)}")
    print(f"  • Средняя уверенность OCR: {ocr_results.get('average_confidence', 0):.2%}")
    print(f"  • Исходный текст:")
    print(f"    {ocr_results.get('raw_text', 'N/A')}")
    
    # LLM результаты
    llm_results = result.get("llm_results", {})
    print(f"\n🤖 LLM РЕЗУЛЬТАТЫ:")
    print(f"  • Исправлений внесено: {llm_results.get('corrections_count', 0)}")
    print(f"  • Уверенность коррекции: {llm_results.get('confidence_score', 0):.2%}")
    print(f"  • Исправленный текст:")
    print(f"    {llm_results.get('corrected_text', 'N/A')}")
    
    # Исправления
    corrections = llm_results.get("corrections", [])
    if corrections:
        print(f"\n  📝 ДЕТАЛИ ИСПРАВЛЕНИЙ:")
        for i, corr in enumerate(corrections, 1):
            print(f"    {i}. '{corr.get('original', '')}' → '{corr.get('corrected', '')}'")
            if corr.get('reason'):
                print(f"       Причина: {corr['reason']}")
    
    # Лексический анализ
    lexical = llm_results.get("lexical_analysis", {})
    if lexical:
        print(f"\n  📊 ЛЕКСИЧЕСКИЙ АНАЛИЗ:")
        print(f"    • Всего слов: {lexical.get('word_count', 0)}")
        print(f"    • Уникальных слов: {lexical.get('unique_words', 0)}")
        if lexical.get("tokens"):
            print(f"    • Токены: {', '.join(lexical['tokens'][:10])}{'...' if len(lexical['tokens']) > 10 else ''}")
    
    # Итог
    print(f"\n✅ Статус: {'Успешно' if result.get('summary', {}).get('success') else 'Ошибка'}")
    print("="*70)


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description="Мультиагентная система для распознавания и исправления старотатарского текста"
    )
    
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Путь к изображению для обработки"
    )
    
    parser.add_argument(
        "--ocr-model",
        type=str,
        default="runs/detect/old_tatar_yolov8/weights/best.pt",
        help="Путь к модели OCR"
    )
    
    parser.add_argument(
        "--ocr-conf",
        type=float,
        default=0.25,
        help="Порог уверенности для OCR (0.0-1.0)"
    )
    
    parser.add_argument(
        "--llm-model",
        type=str,
        default="neurotatarlar/tweety-tatar-base",
        help="Имя LLM модели (HuggingFace или Ollama)"
    )
    
    parser.add_argument(
        "--llm-type",
        type=str,
        choices=["huggingface", "ollama"],
        default="huggingface",
        help="Тип LLM модели"
    )
    
    parser.add_argument(
        "--llm-device",
        type=str,
        default=None,
        help="Устройство для LLM (cuda/cpu, по умолчанию автоопределение)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Путь для сохранения результатов в JSON (опционально)"
    )
    
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Вывести только JSON без форматирования"
    )
    
    args = parser.parse_args()
    
    # Проверка существования изображения
    if not os.path.exists(args.image):
        print(f"❌ Ошибка: Изображение не найдено: {args.image}")
        return 1
    
    print("="*70)
    print("МУЛЬТИАГЕНТНАЯ СИСТЕМА ОБРАБОТКИ СТАРОТАТАРСКОГО ТЕКСТА")
    print("="*70)
    print(f"\nПараметры:")
    print(f"  • Изображение: {args.image}")
    print(f"  • OCR модель: {args.ocr_model}")
    print(f"  • OCR порог уверенности: {args.ocr_conf}")
    print(f"  • LLM модель: {args.llm_model}")
    print(f"  • LLM тип: {args.llm_type}")
    print(f"  • LLM устройство: {args.llm_device or 'автоопределение'}")
    
    # Инициализация оркестратора
    try:
        orchestrator = MultiAgentOrchestrator(
            ocr_model_path=args.ocr_model,
            ocr_conf_threshold=args.ocr_conf,
            llm_model_name=args.llm_model,
            llm_model_type=args.llm_type,
            llm_device=args.llm_device
        )
    except Exception as e:
        print(f"\n❌ Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Обработка изображения
    try:
        result_state = orchestrator.process(args.image)
        final_result = result_state.get("final_result", {})
        
        # Вывод результатов
        if args.json_only:
            print(json.dumps(final_result, ensure_ascii=False, indent=2))
        else:
            print_results(final_result)
        
        # Сохранение результатов
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Результаты сохранены в: {args.output}")
        
        return 0 if final_result.get("summary", {}).get("success") else 1
        
    except Exception as e:
        print(f"\n❌ Ошибка при обработке: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

