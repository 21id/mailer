@echo off
setlocal enabledelayedexpansion

for /f "usebackq tokens=*" %%a in (".env") do (
    set "line=%%a"
    if not "!line!"=="" if "!line:~0,1!" NEQ "#" (
        for /f "tokens=1,* delims==" %%b in ("!line!") do set "%%b=%%c"
    )
)

set "SMTP_FROM=21ID <no-reply@21id.uz>"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
