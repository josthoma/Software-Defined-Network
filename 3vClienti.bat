#!/bin/sh
REM #Troubleshooting Tool, quickly makes Clients from ID 1 to 6
REM #Save hostname as HOST
REM ##python Client.py 1 DESKTOP-865AFU4 1234
FOR /F "usebackq" %%i IN (`hostname`) DO SET HOST=%%i  
start cmd /K python Client.py 1 %HOST% 1234
start cmd /K python Client.py 2 %HOST% 1234
cmd /K python Client.py 3 %HOST% 1234 -v
