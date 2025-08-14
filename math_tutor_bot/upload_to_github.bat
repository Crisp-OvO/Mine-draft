@echo off
chcp 65001 >nul
echo 🚀 正在准备上传到GitHub...

:: 设置变量
set REPO_URL=https://github.com/Crisp-OvO/Mine-draft.git
set PROJECT_NAME=math_tutor_bot
set TEMP_DIR=%TEMP%\github_upload_%RANDOM%

echo.
echo 📁 当前目录: %CD%
echo 🎯 目标仓库: %REPO_URL%
echo 📦 项目名称: %PROJECT_NAME%
echo.

:: 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到Git，请先安装Git
    echo 💡 下载地址：https://git-scm.com/download/win
    pause
    exit /b 1
)

:: 创建临时目录
echo 📂 创建临时工作目录...
mkdir "%TEMP_DIR%" 2>nul
cd /d "%TEMP_DIR%"

:: 克隆仓库
echo 📥 正在克隆仓库...
git clone "%REPO_URL%" repo
if errorlevel 1 (
    echo ❌ 克隆失败，请检查网络连接和仓库权限
    pause
    exit /b 1
)

cd repo

:: 创建项目文件夹
echo 📁 创建项目文件夹...
if exist "%PROJECT_NAME%" rmdir /s /q "%PROJECT_NAME%"
mkdir "%PROJECT_NAME%"

:: 复制项目文件
echo 📋 正在复制项目文件...
xcopy "%~dp0*" "%PROJECT_NAME%\" /E /H /Y /EXCLUDE:%~dp0upload_exclude.txt 2>nul

:: 创建.gitignore
echo 📝 创建.gitignore文件...
(
echo # 环境配置
echo .env
echo *.log
echo.
echo # 记忆数据（可选）
echo memory_data.json
echo.
echo # Python
echo __pycache__/
echo *.pyc
echo *.pyo
echo .pytest_cache/
echo.
echo # 上传脚本
echo upload_to_github.bat
echo upload_exclude.txt
echo.
echo # IDE
echo .vscode/
echo .idea/
) > "%PROJECT_NAME%\.gitignore"

:: 创建README
echo 📖 创建README文件...
(
echo # 智能数学教学助手
echo.
echo 基于阿里云百炼大模型的小学数学解方程教学系统，支持长期记忆、个性化引导和知识库检索。
echo.
echo ## ✨ 特性
echo.
echo - 🤖 智能分步解题引导
echo - 🧠 长期记忆与个性化教学  
echo - 😊 多样化表情/引导词系统（30+种状态）
echo - 📚 知识库检索集成
echo - 💬 控制台友好输出
echo - 🔄 "我不会"跟进处理
echo.
echo ## 🚀 快速开始
echo.
echo ```powershell
echo # 1. 安装依赖
echo pip install -r requirements.txt
echo.
echo # 2. 配置环境
echo copy env\.env.example .env
echo # 编辑 .env 填入你的API密钥
echo.
echo # 3. 运行
echo python main.py
echo ```
echo.
echo ## ⚙️ 配置说明
echo.
echo 详见 `env/.env.example` 配置模板。需要配置：
echo - BOT_API_KEY: 阿里云百炼API密钥
echo - AGENT_ID: 模型名称（如qwen-plus）
echo - KB_SEARCH_URL: 知识库检索地址（可选）
echo - KB_ID: 知识库ID（可选）
echo.
echo ## 📁 项目结构
echo.
echo ```
echo math_tutor_bot/
echo ├── main.py                 # 主程序
echo ├── config.py               # 配置管理
echo ├── bot_client.py           # API客户端
echo ├── memory_manager.py       # 记忆管理
echo ├── knowledge_manager.py    # 知识库管理
echo ├── requirements.txt        # 依赖包
echo └── env/
echo     ├── .env.example        # 配置模板
echo     └── emoji_lexicon.json  # 表情词典
echo ```
echo.
echo ## 🎯 使用示例
echo.
echo 1. 输入简单题目：`5x + 3 = 18` → 一次性完整解法
echo 2. 输入复杂题目：`3(x-2)+5=2x+9` → 分步引导
echo 3. 回复"我不会"或"继续" → 继续当前题目的下一步
echo.
echo ## 📄 开源许可
echo.
echo MIT License
) > "%PROJECT_NAME%\README.md"

:: 添加所有文件
echo ➕ 添加文件到Git...
git add .

:: 提交更改
echo 💾 提交更改...
git commit -m "✨ 添加智能数学教学助手项目

- 支持阿里云百炼大模型调用
- 长期记忆与个性化教学系统
- 多样化表情/引导词库（30+种状态）
- 知识库检索集成
- 分步解题引导逻辑
- 控制台友好输出格式
- '我不会'跟进处理机制"

:: 推送到远程仓库
echo 🚀 正在推送到GitHub...
git push origin main
if errorlevel 1 (
    echo ❌ 推送失败，可能需要身份验证
    echo 💡 请确保已配置GitHub访问权限（Personal Access Token或SSH密钥）
    echo 🔗 设置指南：https://docs.github.com/en/authentication
) else (
    echo ✅ 上传成功！
    echo 🌐 访问地址：https://github.com/Crisp-OvO/Mine-draft/tree/main/%PROJECT_NAME%
)

:: 清理临时文件
echo 🧹 清理临时文件...
cd /d "%~dp0"
rmdir /s /q "%TEMP_DIR%" 2>nul

echo.
echo 🎉 操作完成！
pause 