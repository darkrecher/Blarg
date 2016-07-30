@echo off

c:\python25\python.exe pygame2exe.py
copy blarg_windowed.bat dist
cd dist
ren zemain.exe blarg.exe

echo.
echo.
echo Construction finie. Si vous appuyez sur une touche maitenant, la fenetre va se fermer.
echo.
PAUSE