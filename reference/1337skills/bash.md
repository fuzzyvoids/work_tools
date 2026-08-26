# Bash - Bourne Again Shell beginner

Bash (Bourne Again Shell) is a Unix shell and command language written by Brian Fox for the GNU Project as a free software replacement for the Bourne Shell. First released in 1989, Bash has become the default shell on most Linux distributions and is one of the most widely used shells in the Unix/Linux ecosystem. It combines the features of the original Bourne shell with additional functionality including command completion, command history, and improved scripting capabilities.

## Installation and Setup

### Checking Bash Installation

```bash
# Check if Bash is installed
which bash
/bin/bash

# Check Bash version
bash --version
GNU bash, version 5.1.16(1)-release (x86_64-pc-linux-gnu)

# Check current shell
echo $SHELL
/bin/bash

# Check available shells
cat /etc/shells
```

### Setting Bash as Default Shell

```bash
# Set Bash as default shell for current user
chsh -s /bin/bash

# Set Bash as default shell for specific user (as root)
sudo chsh -s /bin/bash username

# Verify shell change
echo $SHELL
```

### Bash Installation on Different Systems

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install bash

# CentOS/RHEL/Fedora
sudo dnf install bash

# macOS (using Homebrew for latest version)
brew install bash

# Arch Linux
sudo pacman -S bash

# FreeBSD
pkg install bash
```

## Basic Bash Syntax and Commands

### Command Structure

```bash
# Basic command structure
command [options] [arguments]

# Examples
ls -la /home
cp file1.txt file2.txt
grep -r "pattern" /path/to/search
```

### Variables and Environment

```bash
# Variable assignment (no spaces around =)
name="John Doe"
age=30
path="/home/user"

# Using variables
echo $name
echo $\\\\{name\\\\}
echo "Hello, $name"

# Environment variables
export PATH="/usr/local/bin:$PATH"
export EDITOR="vim"

# Special variables
echo $0    # Script name
echo $1    # First argument
echo $#    # Number of arguments
echo $@    # All arguments
echo $    # Process ID
echo $?    # Exit status of last command
```

### Command Substitution

```bash
# Using $() (preferred)
current_date=$(date)
file_count=$(ls|wc -l)
user_home=$(eval echo ~$USER)

# Using backticks (legacy)
current_date=`date`
file_count=`ls|wc -l`

# Nested command substitution
echo "Today is $(date +%A), $(date +%B) $(date +%d)"
```

### Quoting and Escaping

```bash
# Single quotes (literal)
echo 'The variable $HOME is not expanded'

# Double quotes (variable expansion)
echo "Your home directory is $HOME"

# Escaping special characters
echo "The price is \$10"
echo "Use \"quotes\" inside quotes"

# Here documents
cat << EOF
This is a multi-line
text block that can contain
variables like $HOME
EOF

# Here strings
grep "pattern" <<< "$variable"
```

## File Operations and Navigation

### Directory Navigation

```bash
# Change directory
cd /path/to/directory
cd ~                    # Home directory
cd -                    # Previous directory
cd ..                   # Parent directory
cd ../..                # Two levels up

# Print working directory
pwd

# Directory stack operations
pushd /path/to/dir      # Push directory onto stack
popd                    # Pop directory from stack
dirs                    # Show directory stack
```

### File and Directory Listing

```bash
# Basic listing
ls
ls -l                   # Long format
ls -la                  # Long format with hidden files
ls -lh                  # Human readable sizes
ls -lt                  # Sort by modification time
ls -lS                  # Sort by size
ls -lR                  # Recursive listing

# Advanced listing options
ls -la --color=auto     # Colored output
ls -la --time-style=full-iso  # ISO time format
ls -la --group-directories-first  # Directories first
```

### File Operations

```bash
# Create files
touch file.txt
touch file1.txt file2.txt file3.txt

# Copy files and directories
cp source.txt destination.txt
cp -r source_dir/ destination_dir/
cp -p file.txt backup.txt    # Preserve attributes
cp -u source.txt dest.txt    # Update only if newer

