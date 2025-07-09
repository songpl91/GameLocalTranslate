# -*- coding: utf-8 -*-
"""
数据库模块
用于管理翻译历史、纠错表等数据
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from loguru import logger
from config import settings

class DatabaseManager:
    """
    数据库管理器
    负责所有数据库操作
    """
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path or settings.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """
        初始化数据库表结构
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建纠错表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS correction_table (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_text TEXT NOT NULL,
                        correct_translation TEXT NOT NULL,
                        source_language TEXT NOT NULL,
                        target_language TEXT NOT NULL,
                        category TEXT DEFAULT 'general',
                        priority INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(source_text, source_language, target_language)
                    )
                """)
                
                # 创建翻译历史表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS translation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_text TEXT NOT NULL,
                        translated_text TEXT NOT NULL,
                        source_language TEXT NOT NULL,
                        target_language TEXT NOT NULL,
                        api_provider TEXT NOT NULL,
                        model_name TEXT,
                        file_name TEXT,
                        translation_time REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建项目配置表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS project_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setting_key TEXT UNIQUE NOT NULL,
                        setting_value TEXT NOT NULL,
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def add_correction_entry(self, source_text: str, correct_translation: str, 
                           source_lang: str, target_lang: str, 
                           category: str = "general", priority: int = 1) -> bool:
        """
        添加纠错条目
        
        Args:
            source_text: 源文本
            correct_translation: 正确翻译
            source_lang: 源语言
            target_lang: 目标语言
            category: 分类
            priority: 优先级
            
        Returns:
            bool: 是否添加成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO correction_table 
                    (source_text, correct_translation, source_language, target_language, category, priority, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (source_text, correct_translation, source_lang, target_lang, category, priority, datetime.now()))
                conn.commit()
                logger.info(f"添加纠错条目: {source_text} -> {correct_translation}")
                return True
        except Exception as e:
            logger.error(f"添加纠错条目失败: {e}")
            return False
    
    def get_correction(self, source_text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        查找纠错翻译
        
        Args:
            source_text: 源文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            Optional[str]: 正确翻译，如果没找到返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT correct_translation FROM correction_table 
                    WHERE source_text = ? AND source_language = ? AND target_language = ?
                    ORDER BY priority DESC, updated_at DESC
                    LIMIT 1
                """, (source_text, source_lang, target_lang))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"查找纠错翻译失败: {e}")
            return None
    
    def get_all_corrections(self, source_lang: str = None, target_lang: str = None) -> List[Dict]:
        """
        获取所有纠错条目
        
        Args:
            source_lang: 源语言过滤
            target_lang: 目标语言过滤
            
        Returns:
            List[Dict]: 纠错条目列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM correction_table"
                params = []
                
                if source_lang or target_lang:
                    conditions = []
                    if source_lang:
                        conditions.append("source_language = ?")
                        params.append(source_lang)
                    if target_lang:
                        conditions.append("target_language = ?")
                        params.append(target_lang)
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY priority DESC, updated_at DESC"
                
                cursor.execute(query, params)
                columns = [description[0] for description in cursor.description]
                results = cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            logger.error(f"获取纠错条目失败: {e}")
            return []
    
    def add_translation_history(self, original_text: str, translated_text: str,
                              source_lang: str, target_lang: str, api_provider: str,
                              model_name: str = None, file_name: str = None,
                              translation_time: float = None) -> bool:
        """
        添加翻译历史记录
        
        Args:
            original_text: 原文
            translated_text: 译文
            source_lang: 源语言
            target_lang: 目标语言
            api_provider: API提供商
            model_name: 模型名称
            file_name: 文件名
            translation_time: 翻译耗时
            
        Returns:
            bool: 是否添加成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO translation_history 
                    (original_text, translated_text, source_language, target_language, 
                     api_provider, model_name, file_name, translation_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (original_text, translated_text, source_lang, target_lang,
                      api_provider, model_name, file_name, translation_time))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"添加翻译历史失败: {e}")
            return False
    
    def get_translation_history(self, limit: int = 100) -> List[Dict]:
        """
        获取翻译历史记录
        
        Args:
            limit: 返回记录数量限制
            
        Returns:
            List[Dict]: 翻译历史记录列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM translation_history 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                columns = [description[0] for description in cursor.description]
                results = cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            logger.error(f"获取翻译历史失败: {e}")
            return []
    
    def delete_correction(self, correction_id: int) -> bool:
        """
        删除纠错条目
        
        Args:
            correction_id: 纠错条目ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM correction_table WHERE id = ?", (correction_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除纠错条目失败: {e}")
            return False
    
    def init_default_corrections(self):
        """
        初始化默认的纠错条目（游戏常用术语）
        """
        default_corrections = [
            # 游戏通用术语
            ("HP", "生命值", "en", "zh", "game_term", 10),
            ("MP", "魔法值", "en", "zh", "game_term", 10),
            ("EXP", "经验值", "en", "zh", "game_term", 10),
            ("Level", "等级", "en", "zh", "game_term", 10),
            ("Attack", "攻击力", "en", "zh", "game_term", 10),
            ("Defense", "防御力", "en", "zh", "game_term", 10),
            ("Speed", "速度", "en", "zh", "game_term", 10),
            ("Critical", "暴击", "en", "zh", "game_term", 10),
            ("Skill", "技能", "en", "zh", "game_term", 10),
            ("Item", "道具", "en", "zh", "game_term", 10),
            ("Equipment", "装备", "en", "zh", "game_term", 10),
            ("Weapon", "武器", "en", "zh", "game_term", 10),
            ("Armor", "护甲", "en", "zh", "game_term", 10),
            ("Quest", "任务", "en", "zh", "game_term", 10),
            ("Mission", "任务", "en", "zh", "game_term", 10),
            ("Boss", "首领", "en", "zh", "game_term", 10),
            ("Guild", "公会", "en", "zh", "game_term", 10),
            ("Team", "队伍", "en", "zh", "game_term", 10),
            ("Player", "玩家", "en", "zh", "game_term", 10),
            ("Character", "角色", "en", "zh", "game_term", 10),
        ]
        
        for source, translation, src_lang, tgt_lang, category, priority in default_corrections:
            self.add_correction_entry(source, translation, src_lang, tgt_lang, category, priority)
        
        logger.info("默认纠错条目初始化完成")

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

if __name__ == "__main__":
    # 初始化默认纠错条目
    db_manager.init_default_corrections()