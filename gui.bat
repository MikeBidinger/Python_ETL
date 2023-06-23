@echo OFF 
set CONDAPATH=C:\Users\MB91448\Anaconda3
set ENVNAME=base

if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

python gui.py

call conda deactivate