# Move and rename
mv old_name.txt new_name.txt
mv file.txt /path/to/destination/
mv *.txt /path/to/directory/

# Remove files and directories
rm file.txt
rm -f file.txt              # Force removal
rm -r directory/            # Recursive removal
rm -rf directory/           # Force recursive removal
rm -i *.txt                 # Interactive removal

# Create directories
mkdir directory_name
mkdir -p path/to/nested/directory
mkdir -m 755 directory_name  # With specific permissions
```

### File Permissions and Ownership

```bash
# Change permissions
chmod 755 file.txt
chmod u+x script.sh         # Add execute for user
chmod g-w file.txt          # Remove write for group
chmod o=r file.txt          # Set read-only for others
chmod -R 644 directory/     # Recursive permission change

# Change ownership
chown user:group file.txt
chown -R user:group directory/
chgrp group file.txt        # Change group only

# View permissions
ls -l file.txt
stat file.txt               # Detailed file information
```

## Text Processing and Manipulation

### File Content Operations

```bash
# View file contents
cat file.txt                # Display entire file
less file.txt               # Paginated view
more file.txt               # Simple paginated view
head file.txt               # First 10 lines
head -n 20 file.txt         # First 20 lines
tail file.txt               # Last 10 lines
tail -n 20 file.txt         # Last 20 lines
tail -f file.txt            # Follow file changes

# File comparison
diff file1.txt file2.txt
diff -u file1.txt file2.txt  # Unified format
cmp file1.txt file2.txt      # Binary comparison
```

### Text Search and Filtering

```bash
# grep - pattern searching
grep "pattern" file.txt
grep -i "pattern" file.txt   # Case insensitive
grep -r "pattern" directory/ # Recursive search
grep -n "pattern" file.txt   # Show line numbers
grep -v "pattern" file.txt   # Invert match
grep -E "pattern1|pattern2" file.txt  # Extended regex

# Advanced grep options
grep -A 3 "pattern" file.txt # Show 3 lines after match
grep -B 3 "pattern" file.txt # Show 3 lines before match
grep -C 3 "pattern" file.txt # Show 3 lines around match
grep -l "pattern" *.txt      # Show only filenames
grep -c "pattern" file.txt   # Count matches
```

### Text Processing Tools

```bash
# sed - stream editor
sed 's/old/new/' file.txt           # Replace first occurrence
sed 's/old/new/g' file.txt          # Replace all occurrences
sed '1,5s/old/new/g' file.txt       # Replace in lines 1-5
sed '/pattern/d' file.txt           # Delete lines matching pattern
sed -n '1,10p' file.txt             # Print lines 1-10

# awk - pattern scanning and processing
awk '\\\\{print $1\\\\}' file.txt           # Print first column
awk '\\\\{print $NF\\\\}' file.txt          # Print last column
awk '/pattern/ \\\\{print $0\\\\}' file.txt # Print lines matching pattern
awk -F: '\\\\{print $1\\\\}' /etc/passwd    # Use : as field separator
awk '\\\\{sum += $1\\\\} END \\\\{print sum\\\\}' file.txt  # Sum first column

# cut - extract columns
cut -d: -f1 /etc/passwd             # Extract first field
cut -c1-10 file.txt                 # Extract characters 1-10
cut -f2,4 file.txt                  # Extract fields 2 and 4

# sort and uniq
sort file.txt                       # Sort lines
sort -n file.txt                    # Numeric sort
sort -r file.txt                    # Reverse sort
sort -k2 file.txt                   # Sort by second field
uniq file.txt                       # Remove duplicate lines
sort file.txt|uniq -c             # Count occurrences
```

## Input/Output Redirection and Pipes

### Redirection Operators

```bash
# Output redirection
command > file.txt              # Redirect stdout to file (overwrite)
command >> file.txt             # Redirect stdout to file (append)
command 2> error.log            # Redirect stderr to file
command 2>> error.log           # Redirect stderr to file (append)
command &> output.log           # Redirect both stdout and stderr
command > output.log 2>&1       # Redirect both stdout and stderr

