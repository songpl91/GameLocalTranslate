# -*- coding: utf-8 -*-
"""
翻译引擎模块
支持多种AI API进行翻译
"""

import time
import asyncio
import httpx
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, Union
from loguru import logger
from config import settings
from database import db_manager

class BaseTranslator(ABC):
    """
    翻译器基类
    定义翻译器的通用接口
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化翻译器
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model or settings.DEFAULT_MODEL
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        翻译单个文本
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            str: 翻译结果
        """
        pass
    
    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """
        批量翻译文本
        
        Args:
            texts: 待翻译文本列表
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            List[str]: 翻译结果列表
        """
        results = []
        for text in texts:
            try:
                result = await self.translate_text(text, source_lang, target_lang)
                results.append(result)
                # 添加延迟避免API限制
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"翻译失败: {text[:50]}... - {e}")
                results.append(text)  # 翻译失败时返回原文
        return results
    
    def create_translation_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        创建翻译提示词
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            str: 翻译提示词
        """
        source_name = settings.SUPPORTED_LANGUAGES.get(source_lang, source_lang)
        target_name = settings.SUPPORTED_LANGUAGES.get(target_lang, target_lang)
        
        return f"""请将以下{source_name}文本精准、专业地翻译为{target_name}。

【角色设定】
你是一名资深的海外游戏本地化翻译专家，精通{source_name}与{target_name}语言，深谙两地文化差异，具备丰富的游戏行业术语和表达经验。

【翻译要求】
1. 深入理解原文语境，确保译文准确传达原文含义。
2. 保持原文语气、风格和格式，尤其注意游戏专有名词和术语的标准化翻译。
3. 译文需贴合{target_name}地区玩家的语言习惯和文化背景，避免直译。
4. 仅输出最终翻译内容，不添加任何解释、注释或多余信息。

原文：{text}

翻译："""
    
    def create_review_prompt(self, original_text: str, translated_text: str, source_lang: str, target_lang: str) -> str:
        """
        创建审核提示词
        
        Args:
            original_text: 原文
            translated_text: 译文
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            str: 审核提示词
        """
        source_name = settings.SUPPORTED_LANGUAGES.get(source_lang, source_lang)
        target_name = settings.SUPPORTED_LANGUAGES.get(target_lang, target_lang)
        
        return f"""请作为专业的游戏本地化审核专家，评估以下翻译质量并提供改进建议。

【角色设定】
你是一名资深的游戏本地化审核专家，具备深厚的{source_name}和{target_name}语言功底，熟悉游戏行业术语，擅长发现翻译中的问题并提供专业的修改建议。

【审核标准】
1. 准确性：译文是否准确传达原文含义
2. 流畅性：译文是否符合{target_name}语言习惯
3. 一致性：游戏术语翻译是否统一规范
4. 文化适应性：是否适合{target_name}地区玩家
5. 格式保持：是否保持原文格式和语气

【输出格式】
请按以下JSON格式输出审核结果：
{{
  "quality_score": <1-10分的质量评分>,
  "is_acceptable": <true/false，是否可接受>,
  "issues": [<发现的问题列表>],
  "suggestions": [<改进建议列表>],
  "improved_translation": "<如果需要修改，提供改进后的翻译>"
}}

原文（{source_name}）：{original_text}

译文（{target_name}）：{translated_text}

