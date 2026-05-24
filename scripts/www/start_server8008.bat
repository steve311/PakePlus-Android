@echo off
chcp 65001 >nul
title 白马咖啡店 - 本地服务器

echo ========================================
echo    ☕ 白马咖啡店 · 前世今生
echo    正在启动本地服务器...
echo ========================================
echo.

:: 检查是否安装了 npx
where npx >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 npx，请先安装 Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

:: 获取当前目录路径
set "CURRENT_DIR=%cd%"
echo [信息] 工作目录: %CURRENT_DIR%
echo [信息] 启动端口: 8008
echo.

:: 启动 serve 服务
echo [启动] 正在启动服务器，请稍候...
echo [提示] 启动成功后，请在浏览器访问: http://localhost:8008
echo [提示] 按 Ctrl+C 可停止服务器
echo.

npx serve . -p 8008

pause