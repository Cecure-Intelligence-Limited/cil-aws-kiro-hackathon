@echo off
echo Cleaning up test artifacts...

cd /d "%~dp0"

echo Removing duplicate test files...
if exist backend\documents\documents rmdir /s /q backend\documents\documents
if exist backend\documents\hackathon-test.txt del /f /q backend\documents\hackathon-test.txt

echo Cleaning up any temporary files...
if exist *.tmp del /f /q *.tmp
if exist backend\*.tmp del /f /q backend\*.tmp

echo Test cleanup complete!