审核结果："""
    
    async def review_translation(self, original_text: str, translated_text: str, source_lang: str, target_lang: str) -> Dict:
        """
        审核翻译质量
        
        Args:
            original_text: 原文
            translated_text: 译文
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            Dict: 审核结果
        """
        # 子类需要实现具体的审核逻辑
        raise NotImplementedError("子类必须实现review_translation方法")

class OpenAITranslator(BaseTranslator):
    """
    OpenAI翻译器
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        super().__init__(
            api_key=api_key or settings.OPENAI_API_KEY,
            base_url=base_url or settings.OPENAI_BASE_URL,
            model=model or "gpt-3.5-turbo"
        )
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        使用OpenAI API翻译文本
        """
        if not self.api_key:
            raise ValueError("OpenAI API密钥未设置")
        
        prompt = self.create_translation_prompt(text, source_lang, target_lang)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": settings.MAX_TOKENS,
            "temperature": settings.TEMPERATURE
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
    
    async def review_translation(self, original_text: str, translated_text: str, source_lang: str, target_lang: str) -> Dict:
        """
        使用OpenAI API审核翻译质量
        """
        if not self.api_key:
            raise ValueError("OpenAI API密钥未设置")
        
        prompt = self.create_review_prompt(original_text, translated_text, source_lang, target_lang)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": settings.MAX_TOKENS,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
            result = response.json()
            review_text = result["choices"][0]["message"]["content"].strip()
            
            try:
                import json
                review_result = json.loads(review_text)
                return review_result
            except json.JSONDecodeError:
                return {
                    "quality_score": 5,
                    "is_acceptable": True,
                    "issues": ["审核结果格式解析失败"],
                    "suggestions": ["请检查模型输出格式"],
                    "improved_translation": translated_text,
                    "raw_response": review_text
                }

class DeepSeekTranslator(BaseTranslator):
    """
    DeepSeek翻译器
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        super().__init__(
            api_key=api_key or settings.DEEPSEEK_API_KEY,
            base_url=base_url or settings.DEEPSEEK_BASE_URL,
            model=model or "deepseek-chat"
        )
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        使用DeepSeek API翻译文本
        """
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
        
        prompt = self.create_translation_prompt(text, source_lang, target_lang)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": settings.MAX_TOKENS,
            "temperature": settings.TEMPERATURE
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
    
    async def review_translation(self, original_text: str, translated_text: str, source_lang: str, target_lang: str) -> Dict:
        """
        使用DeepSeek API审核翻译质量
        """
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
        
        prompt = self.create_review_prompt(original_text, translated_text, source_lang, target_lang)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": settings.MAX_TOKENS,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
            result = response.json()
            review_text = result["choices"][0]["message"]["content"].strip()
            
            try:
                import json
                review_result = json.loads(review_text)
                return review_result
            except json.JSONDecodeError:
                return {
                    "quality_score": 5,
                    "is_acceptable": True,
                    "issues": ["审核结果格式解析失败"],
                    "suggestions": ["请检查模型输出格式"],
                    "improved_translation": translated_text,
                    "raw_response": review_text
                }

class QwenTranslator(BaseTranslator):
    """
    千问翻译器
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        super().__init__(
            api_key=api_key or settings.QWEN_API_KEY,
            base_url=base_url or settings.QWEN_BASE_URL,
            model=model or "qwen-turbo"
        )
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        使用千问API翻译文本
        """
        if not self.api_key:
            raise ValueError("千问API密钥未设置")
        
        prompt = self.create_translation_prompt(text, source_lang, target_lang)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": settings.MAX_TOKENS,
            "temperature": settings.TEMPERATURE
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
    
    async def review_translation(self, original_text: str, translated_text: str, source_lang: str, target_lang: str) -> Dict:
        """
        使用千问API审核翻译质量
        """
        if not self.api_key:
            raise ValueError("千问API密钥未设置")
        
        prompt = self.create_review_prompt(original_text, translated_text, source_lang, target_lang)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": settings.MAX_TOKENS,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
            result = response.json()
            review_text = result["choices"][0]["message"]["content"].strip()
            
            try:
                import json
                review_result = json.loads(review_text)
                return review_result
            except json.JSONDecodeError:
                return {
                    "quality_score": 5,
                    "is_acceptable": True,
                    "issues": ["审核结果格式解析失败"],
                    "suggestions": ["请检查模型输出格式"],
                    "improved_translation": translated_text,
                    "raw_response": review_text
                }

class OllamaTranslator(BaseTranslator):
    """
    Ollama翻译器
    用于本地部署的模型
    """
    
    def __init__(self, base_url: str = None, model: str = None):
        super().__init__(
            base_url=base_url or settings.OLLAMA_BASE_URL,
            model=model or "qwen3:8b"
        )
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        使用Ollama API翻译文本
        """
        prompt = self.create_translation_prompt(text, source_lang, target_lang)
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.TEMPERATURE,
                "num_predict": settings.MAX_TOKENS
            }
        }
        
        try:
            # 增加超时时间，因为本地模型可能需要更长时间
            async with httpx.AsyncClient(timeout=120.0) as client:
                # 首先检查服务是否可用
                health_response = await client.get(f"{self.base_url}/api/tags")
                if health_response.status_code != 200:
                    raise Exception(f"Ollama 服务不可用: {health_response.status_code}")
                
                # 检查模型是否存在
                models = health_response.json()
                model_names = [model['name'] for model in models.get('models', [])]
                if self.model not in model_names:
                    raise Exception(f"模型 '{self.model}' 未找到。可用模型: {model_names}")
                
                # 执行翻译请求
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=data
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API请求失败: {response.status_code} - {response.text}")
                
                result = response.json()
                if 'response' not in result:
                    raise Exception(f"API响应格式错误: {result}")
                
                # 清理返回内容中的<think></think>标签
                response_text = result["response"].strip()
                # 使用正则表达式删除<think></think>标签及其内容
                cleaned_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
                return cleaned_text.strip()
                
        except httpx.TimeoutException:
            raise Exception(f"Ollama API请求超时，请检查模型是否正在运行或增加超时时间")
        except httpx.ConnectError:
            raise Exception(f"无法连接到 Ollama 服务 ({self.base_url})，请确保 Ollama 正在运行")
        except Exception as e:
            if "模型" in str(e) or "API" in str(e):
                raise e
            else:
                raise Exception(f"Ollama 翻译失败: {str(e)}")
    
    async def review_translation(self, original_text: str, translated_text: str, source_lang: str, target_lang: str) -> Dict:
        """
        使用Ollama API审核翻译质量
        """
        prompt = self.create_review_prompt(original_text, translated_text, source_lang, target_lang)
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": settings.MAX_TOKENS
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=data
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API请求失败: {response.status_code} - {response.text}")
                
                result = response.json()
                if 'response' not in result:
                    raise Exception(f"API响应格式错误: {result}")
                
                review_text = result["response"].strip()
                # 清理<think></think>标签
                cleaned_text = re.sub(r'<think>.*?</think>', '', review_text, flags=re.DOTALL)
                
                try:
                    import json
                    review_result = json.loads(cleaned_text)
                    return review_result
                except json.JSONDecodeError:
                    return {
                        "quality_score": 5,
                        "is_acceptable": True,
                        "issues": ["审核结果格式解析失败"],
                        "suggestions": ["请检查模型输出格式"],
                        "improved_translation": translated_text,
                        "raw_response": cleaned_text
                    }
                
        except httpx.TimeoutException:
            raise Exception(f"Ollama API请求超时，请检查模型是否正在运行或增加超时时间")
        except httpx.ConnectError:
            raise Exception(f"无法连接到 Ollama 服务 ({self.base_url})，请确保 Ollama 正在运行")
        except Exception as e:
            if "模型" in str(e) or "API" in str(e):
                raise e
            else:
                raise Exception(f"Ollama 审核失败: {str(e)}")

