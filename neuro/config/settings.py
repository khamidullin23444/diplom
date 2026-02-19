"""
Настройки конфигурации для мультиагентной системы
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # OCR настройки
    OCR_MODEL_PATH: str = "runs/detect/old_tatar_yolov8/weights/best.pt"
    OCR_CONFIDENCE_THRESHOLD: float = 0.25
    
    # LLM настройки
    LLM_MODEL_NAME: str = "neurotatarlar/tweety-tatar-base"
    LLM_MODEL_TYPE: str = "huggingface"  # "huggingface" или "ollama"
    LLM_DEVICE: Optional[str] = None  # None = автоопределение
    LLM_TEMPERATURE: float = 0.1
    
    # CUDA настройки
    CUDA_DEVICE: int = 0
    USE_CUDA: bool = True
    
    # Пути
    OUTPUT_DIR: str = "results"
    LOG_DIR: str = "logs"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()

