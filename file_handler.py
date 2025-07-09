# -*- coding: utf-8 -*-
"""
文件处理模块
用于处理Excel、CSV、TXT等文件的读写操作
"""

import os
import pandas as pd
import chardet
from typing import List, Dict, Tuple, Optional, Union, Any
from loguru import logger
from config import settings

class FileHandler:
    """
    文件处理器
    负责处理各种格式文件的读写操作
    """
    
    def __init__(self):
        """
        初始化文件处理器
        """
        self.supported_formats = settings.SUPPORTED_FORMATS
        self.upload_dir = settings.UPLOAD_DIR
        self.output_dir = settings.OUTPUT_DIR
        
        # 确保目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def is_supported_format(self, filename: str) -> bool:
        """
        检查文件格式是否支持
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否支持该格式
        """
        ext = filename.split('.')[-1].lower()
        return ext in self.supported_formats
    
    def detect_encoding(self, file_path: str) -> str:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件编码
        """
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding'] or 'utf-8'
    
    def read_excel(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        读取Excel文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[pd.DataFrame, Dict]: 数据框和元数据
        """
        try:
            # 读取所有sheet
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            # 默认读取第一个sheet
            df = pd.read_excel(file_path, sheet_name=sheet_names[0])
            
            metadata = {
                'sheet_names': sheet_names,
                'current_sheet': sheet_names[0],
                'file_type': 'excel'
            }
            
            return df, metadata
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            raise
    
    def read_csv(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        读取CSV文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[pd.DataFrame, Dict]: 数据框和元数据
        """
        try:
            # 检测编码
            encoding = self.detect_encoding(file_path)
            
            # 尝试检测分隔符
            with open(file_path, 'r', encoding=encoding) as f:
                first_line = f.readline().strip()
            
            # 根据常见分隔符判断
            if ',' in first_line:
                sep = ','
            elif ';' in first_line:
                sep = ';'
            elif '\t' in first_line:
                sep = '\t'
            else:
                sep = ','
            
            df = pd.read_csv(file_path, encoding=encoding, sep=sep)
            
            metadata = {
                'encoding': encoding,
                'separator': sep,
                'file_type': 'csv'
            }
            
            return df, metadata
        except Exception as e:
            logger.error(f"读取CSV文件失败: {e}")
            raise
    
    def read_txt(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        读取TXT文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[pd.DataFrame, Dict]: 数据框和元数据
        """
        try:
            # 检测编码
            encoding = self.detect_encoding(file_path)
            
            # 读取文本内容
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            # 转换为DataFrame
            df = pd.DataFrame({
                'text': [line.strip() for line in lines if line.strip()]
            })
            
            metadata = {
                'encoding': encoding,
                'line_count': len(lines),
                'file_type': 'txt'
            }
            
            return df, metadata
        except Exception as e:
            logger.error(f"读取TXT文件失败: {e}")
            raise
    
    def read_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        根据文件类型读取文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[pd.DataFrame, Dict]: 数据框和元数据
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not self.is_supported_format(file_path):
            raise ValueError(f"不支持的文件格式: {file_path}")
        
        ext = file_path.split('.')[-1].lower()
        
        if ext in ['xlsx', 'xls']:
            return self.read_excel(file_path)
        elif ext == 'csv':
            return self.read_csv(file_path)
        elif ext == 'txt':
            return self.read_txt(file_path)
        else:
            raise ValueError(f"未知的文件格式: {ext}")
    
    def save_excel(self, df: pd.DataFrame, file_path: str, metadata: Dict = None) -> str:
        """
        保存DataFrame到Excel文件
        
        Args:
            df: 数据框
            file_path: 文件路径
            metadata: 元数据
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 如果是更新现有文件且有多个sheet
            if metadata and 'sheet_names' in metadata and len(metadata['sheet_names']) > 1:
                # 读取原始Excel文件
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=metadata.get('current_sheet', 'Sheet1'), index=False)
            else:
                # 创建新Excel文件
                df.to_excel(file_path, index=False)
            
            logger.info(f"Excel文件保存成功: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存Excel文件失败: {e}")
            raise
    
    def save_csv(self, df: pd.DataFrame, file_path: str, metadata: Dict = None) -> str:
        """
        保存DataFrame到CSV文件
        
        Args:
            df: 数据框
            file_path: 文件路径
            metadata: 元数据
            
        Returns:
            str: 保存的文件路径
        """
        try:
            encoding = metadata.get('encoding', 'utf-8') if metadata else 'utf-8'
            sep = metadata.get('separator', ',') if metadata else ','
            
            df.to_csv(file_path, index=False, encoding=encoding, sep=sep)
            
            logger.info(f"CSV文件保存成功: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存CSV文件失败: {e}")
            raise
    
    def save_txt(self, df: pd.DataFrame, file_path: str, metadata: Dict = None) -> str:
        """
        保存DataFrame到TXT文件
        
        Args:
            df: 数据框
            file_path: 文件路径
            metadata: 元数据
            
        Returns:
            str: 保存的文件路径
        """
        try:
            encoding = metadata.get('encoding', 'utf-8') if metadata else 'utf-8'
            
            # 将DataFrame转换为文本行
            text_column = df['text'] if 'text' in df.columns else df.iloc[:, 0]
            lines = text_column.astype(str).tolist()
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write('\n'.join(lines))
            
            logger.info(f"TXT文件保存成功: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存TXT文件失败: {e}")
            raise
    
    def save_file(self, df: pd.DataFrame, file_path: str, metadata: Dict = None) -> str:
        """
        根据文件类型保存DataFrame
        
        Args:
            df: 数据框
            file_path: 文件路径
            metadata: 元数据
            
        Returns:
            str: 保存的文件路径
        """
        ext = file_path.split('.')[-1].lower()
        
        if ext in ['xlsx', 'xls']:
            return self.save_excel(df, file_path, metadata)
        elif ext == 'csv':
            return self.save_csv(df, file_path, metadata)
        elif ext == 'txt':
            return self.save_txt(df, file_path, metadata)
        else:
            raise ValueError(f"未知的文件格式: {ext}")
    
    def get_output_path(self, input_path: str, suffix: str = "_translated") -> str:
        """
        生成输出文件路径
        
        Args:
            input_path: 输入文件路径
            suffix: 文件名后缀
            
        Returns:
            str: 输出文件路径
        """
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}{suffix}{ext}"
        return os.path.join(self.output_dir, output_filename)
    
    def extract_translatable_content(self, df: pd.DataFrame, columns: List[str] = None) -> List[Tuple[int, int, str]]:
        """
        从DataFrame中提取需要翻译的内容
        
        Args:
            df: 数据框
            columns: 需要翻译的列名列表，如果为None则处理所有文本列
            
        Returns:
            List[Tuple[int, int, str]]: 需要翻译的内容列表，每项为(行索引, 列索引, 文本内容)
        """
        translatable_content = []
        
        # 如果没有指定列，则尝试处理所有可能的文本列
        if not columns:
            # 排除明显的非文本列
            exclude_patterns = ['id', 'date', 'time', 'number', 'count', 'amount', 'price']
            columns = []
            
            for col in df.columns:
                # 跳过明显的非文本列
                if any(pattern in str(col).lower() for pattern in exclude_patterns):
                    continue
                
                # 检查列的数据类型，只处理可能是文本的列
                if df[col].dtype == 'object':
                    # 抽样检查是否包含足够长的文本
                    sample = df[col].dropna().astype(str).sample(min(5, len(df))).tolist()
                    if any(len(text) > 3 for text in sample):
                        columns.append(col)
        
        # 提取需要翻译的内容
        for i, row in df.iterrows():
            for j, col in enumerate(df.columns):
                if col in columns and pd.notna(row[col]):
                    text = str(row[col]).strip()
                    if text and len(text) > 1:  # 忽略空字符串和单字符
                        translatable_content.append((i, df.columns.get_loc(col), text))
        
        return translatable_content
    
    def update_dataframe_with_translations(self, df: pd.DataFrame, translations: List[Tuple[int, int, str, str]]) -> pd.DataFrame:
        """
        使用翻译结果更新DataFrame，翻译结果保存在原文列的下一列
        
        Args:
            df: 原始数据框
            translations: 翻译结果列表，每项为(行索引, 列索引, 原文, 译文)
            
        Returns:
            pd.DataFrame: 更新后的数据框
        """
        # 创建DataFrame的副本以避免修改原始数据
        updated_df = df.copy()
        
        # 按列分组处理翻译结果
        translations_by_col = {}
        for row_idx, col_idx, original, translated in translations:
            if col_idx not in translations_by_col:
                translations_by_col[col_idx] = []
            translations_by_col[col_idx].append((row_idx, original, translated))
        
        # 为每个翻译列在其右侧插入翻译结果列
        col_offset = 0
        for col_idx in sorted(translations_by_col.keys()):
            original_col_name = updated_df.columns[col_idx + col_offset]
            translated_col_name = f"{original_col_name}_translated"
            
            # 创建翻译结果列，初始值为空字符串
            translated_values = [''] * len(updated_df)
            
            # 填入翻译结果
            for row_idx, original, translated in translations_by_col[col_idx]:
                translated_values[row_idx] = translated
            
            # 在原文列的下一列插入翻译结果
            insert_position = col_idx + col_offset + 1
            updated_df.insert(insert_position, translated_col_name, translated_values)
            
            # 更新偏移量，因为插入了新列
            col_offset += 1
        
        return updated_df

# 创建全局文件处理器实例
file_handler = FileHandler()