class TranslationEngine:
    """
    翻译引擎
    管理多个翻译器并提供统一接口
    """
    
    def __init__(self):
        """
        初始化翻译引擎
        """
        self.translators = {
            "openai": OpenAITranslator,
            "deepseek": DeepSeekTranslator,
            "qwen": QwenTranslator,
            "ollama": OllamaTranslator
        }
        self.current_translator = None
    
    def set_translator(self, provider: str, **kwargs) -> BaseTranslator:
        """
        设置当前翻译器
        
        Args:
            provider: 翻译服务提供商
            **kwargs: 翻译器初始化参数
            
        Returns:
            BaseTranslator: 翻译器实例
        """
        if provider not in self.translators:
            raise ValueError(f"不支持的翻译服务: {provider}")
        
        translator_class = self.translators[provider]
        self.current_translator = translator_class(**kwargs)
        return self.current_translator
    
    async def translate_with_correction(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        带纠错功能的翻译
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            str: 翻译结果
        """
        # 首先检查纠错表
        correction = db_manager.get_correction(text, source_lang, target_lang)
        if correction:
            logger.info(f"使用纠错表翻译: {text} -> {correction}")
            return correction
        
        # 如果纠错表中没有，则使用AI翻译
        if not self.current_translator:
            raise ValueError("未设置翻译器")
        
        start_time = time.time()
        result = await self.current_translator.translate_text(text, source_lang, target_lang)
        translation_time = time.time() - start_time
        
        # 记录翻译历史
        db_manager.add_translation_history(
            original_text=text,
            translated_text=result,
            source_lang=source_lang,
            target_lang=target_lang,
            api_provider=self.current_translator.name,
            model_name=self.current_translator.model,
            translation_time=translation_time
        )
        
        return result
    
    async def translate_batch_with_correction(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """
        批量翻译（带纠错功能）
        
        Args:
            texts: 待翻译文本列表
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            List[str]: 翻译结果列表
        """
        results = []
        
        for text in texts:
            try:
                result = await self.translate_with_correction(text, source_lang, target_lang)
                results.append(result)
            except Exception as e:
                logger.error(f"翻译失败: {text[:50]}... - {e}")
                results.append(text)  # 翻译失败时返回原文
        
        return results
    
    def get_available_providers(self) -> List[str]:
        """
        获取可用的翻译服务提供商
        
        Returns:
            List[str]: 提供商列表
        """
        return list(self.translators.keys())
    
    async def review_translation(self, original_text: str, translated_text: str, source_lang: str, target_lang: str) -> Dict:
        """
        审核翻译质量
        
        Args:
            original_text: 原文
            translated_text: 翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            Dict: 审核结果
        """
        if not self.current_translator:
            raise ValueError("未设置翻译器")
        
        try:
            result = await self.current_translator.review_translation(
                original_text, translated_text, source_lang, target_lang
            )
            return result
        except Exception as e:
            logger.error(f"翻译审核失败: {e}")
            # 返回默认审核结果
            return {
                "quality_score": 5,
                "is_acceptable": True,
                "issues": [f"审核失败: {str(e)}"],
                "suggestions": ["请检查翻译器配置"],
                "improved_translation": translated_text,
                "error": str(e)
            }
    
    async def test_translator(self, provider: str, **kwargs) -> bool:
        """
        测试翻译器连接
        
        Args:
            provider: 翻译服务提供商
            **kwargs: 翻译器初始化参数
            
        Returns:
            bool: 是否连接成功
        """
        try:
            translator = self.set_translator(provider, **kwargs)
            result = await translator.translate_text("Hello", "en", "zh")
            return bool(result)
        except Exception as e:
            logger.error(f"翻译器测试失败: {e}")
            return False

# 创建全局翻译引擎实例
translation_engine = TranslationEngine()