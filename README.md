# 🎮 游戏本地化翻译助手 (Game Translator Pro)

一个专为游戏本地化设计的智能翻译工具，支持多种文件格式和AI翻译服务，内置游戏术语纠错功能和智能翻译审核系统。

## ✨ 功能特点

- 🔄 **多格式支持**: Excel (.xlsx, .xls)、CSV (.csv)、文本 (.txt)
- 🤖 **多AI集成**: OpenAI、DeepSeek、千问、Ollama等主流AI服务
- 🔍 **智能审核**: AI自动评估翻译质量并提供改进建议
- 📝 **智能纠错**: 内置游戏术语对照表，优先使用准确翻译
- 📊 **批量处理**: 高效处理大量文本内容
- 🎯 **游戏优化**: 专门针对游戏内容的翻译优化
- 📈 **历史追踪**: 完整的翻译历史记录和统计分析
- 🌐 **多语言**: 支持中英日韩法德西俄葡意等多种语言互译
- 💻 **友好界面**: 基于Streamlit的现代化Web界面
- ⚙️ **配置保存**: 自动保存翻译器配置和用户偏好设置

## 🚀 快速开始

### 环境要求

- Python 3.10+
- macOS / Windows / Linux

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd translate
```

2. **创建虚拟环境**
```bash
# 创建Python 3.10虚拟环境
python3.10 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的API密钥
nano .env
```

5. **启动应用**
```bash
# 使用启动脚本（推荐）
python run.py

# 或直接启动Streamlit
streamlit run app.py
```

6. **访问应用**

打开浏览器访问: http://localhost:8501

## 📁 项目结构

```
translate/
├── app.py                 # Streamlit主应用
├── run.py                 # 启动脚本
├── config.py              # 配置管理
├── database.py            # 数据库操作
├── file_handler.py        # 文件处理
├── translator.py          # 翻译引擎
├── requirements.txt       # 依赖包列表
├── .env.example          # 环境变量模板
├── README.md             # 项目说明
├── uploads/              # 上传文件目录
├── outputs/              # 输出文件目录
├── logs/                 # 日志文件目录
└── translation_db.sqlite # SQLite数据库
```

## 🔧 配置说明

### API配置

在`.env`文件中配置你的API密钥：

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 千问
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Ollama (本地)
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

### 支持的翻译服务

| 服务商 | 特点 | 配置要求 | 审核支持 |
|--------|------|----------|----------|
| OpenAI | 翻译质量高，速度快 | API密钥 | ✅ |
| DeepSeek | 性价比高，中文友好 | API密钥 | ✅ |
| 千问 | 阿里云服务，稳定 | API密钥 | ✅ |
| Ollama | 本地部署，数据安全 | 本地安装 | ✅ |

## 📖 使用指南

### 1. 文件翻译

1. **配置翻译器**: 在侧边栏选择AI服务并配置API密钥
2. **上传文件**: 支持Excel、CSV、TXT格式
3. **选择列**: 对于表格文件，选择需要翻译的列
4. **设置语言**: 选择源语言和目标语言
5. **配置审核**: 可选启用翻译质量审核功能
6. **开始翻译**: 系统会显示进度并自动处理
7. **查看审核**: 查看翻译质量评分和改进建议
8. **保存结果**: 下载翻译后的文件

### 2. 翻译审核功能

- **智能评分**: AI自动评估每个翻译的质量（0-10分）
- **问题识别**: 自动识别语法、语义、术语等问题
- **改进建议**: 为低质量翻译提供具体改进方案
- **自动优化**: 可选择自动应用改进建议
- **质量阈值**: 设置可接受的最低质量分数
- **统计分析**: 显示质量分布图和改进统计

### 3. 纠错管理

- **添加术语**: 为常用游戏术语添加标准翻译
- **设置优先级**: 高优先级术语会优先使用
- **分类管理**: 支持游戏术语、UI文本、角色名等分类
- **自动匹配**: 翻译时优先查找纠错表中的准确翻译
- **批量管理**: 支持批量添加和删除纠错条目

### 4. 翻译历史

- **记录追踪**: 查看所有翻译历史和详细信息
- **统计分析**: 翻译数量、耗时、API使用统计
- **质量监控**: 翻译质量趋势和分布分析
- **数据导出**: 支持导出历史记录进行分析

## 🎮 游戏翻译优化

### 内置游戏术语

系统预设了常用游戏术语的标准翻译：

**基础属性**
- HP → 生命值
- MP → 魔法值
- EXP → 经验值
- Level → 等级
- Attack → 攻击力
- Defense → 防御力
- Speed → 速度
- Critical → 暴击

**游戏元素**
- Skill → 技能
- Item → 道具
- Equipment → 装备
- Weapon → 武器
- Armor → 护甲
- Quest → 任务
- Mission → 任务
- Boss → 首领

**社交系统**
- Guild → 公会
- Team → 队伍
- Player → 玩家
- Character → 角色

### 翻译策略

1. **术语优先**: 首先查找纠错表中的标准翻译
2. **智能审核**: AI评估翻译质量并提供改进建议
3. **上下文感知**: 考虑游戏语境进行翻译
4. **风格保持**: 保持角色对话的一致性
5. **格式保留**: 维持原文件的结构和格式
6. **质量控制**: 通过阈值设置确保翻译质量

## 🔍 高级功能

### 批量翻译与审核

```python
# 批量翻译示例
from translator import translation_engine
from file_handler import file_handler