# Input redirection
command < input.txt             # Read input from file
command << EOF                  # Here document
line 1
line 2
EOF

# Advanced redirection
command 3> file.txt             # Redirect to file descriptor 3
exec 3> file.txt                # Open file descriptor 3
echo "text" >&3                 # Write to file descriptor 3
exec 3>&-                       # Close file descriptor 3
```

### Pipes and Command Chaining

```bash
# Basic pipes
ls -l|grep "txt"              # List files and filter for .txt
ps aux|grep "process_name"    # Show processes and filter
cat file.txt|sort|uniq      # Sort and remove duplicates

# Complex pipe chains
cat /var/log/access.log|grep "404"|awk '\\\\{print $1\\\\}'|sort|uniq -c|sort -nr
find . -name "*.log"|xargs grep "ERROR"|cut -d: -f1|sort|uniq

# Tee command (split output)
command|tee file.txt          # Write to file and stdout
command|tee -a file.txt       # Append to file and stdout
```

## Process Management

### Job Control

```bash
# Background and foreground jobs
command &                       # Run command in background
jobs                           # List active jobs
fg %1                          # Bring job 1 to foreground
bg %1                          # Send job 1 to background
kill %1                        # Kill job 1

# Process control signals
Ctrl+C                         # Interrupt (SIGINT)
Ctrl+Z                         # Suspend (SIGTSTP)
Ctrl+\                         # Quit (SIGQUIT)
```

### Process Information

```bash
# Process listing
ps                             # Show current processes
ps aux                         # Show all processes
ps -ef                         # Full format listing
pstree                         # Show process tree
top                            # Real-time process monitor
htop                           # Enhanced process monitor

# Process management
kill PID                       # Terminate process
kill -9 PID                    # Force kill process
killall process_name           # Kill all processes by name
pkill pattern                  # Kill processes matching pattern
nohup command &                # Run command immune to hangups
```

## Bash Scripting Fundamentals

### Script Structure

```bash
#!/bin/bash
# Script description and metadata
# Author: Your Name
# Date: YYYY-MM-DD
# Version: 1.0

# Script content starts here
echo "Hello, World!"
```

### Variables and Data Types

```bash
# String variables
name="John Doe"
message='Hello, World!'
multiline="This is a
multi-line string"

# Numeric variables
number=42
pi=3.14159

# Arrays
fruits=("apple" "banana" "orange")
numbers=(1 2 3 4 5)

# Associative arrays (Bash 4+)
declare -A colors
colors[red]="#FF0000"
colors[green]="#00FF00"
colors[blue]="#0000FF"

# Array operations
echo $\\\\{fruits[0]\\\\}               # First element
echo $\\\\{fruits[@]\\\\}               # All elements
echo $\\\\{#fruits[@]\\\\}              # Array length
fruits+=("grape")               # Append element
```

### Conditional Statements

```bash
# if-then-else
if [ condition ]; then
    echo "Condition is true"
elif [ other_condition ]; then
    echo "Other condition is true"
else
    echo "No condition is true"
fi

# Test conditions
if [ "$var" = "value" ]; then          # String equality
if [ "$num" -eq 10 ]; then             # Numeric equality
if [ "$num" -gt 5 ]; then              # Greater than
if [ "$num" -lt 20 ]; then             # Less than
if [ -f "file.txt" ]; then             # File exists
if [ -d "directory" ]; then            # Directory exists
if [ -r "file.txt" ]; then             # File is readable
if [ -w "file.txt" ]; then             # File is writable
if [ -x "script.sh" ]; then            # File is executable

# Logical operators
if [ condition1 ] && [ condition2 ]; then    # AND
if [ condition1 ]||[ condition2 ]; then    # OR
if [ ! condition ]; then                     # NOT

# Case statement
case $variable in
    pattern1)
        echo "Matched pattern1"
        ;;
    pattern2|pattern3)
        echo "Matched pattern2 or pattern3"
        ;;
    *)
        echo "No pattern matched"
        ;;
