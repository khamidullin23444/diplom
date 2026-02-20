"""
Оркестратор для связи OCR и LLM агентов через LangGraph
"""
from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END
from .ocr_agent import OCRAgent
from .llm_correction_agent import LLMCorrectionAgent
from .transliteration_agent import TransliterationAgent


class PipelineState(TypedDict):
    """Общее состояние пайплайна обработки"""
    image_path: str
    detected_regions: List[Dict[str, Any]]
    raw_text: str
    confidence_scores: List[float]
    corrected_text: str
    corrections: List[Dict[str, Any]]
    lexical_analysis: Dict[str, Any]
    confidence_score: float
    transliteration: str
    final_result: Dict[str, Any]
    error: str


class MultiAgentOrchestrator:
    """
    Оркестратор для управления потоком данных между OCR и LLM агентами
    """
    
    def __init__(self, 
                 ocr_model_path: str = "runs/detect/old_tatar_yolov8/weights/best.pt",
                 ocr_conf_threshold: float = 0.25,
                 llm_model_name: str = "neurotatarlar/tweety-tatar-base",
                 llm_model_type: str = "huggingface",
                 llm_device: Optional[str] = None):
        """
        Инициализация оркестратора
        
        Args:
            ocr_model_path: Путь к модели OCR
            ocr_conf_threshold: Порог уверенности для OCR
            llm_model_name: Имя LLM модели
            llm_model_type: Тип LLM модели ("huggingface" или "ollama")
            llm_device: Устройство для LLM
        """
        print("Инициализация агентов...")
        self.ocr_agent = OCRAgent(
            model_path=ocr_model_path,
            conf_threshold=ocr_conf_threshold
        )
        self.llm_agent = LLMCorrectionAgent(
            model_name=llm_model_name,
            model_type=llm_model_type,
            device=llm_device
        )
        self.translit_agent = TransliterationAgent()
        print("✓ Агенты инициализированы")
    
    def ocr_step(self, state: PipelineState) -> PipelineState:
        """
        Шаг 1: OCR детекция и извлечение текста
        
        Args:
            state: Текущее состояние пайплайна
            
        Returns:
            Обновленное состояние после OCR
        """
        print("\n" + "="*60)
        print("ШАГ 1: OCR РАСПОЗНАВАНИЕ")
        print("="*60)
        
        ocr_state = {
            "image_path": state.get("image_path", ""),
            "detected_regions": [],
            "raw_text": "",
            "confidence_scores": [],
            "error": ""
        }
        
        ocr_state = self.ocr_agent.detect_and_extract(ocr_state)
        
        # Обновление состояния пайплайна
        state["detected_regions"] = ocr_state.get("detected_regions", [])
        state["raw_text"] = ocr_state.get("raw_text", "")
        state["confidence_scores"] = ocr_state.get("confidence_scores", [])
        
        if ocr_state.get("error"):
            state["error"] = f"OCR ошибка: {ocr_state['error']}"
        
        return state
    
    def llm_step(self, state: PipelineState) -> PipelineState:
        """
        Шаг 2: LLM коррекция и лексический анализ
        
        Args:
            state: Текущее состояние пайплайна
            
        Returns:
            Обновленное состояние после LLM обработки
        """
        print("\n" + "="*60)
        print("ШАГ 2: LLM КОРРЕКЦИЯ И АНАЛИЗ")
        print("="*60)
        
        # Проверка наличия ошибок от предыдущего шага
        if state.get("error"):
            print(f"⚠ Пропуск LLM шага из-за ошибки: {state['error']}")
            return state
        
        raw_text = state.get("raw_text", "")
        if not raw_text:
            state["error"] = "Пустой текст для коррекции"
            return state
        
        llm_state = {
            "raw_text": raw_text,
            "corrected_text": "",
            "corrections": [],
            "lexical_analysis": {},
            "confidence_score": 0.0,
            "error": ""
        }
        
        llm_state = self.llm_agent.correct_and_analyze(llm_state)
        
        # Обновление состояния пайплайна
        state["corrected_text"] = llm_state.get("corrected_text", "")
        state["corrections"] = llm_state.get("corrections", [])
        state["lexical_analysis"] = llm_state.get("lexical_analysis", {})
        state["confidence_score"] = llm_state.get("confidence_score", 0.0)
        
        if llm_state.get("error"):
            state["error"] = f"LLM ошибка: {llm_state['error']}"
        
        return state

    def translit_step(self, state: PipelineState) -> PipelineState:
        """
        Шаг 3: Транслитерация распознанного/исправленного текста.

        Args:
            state: Текущее состояние пайплайна

        Returns:
            Обновлённое состояние с полем transliteration
        """
        print("\n" + "=" * 60)
        print("ШАГ 3: ТРАНСЛИТЕРАЦИЯ")
        print("=" * 60)

        if state.get("error"):
            print(f"⚠ Пропуск шага транслитерации из-за ошибки: {state['error']}")
            return state

        # В качестве основы берём уже исправленный текст, если он есть,
        # иначе — сырой текст OCR (например, последовательность классов).
        text_for_translit = state.get("corrected_text") or state.get("raw_text", "")

        translit_state = {
            "raw_text": text_for_translit,
            "transliteration": "",
            "error": "",
        }

        translit_state = self.translit_agent.transliterate(translit_state)

        if translit_state.get("error"):
            state["error"] = f"Ошибка транслитерации: {translit_state['error']}"
        else:
            state["transliteration"] = translit_state.get("transliteration", "")

        return state
    
    def finalize_step(self, state: PipelineState) -> PipelineState:
        """
        Шаг 3: Финализация результатов
        
        Args:
            state: Текущее состояние пайплайна
            
        Returns:
            Финальное состояние с результатами
        """
        print("\n" + "="*60)
        print("ШАГ 4: ФИНАЛИЗАЦИЯ")
        print("="*60)
        
        # Формирование финального результата
        final_result = {
            "source_image": state.get("image_path", ""),
            "ocr_results": {
                "detected_regions_count": len(state.get("detected_regions", [])),
                "raw_text": state.get("raw_text", ""),
                "average_confidence": (
                    sum(state.get("confidence_scores", [])) / len(state.get("confidence_scores", [1]))
                    if state.get("confidence_scores") else 0.0
                )
            },
            "llm_results": {
                "corrected_text": state.get("corrected_text", ""),
                "corrections_count": len(state.get("corrections", [])),
                "corrections": state.get("corrections", []),
                "lexical_analysis": state.get("lexical_analysis", {}),
                "confidence_score": state.get("confidence_score", 0.0)
            },
            "summary": {
                "success": not bool(state.get("error")),
                "error": state.get("error", ""),
                "total_processing_time": "N/A"  # Можно добавить измерение времени
            },
            "transliteration": state.get("transliteration", ""),
        }
        
        state["final_result"] = final_result
        
        return state
    
    def create_pipeline(self) -> StateGraph:
        """
        Создание полного пайплайна обработки
        
        Returns:
            Скомпилированный граф пайплайна
        """
        print("\nСоздание пайплайна обработки...")
        
        # Создание графа
        workflow = StateGraph(PipelineState)
        
        # Добавление узлов
        workflow.add_node("ocr_step", self.ocr_step)
        workflow.add_node("llm_step", self.llm_step)
        workflow.add_node("translit_step", self.translit_step)
        workflow.add_node("finalize", self.finalize_step)
        
        # Определение потока обработки
        workflow.add_edge(START, "ocr_step")
        workflow.add_edge("ocr_step", "llm_step")
        workflow.add_edge("llm_step", "translit_step")
        workflow.add_edge("translit_step", "finalize")
        workflow.add_edge("finalize", END)
        
        print("✓ Пайплайн создан")
        
        return workflow.compile()
    
    def process(self, image_path: str) -> PipelineState:
        """
        Обработка изображения через весь пайплайн
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            Финальное состояние с результатами обработки
        """
        pipeline = self.create_pipeline()
        
        # Начальное состояние
        initial_state: PipelineState = {
            "image_path": image_path,
            "detected_regions": [],
            "raw_text": "",
            "confidence_scores": [],
            "corrected_text": "",
            "corrections": [],
            "lexical_analysis": {},
            "confidence_score": 0.0,
            "final_result": {},
            "error": ""
        }
        
        # Запуск пайплайна
        result = pipeline.invoke(initial_state)
        
        return result


def create_multi_agent_pipeline(
    ocr_model_path: str = "runs/detect/old_tatar_yolov8/weights/best.pt",
    ocr_conf_threshold: float = 0.25,
    llm_model_name: str = "neurotatarlar/tweety-tatar-base",
    llm_model_type: str = "huggingface",
    llm_device: Optional[str] = None
) -> StateGraph:
    """
    Фабричная функция для создания мультиагентного пайплайна
    
    Args:
        ocr_model_path: Путь к модели OCR
        ocr_conf_threshold: Порог уверенности для OCR
        llm_model_name: Имя LLM модели
        llm_model_type: Тип LLM модели
        llm_device: Устройство для LLM
        
    Returns:
        Скомпилированный граф пайплайна
    """
    orchestrator = MultiAgentOrchestrator(
        ocr_model_path=ocr_model_path,
        ocr_conf_threshold=ocr_conf_threshold,
        llm_model_name=llm_model_name,
        llm_model_type=llm_model_type,
        llm_device=llm_device
    )
    
    return orchestrator.create_pipeline()

