# -*- coding: utf-8 -*-
"""
配置文件
用于管理项目的全局配置信息
"""

import os
from typing import Dict, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    项目配置类
    使用pydantic进行配置管理，支持环境变量覆盖
    """
    
    # 应用基础配置
    APP_NAME: str = "游戏本地化翻译助手"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 文件配置
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    DATA_DIR: str = "data"  # 用于保存应用数据和配置
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # 支持的文件格式
    SUPPORTED_FORMATS: List[str] = ["xlsx", "xls", "csv", "txt"]
    
    # 支持的语言列表
    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "zh": "中文",
        "en": "英语",
        "ja": "日语",
        "ko": "韩语",
        "fr": "法语",
        "de": "德语",
        "es": "西班牙语",
        "ru": "俄语",
        "pt": "葡萄牙语",
        "it": "意大利语"
    }
    
    # AI API 配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    
    # 翻译配置
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.3
    BATCH_SIZE: int = 10  # 批量翻译的大小
    
    # 数据库配置
    DATABASE_PATH: str = "translation_db.sqlite"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()

# 确保必要的目录存在
def ensure_directories():
    """
    确保必要的目录存在
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.DATA_DIR, exist_ok=True)

if __name__ == "__main__":
    ensure_directories()