pyinstaller gui.py
echo d | xcopy .\config .\dist\gui\config /s /f /h /y
echo d | xcopy .\browsermob-proxy .\dist\gui\browsermob-proxy /s /f /h /y
echo a | copy ffprobe.exe .\dist\gui\ffprobe.exe 
echo a | copy ffplay.exe .\dist\gui\ffplay.exe 
echo a | copy ffmpeg.exe .\dist\gui\ffmpeg.exe 
echo a | copy chromedriver.exe .\dist\gui\chromedriver.exe 
pause