esac
```

### Loops

```bash
# for loop
for i in \\\\{1..10\\\\}; do
    echo "Number: $i"
done

for file in *.txt; do
    echo "Processing: $file"
done

for item in "$\\\\{array[@]\\\\}"; do
    echo "Item: $item"
done

# C-style for loop
for ((i=1; i<=10; i++)); do
    echo "Counter: $i"
done

# while loop
counter=1
while [ $counter -le 10 ]; do
    echo "Counter: $counter"
    ((counter++))
done

# until loop
counter=1
until [ $counter -gt 10 ]; do
    echo "Counter: $counter"
    ((counter++))
done

# Loop control
for i in \\\\{1..10\\\\}; do
    if [ $i -eq 5 ]; then
        continue    # Skip iteration
    fi
    if [ $i -eq 8 ]; then
        break      # Exit loop
    fi
    echo $i
done
```

### Functions

```bash
# Function definition
function greet() \\\\{
    echo "Hello, $1!"
\\\\}

# Alternative syntax
greet() \\\\{
    echo "Hello, $1!"
\\\\}

# Function with return value
calculate_sum() \\\\{
    local num1=$1
    local num2=$2
    local sum=$((num1 + num2))
    echo $sum
\\\\}

# Function with local variables
process_file() \\\\{
    local filename=$1
    local line_count=$(wc -l < "$filename")
    echo "File $filename has $line_count lines"
\\\\}

# Function usage
greet "World"
result=$(calculate_sum 5 3)
echo "Sum: $result"
```

## Advanced Bash Features

### Parameter Expansion

```bash
# Basic parameter expansion
echo $\\\\{variable\\\\}
echo $\\\\{variable:-default\\\\}       # Use default if unset
echo $\\\\{variable:=default\\\\}       # Set default if unset
echo $\\\\{variable:+alternate\\\\}     # Use alternate if set
echo $\\\\{variable:?error\\\\}         # Error if unset

