"""
LLM агент для исправления и лексического анализа старотатарского текста
"""
import os
import json
import torch
from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠ transformers не установлен. LLM агент будет использовать заглушку.")

try:
    from langchain_community.llms import Ollama
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠ langchain не установлен. Будет использован прямой вызов модели.")


class LLMCorrectionState(TypedDict):
    """Состояние LLM агента коррекции"""
    raw_text: str
    corrected_text: str
    corrections: List[Dict[str, Any]]
    lexical_analysis: Dict[str, Any]
    confidence_score: float
    error: str


class LLMCorrectionAgent:
    """
    Агент для исправления текста и лексического анализа с использованием LLM
    Поддерживает модели: tweety-tatar-base, mGPT-1.3B-tatar, или любую другую через HuggingFace/Ollama
    """
    
    def __init__(self, 
                 model_name: str = "neurotatarlar/tweety-tatar-base",
                 model_type: str = "huggingface",  # "huggingface" или "ollama"
                 device: Optional[str] = None):
        """
        Инициализация LLM агента
        
        Args:
            model_name: Имя модели (HuggingFace или Ollama)
            model_type: Тип модели ("huggingface" или "ollama")
            device: Устройство для вычислений ("cuda", "cpu" или None для автоопределения)
        """
        self.model_name = model_name
        self.model_type = model_type
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        if model_type == "huggingface" and TRANSFORMERS_AVAILABLE:
            self._init_huggingface_model()
        elif model_type == "ollama" and LANGCHAIN_AVAILABLE:
            self._init_ollama_model()
        else:
            print("⚠ LLM модель не загружена. Будет использована заглушка.")
            self.model = None
            self.tokenizer = None
    
    def _init_huggingface_model(self):
        """Инициализация модели через HuggingFace Transformers"""
        try:
            print(f"Загрузка модели HuggingFace: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            print(f"✓ Модель загружена на устройство: {self.device}")
        except Exception as e:
            print(f"⚠ Ошибка загрузки модели HuggingFace: {e}")
            print("Будет использована заглушка.")
            self.model = None
            self.tokenizer = None
    
    def _init_ollama_model(self):
        """Инициализация модели через Ollama"""
        try:
            print(f"Инициализация Ollama модели: {self.model_name}")
            self.llm = Ollama(model=self.model_name, temperature=0.1)
            print(f"✓ Ollama модель инициализирована: {self.model_name}")
        except Exception as e:
            print(f"⚠ Ошибка инициализации Ollama: {e}")
            self.llm = None
    
    def create_correction_prompt(self, raw_text: str) -> str:
        """
        Создание промпта для коррекции старотатарского текста
        
        Args:
            raw_text: Исходный текст
            
        Returns:
            Форматированный промпт
        """
        prompt = f"""Ты эксперт по старотатарской письменности и лексике.

Исходный распознанный текст (возможны ошибки OCR):
{raw_text}

Выполни следующие задачи:
1. Исправь ошибки распознавания (неправильные буквы, слова)
2. Приведи текст к стандартной орфографии старотатарского языка
3. Определи основные слова и их части речи
4. Оцени уверенность коррекции (0.0-1.0)

Ответь ТОЛЬКО JSON объектом без дополнительного текста:
{{
    "corrected_text": "исправленный текст здесь",
    "corrections": [
        {{"original": "слово1", "corrected": "слово1_исправленное", "reason": "причина"}},
        {{"original": "слово2", "corrected": "слово2_исправленное", "reason": "причина"}}
    ],
    "lexical_analysis": {{
        "tokens": ["слово1", "слово2"],
        "pos_tags": ["NOUN", "VERB"],
        "word_count": 2,
        "unique_words": 2
    }},
    "confidence": 0.85
}}"""
        return prompt
    
    def correct_and_analyze(self, state: LLMCorrectionState) -> LLMCorrectionState:
        """
        Исправление текста и лексический анализ
        
        Args:
            state: Состояние агента
            
        Returns:
            Обновленное состояние с исправленным текстом
        """
        raw_text = state.get("raw_text", "")
        
        if not raw_text:
            state["error"] = "Пустой текст для коррекции"
            return state
        
        try:
            if self.model_type == "huggingface" and self.model is not None:
                result = self._correct_with_huggingface(raw_text)
            elif self.model_type == "ollama" and hasattr(self, 'llm') and self.llm is not None:
                result = self._correct_with_ollama(raw_text)
            else:
                # Заглушка для тестирования
                result = self._correct_with_stub(raw_text)
            
            # Обновление состояния
            state["corrected_text"] = result.get("corrected_text", raw_text)
            state["corrections"] = result.get("corrections", [])
            state["lexical_analysis"] = result.get("lexical_analysis", {})
            state["confidence_score"] = result.get("confidence", 0.5)
            state["error"] = ""
            
            print(f"✓ LLM коррекция завершена. Уверенность: {state['confidence_score']:.2%}")
            
        except Exception as e:
            state["error"] = f"Ошибка при коррекции текста: {str(e)}"
            import traceback
            traceback.print_exc()
        
        return state
    
    def _correct_with_huggingface(self, text: str) -> Dict[str, Any]:
        """Коррекция с использованием HuggingFace модели"""
        prompt = self.create_correction_prompt(text)
        
        # Токенизация
        inputs = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=1024)
        inputs = inputs.to(self.device)
        
        # Генерация
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=512,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Декодирование
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Извлечение JSON из ответа
        return self._parse_llm_response(generated_text)
    
    def _correct_with_ollama(self, text: str) -> Dict[str, Any]:
        """Коррекция с использованием Ollama"""
        prompt = self.create_correction_prompt(text)
        response = self.llm.invoke(prompt)
        return self._parse_llm_response(response)
    
    def _correct_with_stub(self, text: str) -> Dict[str, Any]:
        """Заглушка для тестирования без реальной модели"""
        words = text.split()
        corrections = []
        
        # Простая заглушка - просто возвращаем текст как есть
        return {
            "corrected_text": text,
            "corrections": corrections,
            "lexical_analysis": {
                "tokens": words,
                "pos_tags": ["UNKNOWN"] * len(words),
                "word_count": len(words),
                "unique_words": len(set(words))
            },
            "confidence": 0.7
        }
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Парсинг ответа LLM в JSON формат
        
        Args:
            response: Ответ от LLM
            
        Returns:
            Распарсенный JSON объект
        """
        try:
            # Попытка найти JSON в ответе
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Если JSON не найден, возвращаем заглушку
                return {
                    "corrected_text": response.strip(),
                    "corrections": [],
                    "lexical_analysis": {
                        "tokens": response.split(),
                        "pos_tags": [],
                        "word_count": len(response.split()),
                        "unique_words": len(set(response.split()))
                    },
                    "confidence": 0.5
                }
        except json.JSONDecodeError:
            # Если парсинг не удался, возвращаем заглушку
            return {
                "corrected_text": response.strip(),
                "corrections": [],
                "lexical_analysis": {},
                "confidence": 0.3
            }


def create_llm_agent(model_name: str = "neurotatarlar/tweety-tatar-base",
                     model_type: str = "huggingface",
                     device: Optional[str] = None) -> StateGraph:
    """
    Создание графа LLM агента с использованием LangGraph
    
    Args:
        model_name: Имя модели
        model_type: Тип модели ("huggingface" или "ollama")
        device: Устройство для вычислений
        
    Returns:
        Скомпилированный граф агента
    """
    llm = LLMCorrectionAgent(model_name=model_name, model_type=model_type, device=device)
    
    # Создание графа
    workflow = StateGraph(LLMCorrectionState)
    
    # Добавление узла обработки
    workflow.add_node("llm_correction", llm.correct_and_analyze)
    
    # Определение потока
    workflow.add_edge(START, "llm_correction")
    workflow.add_edge("llm_correction", END)
    
    return workflow.compile()