# 设置翻译器
translation_engine.set_translator("openai", api_key="your_key")

# 读取文件
df, metadata = file_handler.read_file("game_text.xlsx")

# 提取翻译内容
content = file_handler.extract_translatable_content(df)

# 批量翻译（带纠错）
translations = await translation_engine.translate_batch_with_correction(
    [text for _, _, text in content], "en", "zh"
)

# 翻译质量审核
for original, translated in zip(original_texts, translations):
    review_result = await translation_engine.review_translation(
        original, translated, "en", "zh"
    )
    print(f"质量评分: {review_result['score']}/10")
    if review_result['score'] < 7:
        print(f"改进建议: {review_result['improved_translation']}")
```

### 自定义翻译器

```python
from translator import BaseTranslator

class CustomTranslator(BaseTranslator):
    async def translate_text(self, text, source_lang, target_lang):
        # 实现自定义翻译逻辑
        return translated_text
    
    async def review_translation(self, original_text, translated_text, source_lang, target_lang):
        # 实现自定义审核逻辑
        return {
            "score": 8,
            "issues": [],
            "improved_translation": translated_text
        }
```

### 纠错表管理

```python
from database import db_manager

# 添加纠错条目
db_manager.add_correction_entry(
    source_text="HP",
    correct_translation="生命值",
    source_lang="en",
    target_lang="zh",
    category="game_term",
    priority=10
)

# 查找纠错翻译
correction = db_manager.get_correction("HP", "en", "zh")
if correction:
    print(f"使用纠错翻译: {correction}")
```

## 📊 性能优化

- **并发处理**: 支持异步批量翻译和审核
- **智能缓存**: 重复内容自动缓存，纠错表优先匹配
- **错误重试**: 自动重试失败的翻译和审核
- **进度显示**: 实时显示翻译进度和质量评分
- **质量控制**: 通过阈值设置自动筛选和改进翻译
- **配置持久化**: 自动保存用户配置和偏好设置
- **批量审核**: 支持批量质量评估和改进建议

## 🛠️ 开发指南

### 代码结构

- **模块化设计**: 每个功能独立模块
- **接口统一**: 统一的翻译器接口
- **配置分离**: 配置与代码分离
- **错误处理**: 完善的异常处理机制

### 扩展开发

1. **添加新的翻译服务**:
   - 继承`BaseTranslator`类
   - 实现`translate_text`方法
   - 在`TranslationEngine`中注册

2. **支持新的文件格式**:
   - 在`FileHandler`中添加读写方法
   - 更新支持格式列表

3. **自定义纠错规则**:
   - 扩展数据库表结构
   - 实现自定义匹配逻辑

## 🐛 故障排除

### 常见问题

**Q: 翻译失败，显示API错误**
A: 检查API密钥是否正确，账户是否有余额，网络连接是否正常

**Q: 文件上传失败**
A: 检查文件格式和大小，确保在支持范围内（最大50MB）

**Q: 翻译速度很慢**
A: 可能是网络问题或API限制，尝试更换服务商或关闭翻译审核功能

**Q: 纠错表不生效**
A: 检查术语匹配是否精确，注意大小写和空格，确保优先级设置正确

**Q: 翻译审核功能无法使用**
A: 确保选择的AI服务支持审核功能，检查API配置是否正确

**Q: 质量评分偏低**
A: 可以调整质量阈值，或者检查源文本是否包含特殊字符或格式

**Q: 自动改进不生效**
A: 检查是否启用了"自动应用改进建议"选项，确保质量阈值设置合理

**Q: 配置无法保存**
A: 检查data目录是否有写入权限，确保配置文件没有被占用

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 🔒 安全说明

- **API密钥**: 妥善保管API密钥，不要提交到版本控制
- **数据隐私**: 翻译数据仅存储在本地数据库
- **网络安全**: 使用HTTPS连接API服务
- **文件安全**: 上传文件会在本地处理，不会上传到云端

## 📝 更新日志

### v0.0.1
- ✨ 初始版本发布
- 🔄 支持Excel、CSV、TXT文件格式
- 🤖 集成OpenAI、DeepSeek、千问、Ollama四大AI服务
- 🔍 智能翻译审核系统，AI自动评估翻译质量
- 📝 内置游戏术语纠错功能，支持20+常用游戏术语
- 💻 基于Streamlit的现代化Web界面
- 📊 完整的翻译历史记录和统计分析
- ⚙️ 配置自动保存和恢复功能
- 🎯 专门针对游戏本地化的翻译优化
- 🌐 支持10种主流语言互译
- 📈 实时翻译进度显示和质量监控
- 🔧 灵活的质量阈值和自动改进设置

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情

## 🙏 致谢

- [Streamlit](https://streamlit.io/) - 优秀的Web应用框架
- [Pandas](https://pandas.pydata.org/) - 强大的数据处理库
- [OpenAI](https://openai.com/) - 先进的AI翻译服务
- [Loguru](https://github.com/Delgan/loguru) - 简洁的日志库

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: songpl911@gmail.com

---

**🎮 让游戏本地化更简单！**
