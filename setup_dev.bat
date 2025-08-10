@echo off
chcp 65001
echo.
echo ================================================
echo   GPT Researcher 开发环境配置脚本
echo ================================================
echo.

echo [1/4] 检查 Python 版本...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

echo.
echo [2/4] 创建虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo 错误: 创建虚拟环境失败
    pause
    exit /b 1
)

echo.
echo [3/4] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [4/4] 复制环境配置文件...
if not exist .env (
    copy config.env .env
    echo 已创建 .env 文件，请编辑其中的 API 密钥
) else (
    echo .env 文件已存在，跳过创建
)

echo.
echo ================================================
echo   安装完成！
echo ================================================
echo.
echo 接下来的步骤：
echo 1. 编辑 .env 文件，填入您的 API 密钥
echo 2. 运行: venv\Scripts\activate.bat
echo 3. 运行: python -m uvicorn main:app --reload
echo 4. 打开浏览器访问: http://localhost:8000
echo.
pause
