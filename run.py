#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏本地化翻译助手启动脚本
用于启动Streamlit应用
"""

import os
import sys
import subprocess
from pathlib import Path
from loguru import logger

def setup_logging():
    """
    设置日志配置
    """
    # 创建logs目录
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 配置loguru
    logger.remove()  # 移除默认处理器
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 添加文件输出
    logger.add(
        logs_dir / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8"
    )

def check_dependencies():
    """
    检查依赖包是否安装
    """
    logger.info("检查依赖包...")
    
    required_packages = [
        "streamlit",
        "pandas",
        "openpyxl",
        "chardet",
        "httpx",
        "loguru",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.debug(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} 未安装")
    
    if missing_packages:
        logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
        logger.info("请运行以下命令安装依赖:")
        logger.info("pip install -r requirements.txt")
        return False
    
    logger.info("✅ 所有依赖包已安装")
    return True

def setup_environment():
    """
    设置环境
    """
    logger.info("设置环境...")
    
    # 检查.env文件
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        logger.warning("未找到.env文件，正在从.env.example创建...")
        env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
        logger.info("✅ .env文件已创建，请编辑并填入你的API密钥")
    
    # 创建必要的目录
    directories = ["uploads", "outputs", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.debug(f"✅ 目录已创建: {directory}")
    
    logger.info("✅ 环境设置完成")

def initialize_database():
    """
    初始化数据库
    """
    logger.info("初始化数据库...")
    
    try:
        # 导入数据库模块来触发初始化
        from database import db_manager
        
        # 初始化默认纠错条目
        db_manager.init_default_corrections()
        
        logger.info("✅ 数据库初始化完成")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return False

def run_streamlit():
    """
    启动Streamlit应用
    """
    logger.info("启动Streamlit应用...")
    
    # Streamlit配置
    streamlit_config = {
        "server.port": 8501,
        "server.address": "localhost",
        "server.headless": False,
        "browser.gatherUsageStats": False,
        "theme.base": "light",
        "theme.primaryColor": "#FF6B6B",
        "theme.backgroundColor": "#FFFFFF",
        "theme.secondaryBackgroundColor": "#F0F2F6",
        "theme.textColor": "#262730"
    }
    
    # 构建命令
    cmd = ["streamlit", "run", "app.py"]
    
    # 添加配置参数
    for key, value in streamlit_config.items():
        cmd.extend(["--server.port" if key == "server.port" else f"--{key}", str(value)])
    
    try:
        logger.info(f"执行命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Streamlit启动失败: {e}")
        return False
    except KeyboardInterrupt:
        logger.info("👋 用户中断，正在退出...")
        return True
    except Exception as e:
        logger.error(f"❌ 启动过程中出现错误: {e}")
        return False

def main():
    """
    主函数
    """
    print("🎮 游戏本地化翻译助手启动器")
    print("=" * 50)
    
    # 设置日志
    setup_logging()
    
    logger.info("🚀 启动游戏本地化翻译助手...")
    
    # 检查依赖
    if not check_dependencies():
        logger.error("❌ 依赖检查失败，请安装缺少的包")
        sys.exit(1)
    
    # 设置环境
    setup_environment()
    
    # 初始化数据库
    if not initialize_database():
        logger.error("❌ 数据库初始化失败")
        sys.exit(1)
    
    # 显示启动信息
    logger.info("🎉 准备工作完成！")
    logger.info("📱 应用将在浏览器中打开: http://localhost:8501")
    logger.info("⏹️  按 Ctrl+C 停止应用")
    logger.info("=" * 50)
    
    # 启动应用
    success = run_streamlit()
    
    if success:
        logger.info("👋 应用已正常退出")
    else:
        logger.error("❌ 应用异常退出")
        sys.exit(1)

if __name__ == "__main__":
    main()