"""
Агент транслитерации последовательности распознанных арабских/старотатарских символов
в удобочитаемую латиницу/кириллицу.

Предполагается, что на вход подаётся строка вида:
    "[A] [K] [Iy] ..."
или последовательность имён классов YOLO:
    "A K Iy ..."
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class TransliterationState(TypedDict):
    """Состояние агента транслитерации."""

    raw_text: str          # исходный текст после OCR/LLM (может быть последовательность классов)
    transliteration: str   # результат транслитерации
    error: str


class TransliterationAgent:
    """
    Агент транслитерации, использующий простую таблицу соответствий
    между классами YOLO (A, Wau, Iy, ...) и целевым алфавитом.
    """

    def __init__(self):
        # Базовое соответствие классов из статьи (22 класса) -> условная латиница.
        # Эти соответствия можно скорректировать под нужную систему транслитерации.
        self.class_to_lat = {
            "A": "a",
            "Wau": "u",
            "Iy": "i",
            "N": "n",
            "K": "k",
            "R": "r",
            "L": "l",
            "D": "d",
            "B": "b",
            "T": "t",
            "M": "m",
            "S": "s",
            "Ha": "h",
            "G": "g",
            "Sh": "ş",
            "La": "la",
            "Z": "z",
            "F": "f",
            "Ta": "ṭ",
            "h": "h",
            "Zzh": "ẓ",
        }

    def transliterate(self, state: TransliterationState) -> TransliterationState:
        """
        Простейшая транслитерация: разбираем последовательность классов и
        конкатенируем латинские эквиваленты.
        """
        raw = state.get("raw_text", "")
        if not raw:
            state["error"] = "Пустой текст для транслитерации"
            return state

        # Удаляем возможные скобки [A], [K], ... -> A, K, ...
        tokens = []
        for part in raw.split():
            token = part.strip()
            if token.startswith("[") and token.endswith("]"):
                token = token[1:-1]
            tokens.append(token)

        # Применяем таблицу соответствий
        result_chars = []
        for tok in tokens:
            mapped = self.class_to_lat.get(tok, tok)
            result_chars.append(mapped)

        state["transliteration"] = "".join(result_chars)
        state["error"] = ""
        return state


def create_transliteration_agent() -> StateGraph:
    """
    Создание графа агента транслитерации для использования отдельно при необходимости.
    """
    agent = TransliterationAgent()
    workflow = StateGraph(TransliterationState)

    workflow.add_node("transliteration", agent.transliterate)
    workflow.add_edge(START, "transliteration")
    workflow.add_edge("transliteration", END)

    return workflow.compile()

