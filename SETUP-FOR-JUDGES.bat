@echo off
echo ========================================
echo Aura Desktop Assistant - Judge Setup
echo ========================================
echo.
echo Welcome judges! This script will set up
echo the complete desktop demo in one step.
echo.
echo What this will do:
echo   ✅ Verify system requirements
echo   ✅ Install all dependencies  
echo   ✅ Set up the backend server
echo   ✅ Create demo data
echo   ✅ Launch the desktop application
echo.
echo Expected time: 2-3 minutes
echo.
pause

:: Run the complete setup
call local-test\desktop-demo-complete.bat

echo.
echo ========================================
echo 🎉 SETUP COMPLETE!
echo ========================================
echo.
echo The Aura Desktop Assistant is now running.
echo.
echo 📋 Quick Test Guide:
echo   1. Press Ctrl+' to activate Aura
echo   2. Say: "Create a meeting notes document"
echo   3. Check the documents folder for results
echo.
echo 🏆 You're ready to evaluate the submission!
echo.
pause