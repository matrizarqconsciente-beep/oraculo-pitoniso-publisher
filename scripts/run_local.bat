@echo off
chcp 65001 >nul
title Publicador Oraculo Pitoniso

set REPO_DIR=C:\Users\Paul\oraculo_pitoniso\oraculo-pitoniso-publisher
set BOT_DIR=C:\Users\Paul\oraculo_pitoniso\trance-trading-competition\data
set LOG=%REPO_DIR%\output\publish_log.txt
set PYTHON=C:\Users\Paul\AppData\Local\Programs\Python\Python312\python.exe

echo. >> "%LOG%"
echo === %date% %time% === >> "%LOG%"

if exist "%BOT_DIR%\competition_results.json" (
    copy /Y "%BOT_DIR%\competition_results.json" "%REPO_DIR%\data\competition_results.json" >nul
    echo Datos de competencia copiados >> "%LOG%"
)
if exist "%BOT_DIR%\golden_trades_pending.json" (
    copy /Y "%BOT_DIR%\golden_trades_pending.json" "%REPO_DIR%\data\golden_trades_pending.json" >nul
    echo Golden trades copiados >> "%LOG%"
)

cd /d "%REPO_DIR%"

set HOUR=%time:~0,2%
if %HOUR% LSS 10 set HOUR=0%time:~1,1%

if %HOUR%==08 (
    REM Arranque: todos los formatos
    %PYTHON% social_publisher.py all >> "%LOG%" 2>&1
) else if %HOUR%==10 (
    REM Para los que arrancan el dia: aprender a operar
    %PYTHON% social_publisher.py beginner >> "%LOG%" 2>&1
) else if %HOUR%==12 (
    REM Educativo: como funciona el ecosistema
    %PYTHON% social_publisher.py explainer >> "%LOG%" 2>&1
) else if %HOUR%==14 (
    REM Actualizacion ranking + trade
    %PYTHON% social_publisher.py ranking >> "%LOG%" 2>&1
    %PYTHON% social_publisher.py golden >> "%LOG%" 2>&1
) else if %HOUR%==16 (
    REM Tarde: atraer nuevos con aprender a operar
    %PYTHON% social_publisher.py beginner >> "%LOG%" 2>&1
) else if %HOUR%==18 (
    REM Trade destacado
    %PYTHON% social_publisher.py golden >> "%LOG%" 2>&1
) else if %HOUR%==20 (
    REM Cierre: trade + resumen
    %PYTHON% social_publisher.py golden >> "%LOG%" 2>&1
    %PYTHON% social_publisher.py daily >> "%LOG%" 2>&1
) else (
    REM Ultimo post del dia
    %PYTHON% social_publisher.py golden >> "%LOG%" 2>&1
)
