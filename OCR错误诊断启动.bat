@echo off
chcp 65001 >nul
title OCR错误深度诊断系统

echo.
echo 🔬 ==========================================
echo    OCR错误深度诊断系统 - 专业版
echo ==========================================
echo.
echo 🎯 诊断能力:
echo    ✅ 详细API错误分析 (HTTP 400/401/403/500)
echo    ✅ 图片格式兼容性测试
echo    ✅ 多种尺寸适配测试
echo    ✅ Base64编码验证
echo    ✅ 内置测试图片 + 自定义上传
echo    ✅ 实时错误日志分析
echo.

echo 🔧 配置API密钥...
set DASHSCOPE_API_KEY=sk-2763f2c284eb4503845e73ff6b58c172

echo 📂 进入项目目录...
cd /d "%~dp0math-solver-backend"

echo.
echo 🚀 启动升级版OCR诊断后端...
echo    服务地址: http://localhost:3001
echo    诊断页面: http://localhost:3001/ocr-debug-advanced.html
echo.
echo 💡 诊断流程:
echo    1. 选择内置测试图片或上传您的图片
echo    2. 执行完整诊断 (图片分析+API测试+OCR识别)
echo    3. 查看详细的错误分析和解决建议
echo    4. 测试不同格式和尺寸的兼容性
echo.

start "" node server.js

echo 📱 正在打开OCR错误诊断专家页面...
timeout /t 3 /nobreak >nul
start "" "http://localhost:3001/ocr-debug-advanced.html"

echo.
echo ✅ 诊断系统启动完成！
echo.
echo 🔍 诊断提示:
echo    • 首先尝试内置的简单测试图片
echo    • 如果内置图片也失败，说明是API配置问题
echo    • 如果内置图片成功，您的图片失败，说明是图片质量问题
echo    • 查看详细的错误日志来定位具体原因
echo.
echo 📞 如果需要更多帮助，请提供:
echo    • 具体的HTTP错误代码
echo    • API响应的详细信息
echo    • 图片的格式和大小信息
echo.
echo 按任意键退出...
pause >nul 