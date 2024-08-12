@echo on
set PY_FILE=stadium_converter.py
set PROJECT_NAME=PES4-WE8 Stadium Converter
set VERSION=1.0.0
set FILE_VERSION=file_version_info.txt
set ICO_DIR=pes_indie.ico
set EXTRA_ARG=--add-data=resources/*;resources
pyinstaller --onefile "%PY_FILE%" --icon="%ICO_DIR%" --name "%PROJECT_NAME%_%VERSION%"  %EXTRA_ARG%  --version-file "%FILE_VERSION%"

cd dist
tar -acvf "%PROJECT_NAME%_%VERSION%.zip" *
pause
