@echo off

REM Definir o caminho do Python
set PYTHON_PATH=C:\Users\gabi1\AppData\Local\Programs\Python\Python312\python.exe

echo Installing required Python package pywin32
"%PYTHON_PATH%" -m pip install pywin32

echo Installing the Python service
"%PYTHON_PATH%" "%~dp0\server_service.py" install

echo Starting the Python service
"%PYTHON_PATH%" "%~dp0\server_service.py" start

echo Service setup completed

set /p resposta=Você deseja parar o serviço agora? (sim/não): 

if /i "%resposta%"=="sim" (
    echo Tentando parar o serviço...
    "%PYTHON_PATH%" "%~dp0\server_service.py" stop
    
    REM Pausa para garantir que o serviço tenha tempo para parar
    timeout /t 5 /nobreak > nul

    REM Verifica se o serviço ainda está em execução
    echo Verificando se o serviço foi parado corretamente...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9999') do (
        set PID=%%a
    )

    if defined PID (
        echo O serviço não foi parado corretamente. Tentando finalizar o processo com PID %PID%...
        taskkill /PID %PID% /F

        REM Segunda verificação
        echo Verificando novamente se o processo foi finalizado...
        timeout /t 5 /nobreak > nul
        set PID=

        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9999') do (
            set PID=%%a
        )

        if defined PID (
            echo Falha ao finalizar o processo com PID %PID%. Por favor, finalize manualmente.
        ) else (
            echo Processo finalizado com sucesso.
        )
    ) else (
        echo Serviço parado com sucesso.
    )
) else (
    echo Operação cancelada. O serviço não foi alterado.
)

pause
