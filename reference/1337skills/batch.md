# Batch Scripting intermediate

Batch scripting for Windows provides command-line automation through .bat and .cmd files. This guide covers variables, control structures, file operations, and practical examples.

## File Basics

### Creating Batch Files

```batch
@echo off
REM This is a comment
REM Batch files end with .bat or .cmd extension

echo Hello, World!
pause
```

### Execution

```bash
# Run batch file
script.bat

# Run with parameters
script.bat param1 param2

# Run from different directory
C:\path\to\script.bat

# Run minimized
start /min script.bat

# Run with elevated privileges
runas /user:Administrator script.bat
```

## Basic Commands

| Command | Description |
| --- | --- |
| `@echo off` | Turn off command echoing |
| `echo <text>` | Display text |
| `cls` | Clear screen |
| `pause` | Wait for user input |
| `exit` | Exit script |
| `title <name>` | Set window title |
| `dir` | List files and directories |
| `cd <path>` | Change directory |

## Variables

### Variable Declaration and Usage

```batch
@echo off

REM Set variable
set name=John
set age=30
set path=C:\Users\Documents

REM Display variable
echo %name%
echo Age: %age%

REM Concatenate variables
set fulltext=Hello %name%, you are %age% years old
echo %fulltext%

REM Variable with spaces
set "message=This is a long message with spaces"
echo %message%
```

### Special Variables

```batch
@echo off

REM Script parameters
echo Script name: %0
echo First parameter: %1
echo Second parameter: %2
echo All parameters: %*

REM System variables
echo User: %username%
echo Computer: %computername%
echo OS: %OS%
echo Current directory: %cd%
echo Temp folder: %temp%
echo System drive: %systemdrive%

REM Error code (last command)
dir nonexistent.file 2>nul
echo Error code: %errorlevel%
```

### Delayed Expansion

```batch
@echo off
setlocal enabledelayedexpansion

REM Without delayed expansion (won't work as expected)
set count=1
if %count%==1 (
    set count=2
    echo %count%  REM Still shows 1
)

REM With delayed expansion
set count=1
if %count%==1 (
    set count=2
    echo !count!  REM Shows 2
)
```

## Input and Output

### User Input

```batch
@echo off

REM Simple pause
pause

REM Prompt for input
set /p name="Enter your name: "
echo Hello %name%

REM Input with default
set /p age="Enter age (default 25): "
if "%age%"=="" set age=25

REM Menu selection
echo 1. Option 1
echo 2. Option 2
echo 3. Option 3
set /p choice="Select option (1-3): "
```

### Output Redirection

```batch
@echo off

REM Write to file
echo This is line 1 > output.txt
echo This is line 2 >> output.txt

REM Append to file
echo Additional line >> output.txt

REM Output to file and console
echo Starting process | tee output.log

REM Redirect errors
command 2> error.log
command 2>&1 output.log  REM Combine stdout and stderr

REM Suppress output
dir > nul 2>&1

REM Read file line by line
for /f "tokens=*" %%a in (input.txt) do (
    echo %%a
)
```

## Control Structures

### If Statements

```batch
@echo off

REM Simple if
if "%name%"=="John" (
    echo Hello John
)

REM If-else
if "%age%"=="25" (
    echo You are 25
) else (
    echo You are not 25
)

REM Numeric comparison
if %count% gtr 10 (
    echo Count is greater than 10
)

REM If not
if not "%status%"=="complete" (
    echo Process not complete
)

REM Comparison operators
REM EQU - equal
REM NEQ - not equal
REM LSS - less than
REM LEQ - less than or equal
REM GTR - greater than
REM GEQ - greater than or equal

REM Test if file exists
if exist "C:\file.txt" (
    echo File exists
)

REM Test if directory exists
if exist "C:\folder\" (
    echo Directory exists
)

REM Check if variable is defined
if defined myvar (
    echo Variable is set
)

REM Check error code
if %errorlevel%==0 (
    echo Command succeeded
) else (
    echo Command failed
)
```

### For Loops

```batch
@echo off

REM Loop through list
for %%i in (apple banana cherry) do (
    echo %%i
)

REM Loop through range
for /l %%i in (1,1,10) do (
    echo Number: %%i
)

REM Loop through directory
for %%f in (*.txt) do (
    echo Processing %%f
)

REM Loop through recursive directory
for /r "C:\files" %%f in (*.pdf) do (
    echo %%f
)

REM Loop through file lines
for /f %%a in (input.txt) do (
    echo %%a
)

REM Loop with parse
for /f "tokens=1,2" %%a in (data.txt) do (
    echo %%a - %%b
)
```

### Goto and Labels

```batch
@echo off

echo Starting process
goto step1

echo This is skipped

:step1
echo Step 1 complete
goto step2

:step2
echo Step 2 complete
goto end

:end
echo All done
exit /b 0
```

## Functions/Subroutines

### Basic Function Pattern

```batch
@echo off

call :myfunction arg1 arg2
echo Returned: %result%
exit /b 0

:myfunction
REM Function parameters
set param1=%1
set param2=%2

REM Function logic
set result=%param1%_%param2%

REM Return (implicit)
exit /b 0
```