# String manipulation
string="Hello, World!"
echo $\\\\{string#Hello\\\\}            # Remove shortest match from beginning
echo $\\\\{string##*/\\\\}              # Remove longest match from beginning
echo $\\\\{string%World!\\\\}           # Remove shortest match from end
echo $\\\\{string%%/*\\\\}              # Remove longest match from end
echo $\\\\{string/Hello/Hi\\\\}         # Replace first occurrence
echo $\\\\{string//l/L\\\\}             # Replace all occurrences

# Substring extraction
echo $\\\\{string:0:5\\\\}              # Extract substring (position:length)
echo $\\\\{string:7\\\\}                # Extract from position to end
echo $\\\\{#string\\\\}                 # String length
```

### Arithmetic Operations

```bash
# Arithmetic expansion
result=$((5 + 3))
result=$((10 * 2))
result=$((20 / 4))
result=$((17 % 5))              # Modulo

# Increment/decrement
((counter++))
((counter--))
((counter += 5))
((counter -= 3))

# Arithmetic with variables
num1=10
num2=5
sum=$((num1 + num2))
product=$((num1 * num2))

# Floating point arithmetic (using bc)
result=$(echo "scale=2; 10/3"|bc)
result=$(echo "scale=4; sqrt(16)"|bc -l)
```

### Error Handling

```bash
# Exit on error
set -e                          # Exit on any error
set -u                          # Exit on undefined variable
set -o pipefail                 # Exit on pipe failure

# Error handling in scripts
command||\\\\{
    echo "Command failed"
    exit 1
\\\\}

# Trap signals
trap 'echo "Script interrupted"; exit 1' INT TERM
trap 'cleanup_function' EXIT

# Function error handling
safe_command() \\\\{
    if ! command_that_might_fail; then
        echo "Error: Command failed" >&2
        return 1
    fi
\\\\}
```

## Configuration and Customization

### Bash Configuration Files

```bash
# System-wide configuration
/etc/bash.bashrc                # System-wide bashrc
/etc/profile                    # System-wide profile

# User-specific configuration
~/.bashrc                       # User's bashrc
~/.bash_profile                 # User's profile
~/.bash_login                   # Login shell configuration
~/.profile                      # POSIX shell profile
~/.bash_logout                  # Logout script
```

### Customizing .bashrc

```bash
# ~/.bashrc example configuration

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# User specific environment
export EDITOR="vim"
export BROWSER="firefox"
export PAGER="less"

# Custom PATH
export PATH="$HOME/bin:$HOME/.local/bin:$PATH"

# Aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Custom functions
mkcd() \\\\{
    mkdir -p "$1" && cd "$1"
\\\\}

extract() \\\\{
    if [ -f $1 ] ; then
        case $1 in
            *.tar.bz2)   tar xjf $1     ;;
            *.tar.gz)    tar xzf $1     ;;
            *.bz2)       bunzip2 $1     ;;
            *.rar)       unrar e $1     ;;
            *.gz)        gunzip $1      ;;
            *.tar)       tar xf $1      ;;
            *.tbz2)      tar xjf $1     ;;
            *.tgz)       tar xzf $1     ;;
            *.zip)       unzip $1       ;;
            *.Z)         uncompress $1  ;;
            *.7z)        7z x $1        ;;
            *)     echo "'$1' cannot be extracted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
\\\\}

# Prompt customization
PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

# History configuration
HISTSIZE=10000
HISTFILESIZE=20000
HISTCONTROL=ignoredups:ignorespace
shopt -s histappend

# Shell options
shopt -s checkwinsize
shopt -s globstar
shopt -s cdspell
```

### Bash Options and Settings

```bash
# Set options
set -o vi                       # Vi editing mode
set -o emacs                    # Emacs editing mode (default)
set -o noclobber                # Prevent file overwriting
set +o noclobber                # Allow file overwriting

# Shopt options
shopt -s autocd                 # Auto cd to directory
shopt -s cdspell                # Correct minor spelling errors
shopt -s checkwinsize           # Update LINES and COLUMNS
shopt -s cmdhist                # Save multi-line commands
shopt -s dotglob                # Include hidden files in globbing
shopt -s expand_aliases         # Expand aliases
shopt -s extglob                # Extended globbing
shopt -s globstar               # ** recursive globbing
shopt -s histappend             # Append to history file
shopt -s nocaseglob             # Case-insensitive globbing
```

## Command Line Editing and History

### Command Line Editing

```bash
# Emacs mode (default)
Ctrl+A                          # Beginning of line
Ctrl+E                          # End of line
Ctrl+B                          # Back one character
Ctrl+F                          # Forward one character
Alt+B                           # Back one word
Alt+F                           # Forward one word
Ctrl+D                          # Delete character
Ctrl+H                          # Backspace
Ctrl+K                          # Kill to end of line
Ctrl+U                          # Kill to beginning of line
Ctrl+W                          # Kill previous word
Alt+D                           # Kill next word
Ctrl+Y                          # Yank (paste)
Ctrl+T                          # Transpose characters
Alt+T                           # Transpose words

# Vi mode
set -o vi
Esc                             # Enter command mode
i                               # Insert mode
a                               # Append mode
A                               # Append at end of line
I                               # Insert at beginning of line
```

### History Management

```bash
# History commands
history                         # Show command history
history 10                      # Show last 10 commands
history -c                      # Clear history
history -d 5                    # Delete history entry 5

# History expansion
!!                              # Previous command
!n                              # Command number n
!string                         # Last command starting with string
!?string                        # Last command containing string
^old^new                        # Replace old with new in previous command

# History search
Ctrl+R                          # Reverse search
Ctrl+S                          # Forward search
Ctrl+G                          # Cancel search

# History configuration
export HISTSIZE=10000           # Commands in memory
export HISTFILESIZE=20000       # Commands in file
export HISTCONTROL=ignoredups   # Ignore duplicates
export HISTIGNORE="ls:ll:cd:pwd:bg:fg:history"  # Ignore commands
export HISTTIMEFORMAT="%F %T "  # Add timestamps
```

## Debugging and Troubleshooting

### Debugging Scripts

```bash
# Debug modes
bash -x script.sh               # Execute with trace
bash -n script.sh               # Check syntax without execution
bash -v script.sh               # Verbose mode

# Debug options in script
set -x                          # Enable trace
set +x                          # Disable trace
set -v                          # Enable verbose
set +v                          # Disable verbose

# Conditional debugging
if [ "$DEBUG" = "1" ]; then
    set -x
fi

# Debug function
debug() \\\\{
    if [ "$DEBUG" = "1" ]; then
        echo "DEBUG: $*" >&2
    fi
\\\\}
```

### Error Checking

```bash
# Check command success
if command; then
    echo "Command succeeded"
else
    echo "Command failed"
fi

# Check exit status
command
if [ $? -eq 0 ]; then
    echo "Success"
else
    echo "Failed with exit code $?"
fi

# Validate input
if [ $# -ne 2 ]; then
    echo "Usage: $0 <arg1> <arg2>"
    exit 1
fi

# Check file existence
if [ ! -f "$filename" ]; then
    echo "Error: File $filename does not exist"
    exit 1
fi
```

### Performance Monitoring

```bash
# Time command execution
time command
time \\\\{ command1; command2; \\\\}

# Profile script execution
PS4='+ $(date "+%s.%N"): '
set -x
# Your commands here
set +x

# Memory usage
/usr/bin/time -v command

# Disk usage
du -sh directory/
df -h
```

## Best Practices and Security

### Script Security

```bash
# Use full paths for commands
/bin/ls instead of ls
/usr/bin/find instead of find

# Validate input
case "$input" in
    [a-zA-Z0-9]*)
        # Valid input
        ;;
    *)
        echo "Invalid input"
        exit 1
        ;;
esac

# Quote variables
rm "$filename"                  # Correct
rm $filename                    # Dangerous

# Use arrays for file lists
files=( *.txt )
for file in "$\\\\{files[@]\\\\}"; do
    process "$file"
done
```

### Performance Best Practices

```bash
# Use built-in commands when possible
[[ condition ]]                 # Instead of [ condition ]
(( arithmetic ))                # Instead of [ arithmetic ]

# Avoid unnecessary subshells
var=$(cat file)                 # Subshell
var=$(<file)                    # Built-in

# Use parameter expansion
$\\\\{var#pattern\\\\}                  # Instead of sed/awk for simple operations
$\\\\{var%pattern\\\\}
$\\\\{var/pattern/replacement\\\\}

# Efficient loops
while IFS= read -r line; do     # Read file line by line
    process "$line"
done < file.txt
```

### Code Organization

```bash
# Use functions for repeated code
log_message() \\\\{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
\\\\}

# Separate configuration
CONFIG_FILE="$\\\\{HOME\\\\}/.myapp.conf"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Use meaningful variable names
user_count=10                   # Good
uc=10                          # Poor

# Comment complex logic
# Calculate the number of days between two dates
start_date=$(date -d "$1" +%s)
end_date=$(date -d "$2" +%s)
days=$(( (end_date - start_date) / 86400 ))
```

Bash remains the most widely used shell in Unix and Linux environments, providing a powerful combination of interactive command-line interface and scripting language. Its extensive feature set, POSIX compliance, and widespread availability make it an essential tool for system administrators, developers, and power users. Whether used for simple command execution or complex automation scripts, Bash offers the flexibility and reliability needed for professional computing environments.

Source: https://1337skills.com/cheatsheets/bash/
