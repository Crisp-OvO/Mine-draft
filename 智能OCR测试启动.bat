@echo off
chcp 65001 >nul
title 智能OCR测试工具启动器

echo.
echo 🧠 ==========================================
echo    智能OCR测试工具 - 多策略识别系统
echo ==========================================
echo.
echo 🎯 功能特点:
echo    ✅ 多策略识别算法 (高精度/简化/数学专用)
echo    ✅ 自动图片质量分析
echo    ✅ 智能改进建议系统
echo    ✅ 置信度计算和错误诊断
echo.

echo 🔧 配置API密钥...
set DASHSCOPE_API_KEY=sk-2763f2c284eb4503845e73ff6b58c172

echo 📂 进入项目目录...
cd /d "%~dp0math-solver-backend"

echo.
echo 🚀 启动智能OCR后端服务...
echo    服务地址: http://localhost:3001
echo    测试页面: http://localhost:3001/smart-ocr-test.html
echo.
echo 💡 使用说明:
echo    1. 等待服务启动完成
echo    2. 浏览器会自动打开测试页面
echo    3. 上传数学题图片进行智能识别
echo    4. 查看详细的质量分析和改进建议
echo.

start "" node server.js

echo 📱 正在打开智能OCR测试页面...
timeout /t 3 /nobreak >nul
start "" "http://localhost:3001/smart-ocr-test.html"

echo.
echo ✅ 启动完成！浏览器应该已经打开测试页面
echo.
echo 🔍 注意事项:
echo    • 确保图片清晰、光线充足
echo    • 支持拖拽上传图片
echo    • 系统会自动选择最佳识别策略
echo    • 识别失败时会提供具体改进建议
echo.
echo 按任意键退出...
pause >nul 