# -*- coding: utf-8 -*-
"""
Streamlit前端应用
游戏本地化翻译助手的Web界面
"""

import os
import asyncio
import json
import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from loguru import logger

# 配置matplotlib中文字体
import matplotlib.pyplot as plt
import matplotlib
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans', 'Helvetica', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 导入自定义模块
from config import settings, ensure_directories
from database import db_manager
from file_handler import file_handler
from translator import translation_engine

# 页面配置
st.set_page_config(
    page_title="游戏本地化翻译助手",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 确保目录存在
ensure_directories()

def save_config(provider, config, source_lang, target_lang):
    """
    保存配置到本地文件
    """
    config_data = {
        'provider': provider,
        'config': config,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'enable_review': st.session_state.get('enable_review', False),
        'review_threshold': st.session_state.get('review_threshold', 7),
        'auto_improve': st.session_state.get('auto_improve', False)
    }
    
    config_file = os.path.join(settings.DATA_DIR, 'app_config.json')
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        logger.info("配置已保存")
    except Exception as e:
        logger.error(f"保存配置失败: {e}")

def load_saved_config():
    """
    加载保存的配置
    """
    config_file = os.path.join(settings.DATA_DIR, 'app_config.json')
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 设置到session_state
            st.session_state.saved_provider = config_data.get('provider', 'ollama')
            st.session_state.saved_config = config_data.get('config', {})
            st.session_state.saved_source_lang = config_data.get('source_lang', 'en')
            st.session_state.saved_target_lang = config_data.get('target_lang', 'zh')
            st.session_state.enable_review = config_data.get('enable_review', False)
            st.session_state.review_threshold = config_data.get('review_threshold', 7)
            st.session_state.auto_improve = config_data.get('auto_improve', False)
            
            logger.info("配置已加载")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            # 设置默认值
            st.session_state.saved_provider = 'ollama'
            st.session_state.saved_config = {}
            st.session_state.saved_source_lang = 'en'
            st.session_state.saved_target_lang = 'zh'
            st.session_state.enable_review = False
            st.session_state.review_threshold = 7
            st.session_state.auto_improve = False
    else:
        # 设置默认值
        st.session_state.saved_provider = 'ollama'
        st.session_state.saved_config = {}
        st.session_state.saved_source_lang = 'en'
        st.session_state.saved_target_lang = 'zh'
        st.session_state.enable_review = False
        st.session_state.review_threshold = 7
        st.session_state.auto_improve = False

def init_session_state():
    """
    初始化session state
    """
    if 'uploaded_file_data' not in st.session_state:
        st.session_state.uploaded_file_data = None
    if 'file_metadata' not in st.session_state:
        st.session_state.file_metadata = None
    if 'translation_results' not in st.session_state:
        st.session_state.translation_results = None
    if 'translator_configured' not in st.session_state:
        st.session_state.translator_configured = False
    
    # 加载保存的配置
    load_saved_config()

def sidebar_config():
    """
    侧边栏配置
    """
    st.sidebar.title("🎮 游戏本地化翻译助手")
    st.sidebar.markdown("---")
    
    # 翻译器配置
    st.sidebar.subheader("🔧 翻译器配置")
    
    provider = st.sidebar.selectbox(
        "选择翻译服务",
        options=["openai", "deepseek", "qwen", "ollama"],
        format_func=lambda x: {
            "openai": "OpenAI",
            "deepseek": "DeepSeek",
            "qwen": "千问",
            "ollama": "Ollama (本地)"
        }[x],
        index=["openai", "deepseek", "qwen", "ollama"].index(st.session_state.get('saved_provider', 'ollama')),
        key="sidebar_provider_select"
    )
    
    # 获取保存的配置，如果当前选择的provider与保存的provider一致，则使用保存的配置，否则使用默认配置
    saved_provider = st.session_state.get('saved_provider', 'ollama')
    saved_config = st.session_state.get('saved_config', {}) if provider == saved_provider else {}
    
    # 根据选择的服务显示不同的配置选项
    if provider == "ollama":
        base_url = st.sidebar.text_input("Ollama URL", 
                                        value=saved_config.get('base_url', settings.OLLAMA_BASE_URL))
        model = st.sidebar.text_input("模型名称", 
                                     value=saved_config.get('model', "qwen3:8b"))
        config = {"base_url": base_url, "model": model}
    elif provider == "openai":
        api_key = st.sidebar.text_input("OpenAI API Key", type="password", 
                                       value=saved_config.get('api_key', settings.OPENAI_API_KEY))
        base_url = st.sidebar.text_input("Base URL", 
                                        value=saved_config.get('base_url', settings.OPENAI_BASE_URL))
        model = st.sidebar.text_input("模型名称", 
                                     value=saved_config.get('model', "gpt-3.5-turbo"))
        config = {"api_key": api_key, "base_url": base_url, "model": model}
    elif provider == "deepseek":
        api_key = st.sidebar.text_input("DeepSeek API Key", type="password", 
                                       value=saved_config.get('api_key', settings.DEEPSEEK_API_KEY))
        base_url = st.sidebar.text_input("Base URL", 
                                        value=saved_config.get('base_url', settings.DEEPSEEK_BASE_URL))
        model = st.sidebar.text_input("模型名称", 
                                     value=saved_config.get('model', "deepseek-chat"))
        config = {"api_key": api_key, "base_url": base_url, "model": model}
    elif provider == "qwen":
        api_key = st.sidebar.text_input("千问 API Key", type="password", 
                                       value=saved_config.get('api_key', settings.QWEN_API_KEY))
        base_url = st.sidebar.text_input("Base URL", 
                                        value=saved_config.get('base_url', settings.QWEN_BASE_URL))
        model = st.sidebar.text_input("模型名称", 
                                     value=saved_config.get('model', "qwen-turbo"))
        config = {"api_key": api_key, "base_url": base_url, "model": model}
    
    # 测试连接按钮
    if st.sidebar.button("🔍 测试连接"):
        with st.sidebar:
            with st.spinner("测试连接中..."):
                try:
                    # 使用asyncio运行异步函数
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(
                        translation_engine.test_translator(provider, **config)
                    )
                    loop.close()
                    
                    if success:
                        st.success("✅ 连接成功！")
                        st.session_state.translator_configured = True
                        translation_engine.set_translator(provider, **config)
                    else:
                        st.error("❌ 连接失败，请检查配置")
                        st.session_state.translator_configured = False
                except Exception as e:
                    st.error(f"❌ 连接失败: {str(e)}")
                    st.session_state.translator_configured = False
    
    # 显示连接状态
    if st.session_state.translator_configured:
        st.sidebar.success("🟢 翻译器已配置")
    else:
        st.sidebar.warning("🟡 请配置并测试翻译器")
    
    st.sidebar.markdown("---")
    
    # 语言配置
    st.sidebar.subheader("🌐 语言设置")
    
    source_lang = st.sidebar.selectbox(
        "源语言",
        options=list(settings.SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: settings.SUPPORTED_LANGUAGES[x],
        index=list(settings.SUPPORTED_LANGUAGES.keys()).index(st.session_state.get('saved_source_lang', 'en')),
        key="sidebar_source_lang"
    )
    
    target_lang = st.sidebar.selectbox(
        "目标语言",
        options=list(settings.SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: settings.SUPPORTED_LANGUAGES[x],
        index=list(settings.SUPPORTED_LANGUAGES.keys()).index(st.session_state.get('saved_target_lang', 'zh')),
        key="sidebar_target_lang"
    )
    
    # 审核设置
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 翻译审核设置")
    
    enable_review = st.sidebar.checkbox(
        "启用翻译审核",
        value=st.session_state.get('enable_review', False),
        help="启用后，每次翻译都会进行质量审核和改进建议",
        key="sidebar_enable_review"
    )
    
    review_threshold = st.sidebar.slider(
        "审核质量阈值",
        min_value=1,
        max_value=10,
        value=st.session_state.get('review_threshold', 7),
        help="低于此分数的翻译将被标记为需要改进",
        disabled=not enable_review,
        key="sidebar_review_threshold"
    )
    
    auto_improve = st.sidebar.checkbox(
        "自动应用改进建议",
        value=st.session_state.get('auto_improve', False),
        help="当审核分数低于阈值时，自动使用改进后的翻译",
        disabled=not enable_review,
        key="sidebar_auto_improve"
    )
    
    # 保存配置到 session_state
    st.session_state.provider = provider
    st.session_state.config = config
    st.session_state.source_lang = source_lang
    st.session_state.target_lang = target_lang
    st.session_state.enable_review = enable_review
    st.session_state.review_threshold = review_threshold
    st.session_state.auto_improve = auto_improve
    
    # 保存配置按钮
    if st.sidebar.button("💾 保存配置"):
        save_config(provider, config, source_lang, target_lang)
        st.sidebar.success("✅ 配置已保存")
    
    return provider, config, source_lang, target_lang

def main_interface():
    """
    主界面
    """
    st.title("🎮 游戏本地化翻译助手")
    st.markdown("支持Excel、CSV、TXT文件的智能翻译，内置游戏术语纠错功能")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["📁 文件翻译", "📝 纠错管理", "📊 翻译历史", "ℹ️ 使用说明"])
    
    with tab1:
        file_translation_tab()
    
    with tab2:
        correction_management_tab()
    
    with tab3:
        translation_history_tab()
    
    with tab4:
        help_tab()

def file_translation_tab():
    """
    文件翻译标签页
    """
    st.header("📁 文件翻译")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择要翻译的文件",
        type=['xlsx', 'xls', 'csv', 'txt'],
        help="支持Excel (.xlsx, .xls)、CSV (.csv) 和文本 (.txt) 文件"
    )
    
    if uploaded_file is not None:
        # 保存上传的文件
        file_path = os.path.join(settings.UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # 读取文件
            df, metadata = file_handler.read_file(file_path)
            st.session_state.uploaded_file_data = df
            st.session_state.file_metadata = metadata
            
            st.success(f"✅ 文件上传成功: {uploaded_file.name}")
            
            # 显示文件信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("文件类型", metadata['file_type'].upper())
            with col2:
                st.metric("数据行数", len(df))
            with col3:
                st.metric("数据列数", len(df.columns))
            
            # 预览数据
            st.subheader("📋 数据预览")
            st.dataframe(df.head(10), use_container_width=True)
            
            # 选择要翻译的列
            if metadata['file_type'] != 'txt':
                st.subheader("🎯 选择翻译列")
                columns_to_translate = st.multiselect(
                    "选择需要翻译的列",
                    options=df.columns.tolist(),
                    default=df.columns.tolist(),
                    help="选择包含需要翻译文本的列",
                    key="file_translation_columns"
                )
            else:
                columns_to_translate = ['text']
            
            # 翻译按钮
            if st.button("🚀 开始翻译", type="primary", disabled=not st.session_state.translator_configured):
                if not st.session_state.translator_configured:
                    st.error("❌ 请先配置并测试翻译器")
                    return
                
                # 从 session_state 获取语言设置
                provider = st.session_state.get('provider', 'ollama')
                config = st.session_state.get('config', {})
                source_lang = st.session_state.get('source_lang', 'en')
                target_lang = st.session_state.get('target_lang', 'zh')
                
                # 执行翻译
                with st.spinner("翻译进行中，请稍候..."):
                    try:
                        # 提取需要翻译的内容
                        translatable_content = file_handler.extract_translatable_content(
                            df, columns_to_translate
                        )
                        
                        if not translatable_content:
                            st.warning("⚠️ 未找到需要翻译的内容")
                            return
                        
                        # 显示翻译进度
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # 批量翻译
                        translations = []
                        total_items = len(translatable_content)
                        
                        # 设置翻译器
                        translation_engine.set_translator(provider, **config)
                        
                        # 获取审核设置
                        enable_review = st.session_state.get('enable_review', False)
                        review_threshold = st.session_state.get('review_threshold', 7)
                        auto_improve = st.session_state.get('auto_improve', False)
                        
                        # 用于存储审核结果的列表
                        review_results = []
                        
                        for i, (row_idx, col_idx, text) in enumerate(translatable_content):
                            try:
                                # 使用asyncio运行异步翻译
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                translated_text = loop.run_until_complete(
                                    translation_engine.translate_with_correction(
                                        text, source_lang, target_lang
                                    )
                                )
                                
                                final_translation = translated_text
                                review_result = None
                                
                                # 如果启用了审核功能
                                if enable_review:
                                    try:
                                        # 执行翻译审核
                                        review_result = loop.run_until_complete(
                                            translation_engine.review_translation(
                                                text, translated_text, source_lang, target_lang
                                            )
                                        )
                                        
                                        # 检查审核结果
                                        if review_result and isinstance(review_result, dict):
                                            quality_score = review_result.get('quality_score', 10)
                                            is_acceptable = review_result.get('is_acceptable', True)
                                            improved_translation = review_result.get('improved_translation', translated_text)
                                            
                                            # 如果质量分数低于阈值且启用了自动改进
                                            if quality_score < review_threshold and auto_improve and improved_translation != translated_text:
                                                final_translation = improved_translation
                                                review_result['used_improvement'] = True
                                            else:
                                                review_result['used_improvement'] = False
                                            
                                            # 存储审核结果
                                            review_results.append({
                                                'row_idx': row_idx,
                                                'col_idx': col_idx,
                                                'original_text': text,
                                                'initial_translation': translated_text,
                                                'final_translation': final_translation,
                                                'review_result': review_result
                                            })
                                    
                                    except Exception as review_error:
                                        logger.error(f"审核失败: {text[:50]}... - {review_error}")
                                        # 审核失败时使用原始翻译
                                        review_results.append({
                                            'row_idx': row_idx,
                                            'col_idx': col_idx,
                                            'original_text': text,
                                            'initial_translation': translated_text,
                                            'final_translation': final_translation,
                                            'review_result': {'error': str(review_error)}
                                        })
                                
                                loop.close()
                                
                                translations.append((row_idx, col_idx, text, final_translation))
                                
                                # 更新进度
                                progress = (i + 1) / total_items
                                progress_bar.progress(progress)
                                
                                # 更新状态文本，显示审核信息
                                if enable_review and review_result:
                                    quality_score = review_result.get('quality_score', 'N/A')
                                    status_text.text(f"翻译进度: {i + 1}/{total_items} ({progress:.1%}) - 质量分数: {quality_score}")
                                else:
                                    status_text.text(f"翻译进度: {i + 1}/{total_items} ({progress:.1%})")
                                
                            except Exception as e:
                                logger.error(f"翻译失败: {text[:50]}... - {e}")
                                translations.append((row_idx, col_idx, text, text))  # 失败时保持原文
                                if enable_review:
                                    review_results.append({
                                        'row_idx': row_idx,
                                        'col_idx': col_idx,
                                        'original_text': text,
                                        'initial_translation': text,
                                        'final_translation': text,
                                        'review_result': {'error': str(e)}
                                    })
                        
                        # 更新DataFrame
                        translated_df = file_handler.update_dataframe_with_translations(
                            df, translations
                        )
                        
                        st.session_state.translation_results = translated_df
                        
                        progress_bar.progress(1.0)
                        status_text.text("✅ 翻译完成！")
                        
                        # 显示翻译和审核统计
                        if enable_review and review_results:
                            # 计算审核统计
                            total_reviewed = len([r for r in review_results if 'error' not in r['review_result']])
                            improved_count = len([r for r in review_results if r['review_result'].get('used_improvement', False)])
                            avg_score = sum([r['review_result'].get('quality_score', 0) for r in review_results if 'error' not in r['review_result']]) / max(total_reviewed, 1)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("翻译片段", len(translations))
                            with col2:
                                st.metric("审核通过", total_reviewed)
                            with col3:
                                st.metric("自动改进", improved_count)
                            
                            st.success(f"🎉 翻译完成！共翻译 {len(translations)} 个文本片段，平均质量分数: {avg_score:.1f}")
                            
                            # 存储审核结果到session_state
                            st.session_state.review_results = review_results
                        else:
                            st.success(f"🎉 翻译完成！共翻译 {len(translations)} 个文本片段")
                        
                    except Exception as e:
                        st.error(f"❌ 翻译过程中出现错误: {str(e)}")
                        logger.error(f"翻译错误: {e}")
            
            # 显示翻译结果
            if st.session_state.translation_results is not None:
                st.subheader("📊 翻译结果")
                st.dataframe(st.session_state.translation_results, use_container_width=True)
                
                # 显示审核结果（如果有）
                if hasattr(st.session_state, 'review_results') and st.session_state.review_results:
                    st.subheader("🔍 翻译审核详情")
                    
                    # 创建审核结果的DataFrame
                    review_data = []
                    for result in st.session_state.review_results:
                        review_info = result['review_result']
                        if 'error' not in review_info:
                            review_data.append({
                                '原文': result['original_text'][:50] + '...' if len(result['original_text']) > 50 else result['original_text'],
                                '初始翻译': result['initial_translation'][:50] + '...' if len(result['initial_translation']) > 50 else result['initial_translation'],
                                '最终翻译': result['final_translation'][:50] + '...' if len(result['final_translation']) > 50 else result['final_translation'],
                                '质量分数': review_info.get('quality_score', 'N/A'),
                                '是否可接受': '✅' if review_info.get('is_acceptable', True) else '❌',
                                '已改进': '✅' if review_info.get('used_improvement', False) else '❌',
                                '主要问题': ', '.join(review_info.get('issues', [])[:2]) if review_info.get('issues') else '无'
                            })
                    
                    if review_data:
                        review_df = pd.DataFrame(review_data)
                        st.dataframe(review_df, use_container_width=True)
                        
                        # 显示质量分布
                        col1, col2 = st.columns(2)
                        with col1:
                            # 质量分数分布
                            scores = [r['review_result'].get('quality_score', 0) for r in st.session_state.review_results if 'error' not in r['review_result']]
                            if scores:
                                import matplotlib.pyplot as plt
                                fig, ax = plt.subplots(figsize=(8, 4))
                                ax.hist(scores, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
                                ax.set_xlabel('质量分数')
                                ax.set_ylabel('频次')
                                ax.set_title('翻译质量分数分布')
                                st.pyplot(fig)
                        
                        with col2:
                            # 改进统计
                            improved_count = len([r for r in st.session_state.review_results if r['review_result'].get('used_improvement', False)])
                            total_count = len(st.session_state.review_results)
                            
                            st.write("**审核统计:**")
                            st.write(f"- 总翻译数: {total_count}")
                            st.write(f"- 自动改进: {improved_count}")
                            st.write(f"- 改进率: {improved_count/total_count*100:.1f}%" if total_count > 0 else "- 改进率: 0%")
                    else:
                        st.info("审核过程中遇到错误，无法显示详细结果")
                
                # 下载按钮
                output_path = file_handler.get_output_path(file_path)
                
                if st.button("💾 保存翻译结果"):
                    try:
                        saved_path = file_handler.save_file(
                            st.session_state.translation_results,
                            output_path,
                            st.session_state.file_metadata
                        )
                        st.success(f"✅ 文件已保存: {os.path.basename(saved_path)}")
                        
                        # 提供下载链接
                        with open(saved_path, "rb") as f:
                            st.download_button(
                                label="📥 下载翻译文件",
                                data=f.read(),
                                file_name=os.path.basename(saved_path),
                                mime="application/octet-stream"
                            )
                    except Exception as e:
                        st.error(f"❌ 保存文件失败: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ 文件读取失败: {str(e)}")
            logger.error(f"文件读取错误: {e}")

def correction_management_tab():
    """
    纠错管理标签页
    """
    st.header("📝 纠错管理")
    
    # 添加新的纠错条目
    st.subheader("➕ 添加纠错条目")
    
    col1, col2 = st.columns(2)
    with col1:
        source_text = st.text_input("原文")
        source_lang = st.selectbox(
            "原文语言",
            options=list(settings.SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: settings.SUPPORTED_LANGUAGES[x],
            key="correction_source_lang"
        )
    
    with col2:
        correct_translation = st.text_input("正确翻译")
        target_lang = st.selectbox(
            "目标语言",
            options=list(settings.SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: settings.SUPPORTED_LANGUAGES[x],
            key="correction_target_lang"
        )
    
    col3, col4 = st.columns(2)
    with col3:
        category = st.selectbox(
            "分类",
            options=["general", "game_term", "ui_text", "character_name", "skill_name", "item_name"],
            key="correction_category"
        )
    
    with col4:
        priority = st.slider("优先级", min_value=1, max_value=10, value=5)
    
    if st.button("✅ 添加纠错条目"):
        if source_text and correct_translation:
            success = db_manager.add_correction_entry(
                source_text, correct_translation, source_lang, target_lang, category, priority
            )
            if success:
                st.success("✅ 纠错条目添加成功！")
                st.rerun()
            else:
                st.error("❌ 添加失败，请检查输入")
        else:
            st.warning("⚠️ 请填写原文和正确翻译")
    
    # 显示现有纠错条目
    st.subheader("📋 现有纠错条目")
    
    # 过滤选项
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_source_lang = st.selectbox(
            "过滤源语言",
            options=["全部"] + list(settings.SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: "全部" if x == "全部" else settings.SUPPORTED_LANGUAGES[x],
            key="filter_source_lang"
        )
    
    with col2:
        filter_target_lang = st.selectbox(
            "过滤目标语言",
            options=["全部"] + list(settings.SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: "全部" if x == "全部" else settings.SUPPORTED_LANGUAGES[x],
            key="filter_target_lang"
        )
    
    # 获取纠错条目
    source_filter = None if filter_source_lang == "全部" else filter_source_lang
    target_filter = None if filter_target_lang == "全部" else filter_target_lang
    
    corrections = db_manager.get_all_corrections(source_filter, target_filter)
    
    if corrections:
        # 转换为DataFrame显示
        corrections_df = pd.DataFrame(corrections)
        
        # 选择要显示的列
        display_columns = ['id', 'source_text', 'correct_translation', 'source_language', 
                          'target_language', 'category', 'priority', 'updated_at']
        
        st.dataframe(
            corrections_df[display_columns],
            use_container_width=True,
            column_config={
                "id": "ID",
                "source_text": "原文",
                "correct_translation": "正确翻译",
                "source_language": "源语言",
                "target_language": "目标语言",
                "category": "分类",
                "priority": "优先级",
                "updated_at": "更新时间"
            }
        )
        
        # 删除纠错条目
        st.subheader("🗑️ 删除纠错条目")
        correction_to_delete = st.selectbox(
            "选择要删除的条目",
            options=[0] + [c['id'] for c in corrections],
            format_func=lambda x: "请选择" if x == 0 else f"ID:{x} - {next(c['source_text'] for c in corrections if c['id'] == x)[:30]}...",
            key="correction_to_delete"
        )
        
        if correction_to_delete != 0 and st.button("🗑️ 删除选中条目", type="secondary"):
            if db_manager.delete_correction(correction_to_delete):
                st.success("✅ 删除成功！")
                st.rerun()
            else:
                st.error("❌ 删除失败")
    else:
        st.info("📝 暂无纠错条目，请添加一些常用的翻译纠错")

def translation_history_tab():
    """
    翻译历史标签页
    """
    st.header("📊 翻译历史")
    
    # 获取翻译历史
    history = db_manager.get_translation_history(limit=100)
    
    if history:
        # 转换为DataFrame
        history_df = pd.DataFrame(history)
        
        # 显示统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总翻译数", len(history))
        with col2:
            avg_time = history_df['translation_time'].mean() if 'translation_time' in history_df.columns else 0
            st.metric("平均耗时", f"{avg_time:.2f}s")
        with col3:
            providers = history_df['api_provider'].value_counts()
            most_used = providers.index[0] if len(providers) > 0 else "无"
            st.metric("最常用API", most_used)
        with col4:
            languages = history_df['target_language'].value_counts()
            most_target = languages.index[0] if len(languages) > 0 else "无"
            st.metric("最常翻译到", settings.SUPPORTED_LANGUAGES.get(most_target, most_target))
        
        # 显示历史记录表格
        st.subheader("📋 翻译记录")
        
        # 选择显示的列
        display_columns = ['id', 'original_text', 'translated_text', 'source_language', 
                          'target_language', 'api_provider', 'model_name', 'translation_time', 'created_at']
        
        # 限制文本长度以便显示
        display_df = history_df[display_columns].copy()
        display_df['original_text'] = display_df['original_text'].str[:50] + '...'
        display_df['translated_text'] = display_df['translated_text'].str[:50] + '...'
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "id": "ID",
                "original_text": "原文",
                "translated_text": "译文",
                "source_language": "源语言",
                "target_language": "目标语言",
                "api_provider": "API提供商",
                "model_name": "模型",
                "translation_time": "耗时(秒)",
                "created_at": "创建时间"
            }
        )
    else:
        st.info("📊 暂无翻译历史记录")

def help_tab():
    """
    使用说明标签页
    """
    st.header("ℹ️ 使用说明")
    
    st.markdown("""
    ## 🎮 游戏本地化翻译助手使用指南
    
    ### 📋 功能特点
    - 🔄 支持多种文件格式：Excel (.xlsx, .xls)、CSV (.csv)、文本 (.txt)
    - 🤖 集成多种AI翻译服务：OpenAI、DeepSeek、千问、Ollama
    - 🔍 智能翻译审核：AI自动评估翻译质量并提供改进建议
    - 📝 智能纠错功能：预设游戏术语翻译对照表
    - 📊 翻译历史记录：追踪所有翻译操作
    - 🎯 批量处理：高效处理大量文本
    
    ### 🚀 快速开始
    
    #### 1. 配置翻译器
    - 在左侧边栏选择翻译服务提供商
    - 输入相应的API密钥和配置信息
    - 点击"测试连接"确保配置正确
    
    #### 2. 配置翻译审核（可选）
    - 启用"翻译审核"功能
    - 设置质量阈值（建议6-8分）
    - 选择是否自动应用改进建议
    
    #### 3. 上传文件
    - 在"文件翻译"标签页上传要翻译的文件
    - 系统会自动识别文件格式并显示预览
    - 对于Excel和CSV文件，可以选择需要翻译的列
    
    #### 4. 设置语言
    - 在左侧边栏选择源语言和目标语言
    - 支持中文、英语、日语、韩语等多种语言
    
    #### 5. 开始翻译
    - 点击"开始翻译"按钮
    - 系统会显示翻译进度和质量分数（如启用审核）
    - 翻译完成后可以预览结果和审核详情
    
    #### 6. 保存结果
    - 点击"保存翻译结果"将结果保存到本地
    - 可以下载翻译后的文件
    
    ### 🔍 翻译审核功能
    
    #### 功能介绍
    - **智能评分**：AI自动评估每个翻译的质量（0-10分）
    - **问题识别**：自动识别翻译中的语法、语义、术语等问题
    - **改进建议**：为低质量翻译提供具体的改进建议
    - **自动优化**：可选择自动应用改进建议
    
    #### 配置说明
    - **启用翻译审核**：开启后每次翻译都会进行质量评估
    - **审核质量阈值**：设置可接受的最低质量分数（1-10分，建议6-8分）
    - **自动应用改进建议**：启用后系统会自动使用改进后的翻译
    
    #### 审核结果
    - **质量分数分布图**：直观显示翻译质量分布
    - **详细审核表格**：显示每个翻译的评分和问题分析
    - **改进统计**：显示自动改进的数量和比例
    
    ### 📝 纠错功能
    
    #### 添加纠错条目
    - 在"纠错管理"标签页添加常用术语的正确翻译
    - 设置优先级，高优先级的条目会优先使用
    - 支持分类管理：游戏术语、UI文本、角色名等
    
    #### 自动纠错
    - 翻译时系统会首先查找纠错表
    - 如果找到匹配的条目，直接使用正确翻译
    - 没有找到才会调用AI翻译服务
    
    ### 🔧 支持的翻译服务
    
    #### OpenAI
    - 需要OpenAI API密钥
    - 支持GPT-3.5、GPT-4等模型
    - 翻译质量高，速度快
    
    #### DeepSeek
    - 需要DeepSeek API密钥
    - 国产AI服务，性价比高
    - 对中文支持较好
    
    #### 千问 (Qwen)
    - 需要阿里云API密钥
    - 阿里巴巴的AI服务
    - 支持多种语言翻译
    
    #### Ollama
    - 本地部署的AI模型
    - 无需API密钥，数据更安全
    - 需要本地安装Ollama服务
    
    ### 💡 使用技巧
    
    1. **批量处理**：一次上传多个文件可以提高效率
    2. **审核设置**：根据翻译要求合理设置质量阈值，重要内容建议设置较高阈值
    3. **自动改进**：对于大批量翻译建议启用自动改进，提高整体质量
    4. **纠错优化**：定期维护纠错表，提高翻译准确性
    5. **模型选择**：根据翻译质量要求选择合适的模型
    6. **格式保持**：系统会尽量保持原文件的格式和结构
    7. **历史查看**：通过翻译历史可以追踪和复用之前的翻译
    8. **质量监控**：定期查看审核统计，了解翻译质量趋势
    
    ### ⚠️ 注意事项
    
    - 确保API密钥的安全性，不要泄露给他人
    - 大文件翻译可能需要较长时间，请耐心等待
    - 建议在翻译前备份原始文件
    - 翻译结果仅供参考，重要内容请人工校对
    
    ### 🆘 常见问题
    
    **Q: 翻译失败怎么办？**
    A: 检查网络连接和API配置，确保API密钥有效且有足够余额。
    
    **Q: 如何提高翻译质量？**
    A: 维护好纠错表，选择合适的AI模型，对专业术语进行预设。
    
    **Q: 支持哪些文件大小？**
    A: 目前支持最大50MB的文件，建议分批处理大文件。
    
    **Q: 翻译数据会被保存吗？**
    A: 翻译历史会保存在本地数据库中，不会上传到云端。
    """)

def main():
    """
    主函数
    """
    # 初始化
    init_session_state()
    
    # 侧边栏配置
    provider, config, source_lang, target_lang = sidebar_config()
    
    # 主界面
    main_interface()
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>🎮 游戏本地化翻译助手 v1.0.0 | 让游戏本地化更简单</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()