### Function with Return Value

```batch
@echo off

call :add 5 3
echo Result: %sum%
exit /b

:add
setlocal
set /a result=%1+%2
endlocal & set sum=%result%
exit /b

REM Alternative with delayed expansion
@echo off
setlocal enabledelayedexpansion

call :multiply 4 5
echo Result: !product!
exit /b

:multiply
setlocal enabledelayedexpansion
set /a result=%1*%2
endlocal & set product=!result!
exit /b
```

## File Operations

### File Handling

```batch
@echo off

REM Create file
type nul > newfile.txt

REM Copy file
copy source.txt destination.txt

REM Move file
move source.txt C:\destination\

REM Delete file
del file.txt

REM Rename file
ren oldname.txt newname.txt

REM Create directory
mkdir C:\newdir

REM Remove directory
rmdir C:\emptydir

REM Remove directory with contents
rmdir /s /q C:\dir_with_files
```

## Text Processing

```batch
@echo off

REM Find text in file
findstr "error" logfile.txt

REM Find and count
findstr /c:"error" logfile.txt | find /c /v ""

REM Replace text (requires more complex scripting)
setlocal enabledelayedexpansion
for /f "delims=" %%a in (input.txt) do (
    set line=%%a
    set line=!line:oldtext=newtext!
    echo !line!
) > output.txt

REM Extract specific characters
set text=Hello World
echo %text:~0,5%  REM "Hello"
echo %text:~6,5%  REM "World"
```

## Practical Examples

### Batch File Template

```batch
@echo off
setlocal enabledelayedexpansion

REM Script: Process Files
REM Description: Process all txt files in directory
REM Usage: script.bat [source_directory]

if "%1"=="" (
    set source_dir=.
) else (
    set source_dir=%1
)

echo Processing files in: %source_dir%

for %%f in ("%source_dir%\*.txt") do (
    echo Processing: %%f
    REM Add your processing here
    findstr "important" "%%f" >> results.txt
)

echo Processing complete!
pause
```

### Backup Script

```batch
@echo off

REM Backup important files
set source=C:\Users\%username%\Documents
set backup=D:\Backups
set timestamp=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%

mkdir "%backup%\backup_%timestamp%"

xcopy "%source%\*.docx" "%backup%\backup_%timestamp%\" /i /y
xcopy "%source%\*.xlsx" "%backup%\backup_%timestamp%\" /i /y

echo Backup completed to: %backup%\backup_%timestamp%
```

### System Information Script

```batch
@echo off

echo System Information Report
echo ==========================
echo Date: %date%
echo Time: %time%
echo User: %username%
echo Computer: %computername%
echo ==========================

systeminfo > systeminfo.txt
echo System info saved to systeminfo.txt

pause
```

### Install Application Script

```batch
@echo off

set app_url=https://example.com/app.exe
set install_dir=C:\Program Files\MyApp

mkdir "%install_dir%"

echo Downloading application...
curl.exe -o "%install_dir%\app.exe" "%app_url%"

if errorlevel 1 (
    echo Download failed!
    exit /b 1
)

echo Running installer...
"%install_dir%\app.exe" /install /quiet

if errorlevel 0 (
    echo Installation successful!
) else (
    echo Installation failed!
)

pause
```

## Debugging

```batch
@echo off

REM Enable debug mode
setlocal enabledelayedexpansion

REM Echo variables
echo Debug: variable=%myvar%

REM Show command line
echo Debug: command line: %*

REM Pause at checkpoint
echo Debug: reached checkpoint 1
pause

REM Log to file
echo %date% %time% - Event occurred >> debug.log

REM Test command result
dir nonexistent.file 2>nul
if %errorlevel%==0 (
    echo File found
) else (
    echo File not found, errorlevel: %errorlevel%
)
```

## Best Practices

```batch
@echo off
setlocal enabledelayedexpansion

REM 1. Always use @echo off at top
REM 2. Use quotes around paths with spaces
REM 3. Check error levels after commands
REM 4. Use meaningful variable names
REM 5. Comment complex sections
REM 6. Use delayed expansion for variables in loops
REM 7. Test with echoing before running real commands
REM 8. Always cleanup temporary files

REM Example of good practices:
set "log_file=%temp%\script_%date:~-4%%date:~-10,2%%date:~-7,2%.log"
echo Starting process... >> "%log_file%"

REM Process
for %%f in (*.txt) do (
    echo Processing %%f >> "%log_file%"
    copy "%%f" "backup\%%f" 2>>"%log_file%"
)

echo Completed >> "%log_file%"
echo Log saved to: %log_file%
```

## Resources

- [Microsoft Batch File Documentation](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/)

- [Batch Programming Guide](https://www.tutorialspoint.com/batch_script/)

- [SS64 Batch Reference](https://ss64.com/nt/syntax.html)

---

_Last updated: 2025-03-30_

Source: https://1337skills.com/cheatsheets/batch/
