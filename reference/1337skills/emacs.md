# Emacs Cheatsheet intermediate

## Overview

GNU Emacs is an extensible, customizable, free/libre text editor - and more. At its core is an interpreter for Emacs Lisp, a dialect of the Lisp programming language with extensions to support text editing.

## Basic Concepts

### Key Notation

```plaintext
C-x     # Ctrl + x
M-x     # Alt + x (or Esc then x)
C-M-x   # Ctrl + Alt + x
S-x     # Shift + x
```

### Terminology

```plaintext
Buffer  # Text being edited (file content)
Window  # View of a buffer
Frame   # Emacs window (what other apps call window)
Point   # Cursor position
Mark    # Saved position for region selection
Region  # Text between point and mark
Kill    # Cut (delete and save to kill ring)
Yank    # Paste (from kill ring)
```

## Basic Navigation

### Movement Commands

```plaintext
C-f     # Forward character
C-b     # Backward character
C-n     # Next line
C-p     # Previous line
C-a     # Beginning of line
C-e     # End of line
M-f     # Forward word
M-b     # Backward word
M-a     # Beginning of sentence
M-e     # End of sentence
C-v     # Page down
M-v     # Page up
M-<     # Beginning of buffer
M->     # End of buffer
M-g g   # Go to line number
```

### Advanced Navigation

```plaintext
C-M-f   # Forward s-expression
C-M-b   # Backward s-expression
C-M-a   # Beginning of function
C-M-e   # End of function
C-M-v   # Scroll other window down
C-M-S-v # Scroll other window up
```

## File Operations

### File Management

```plaintext
C-x C-f # Find file (open)
C-x C-s # Save file
C-x C-w # Write file (save as)
C-x C-c # Exit Emacs
C-x C-v # Visit file (replace current buffer)
C-x i   # Insert file
C-x C-r # Read file (read-only)
```

### Buffer Management

```plaintext
C-x b   # Switch buffer
C-x C-b # List buffers
C-x k   # Kill buffer
C-x C-q # Toggle read-only mode
C-x C-z # Suspend Emacs
```

## Editing Commands

### Basic Editing

```plaintext
C-d     # Delete character forward
DEL     # Delete character backward
M-d     # Kill word forward
M-DEL   # Kill word backward
C-k     # Kill line (from point to end)
C-S-backspace # Kill entire line
C-w     # Kill region
M-w     # Copy region
C-y     # Yank (paste)
M-y     # Yank pop (cycle through kill ring)
C-/     # Undo
C-g     # Quit/cancel command
```

### Advanced Editing

```plaintext
C-t     # Transpose characters
M-t     # Transpose words
C-x C-t # Transpose lines
M-u     # Uppercase word
M-l     # Lowercase word
M-c     # Capitalize word
C-x C-u # Uppercase region
C-x C-l # Lowercase region
```

## Search and Replace

### Search

```plaintext
C-s     # Incremental search forward
C-r     # Incremental search backward
C-M-s   # Regex search forward
C-M-r   # Regex search backward
M-s w   # Word search
M-s .   # Symbol search
```

### Replace

```plaintext
M-%     # Query replace
C-M-%   # Query replace regex
M-x replace-string      # Replace all occurrences
M-x replace-regexp      # Replace all regex matches
```

### Search and Replace Keys (during query replace)

```plaintext
y       # Replace this occurrence
n       # Skip this occurrence
!       # Replace all remaining
q       # Quit
.       # Replace this and quit
^       # Go back to previous
```

## Windows and Frames

### Window Management

```plaintext
C-x 2   # Split window horizontally
C-x 3   # Split window vertically
C-x 1   # Delete other windows
C-x 0   # Delete current window
C-x o   # Switch to other window
C-x ^   # Enlarge window vertically
C-x \\\\}   # Enlarge window horizontally
C-x \\\\{   # Shrink window horizontally
```

### Frame Management

```plaintext
C-x 5 2 # Create new frame
C-x 5 0 # Delete current frame
C-x 5 1 # Delete other frames
C-x 5 o # Switch to other frame
C-x 5 f # Find file in new frame
```

## Regions and Marks

### Mark and Region

```plaintext
C-SPC   # Set mark
C-x C-x # Exchange point and mark
C-u C-SPC # Jump to previous mark
M-h     # Mark paragraph
C-x h   # Mark whole buffer
C-M-h   # Mark function
```

### Rectangle Operations

```plaintext
C-x r k # Kill rectangle
C-x r y # Yank rectangle
C-x r o # Open rectangle
C-x r c # Clear rectangle
C-x r t # String rectangle (replace with text)
```

## Help System

### Getting Help

```plaintext
C-h ?   # Help on help
C-h k   # Describe key
C-h f   # Describe function
C-h v   # Describe variable
C-h m   # Describe mode
C-h b   # Show key bindings
C-h a   # Apropos (search commands)
C-h i   # Info browser
C-h t   # Tutorial
```

### Info System

```plaintext
C-h i   # Enter Info
SPC     # Scroll forward
DEL     # Scroll backward
n       # Next node
p       # Previous node
u       # Up node
m       # Menu item
f       # Follow reference
l       # Last node
q       # Quit Info
```

## Modes

### Major Modes

```plaintext
M-x text-mode           # Text mode
M-x fundamental-mode    # Fundamental mode
M-x lisp-mode          # Lisp mode
M-x python-mode        # Python mode
M-x c-mode             # C mode
M-x html-mode          # HTML mode
M-x org-mode           # Org mode
```

### Minor Modes

```plaintext
M-x auto-fill-mode     # Auto-fill mode
M-x flyspell-mode      # Spell checking
M-x linum-mode         # Line numbers
M-x whitespace-mode    # Show whitespace
M-x hl-line-mode       # Highlight current line
```

## Customization

### Basic Configuration (.emacs or init.el)

```elisp
;; Basic settings
(setq inhibit-startup-message t)
(setq make-backup-files nil)
(setq auto-save-default nil)

;; UI improvements
(menu-bar-mode -1)
(tool-bar-mode -1)
(scroll-bar-mode -1)
(global-linum-mode 1)
(show-paren-mode 1)

;; Indentation
(setq-default indent-tabs-mode nil)
(setq-default tab-width 4)

;; Key bindings
(global-set-key (kbd "C-x g") 'goto-line)
(global-set-key (kbd "C-c c") 'comment-region)
(global-set-key (kbd "C-c u") 'uncomment-region)

;; Theme
(load-theme 'wombat t)
```

### Package Management

```elisp
;; Package repositories
(require 'package)
(add-to-list 'package-archives
             '("melpa" . "https://melpa.org/packages/") t)
(package-initialize)

;; Install packages
(unless (package-installed-p 'use-package)
  (package-refresh-contents)
  (package-install 'use-package))

;; Use-package examples
(use-package magit
  :ensure t
  :bind ("C-x g" . magit-status))

(use-package company
  :ensure t
  :config
  (global-company-mode))
```

## Org Mode

### Basic Org Mode

```plaintext
* Heading 1
** Heading 2
*** Heading 3

- List item
  - Sub item
1. Numbered list
2. Second item

*bold* /italic/ _underlined_ =code= ~verbatim~

[[link][description]]
[[file:path/to/file.txt]]
[[https://example.com]]
```

### Org Mode Commands

```plaintext
TAB     # Cycle visibility
S-TAB   # Global cycle visibility
C-c C-t # Toggle TODO state
C-c C-s # Schedule item
C-c C-d # Set deadline
C-c a   # Agenda
C-c c   # Capture
C-c C-e # Export
```

### TODO Keywords

```plaintext
#+TODO: TODO IN-PROGRESS|DONE CANCELLED

* TODO Learn Emacs
* IN-PROGRESS Write documentation
* DONE Install Emacs
* CANCELLED Old project
```

## Dired (Directory Editor)

### Dired Commands

```plaintext
C-x d   # Open Dired
RET     # Open file/directory
^       # Go to parent directory
g       # Refresh
m       # Mark file
u       # Unmark file
U       # Unmark all
d       # Mark for deletion
x       # Execute deletions
C       # Copy file
R       # Rename/move file
D       # Delete file
+       # Create directory
```

### Dired Marking

```plaintext
m       # Mark file
u       # Unmark file
t       # Toggle marks
* s     # Mark all
* %     # Mark by regex
* .     # Mark by extension
U       # Unmark all
```

## Programming Features

### Code Navigation

```plaintext
M-.     # Find definition
M-,     # Return from definition
C-M-f   # Forward s-expression
C-M-b   # Backward s-expression
C-M-u   # Up list
C-M-d   # Down list
```

### Code Editing

```plaintext
C-M-\   # Indent region
C-c C-c # Comment region
M-;     # Comment/uncomment line
C-x r t # Rectangle text (column editing)
```

### Compilation

```plaintext
M-x compile         # Compile
C-x `              # Next error
M-g n              # Next error
M-g p              # Previous error
```

## Advanced Features

### Macros

```plaintext
C-x (   # Start macro recording
C-x )   # End macro recording
C-x e   # Execute macro
C-u C-x ( # Start macro with prefix
M-x name-last-kbd-macro # Name macro
M-x insert-kbd-macro    # Insert macro into buffer
```

### Registers

```plaintext
C-x r s # Save region to register
C-x r i # Insert register contents
C-x r SPC # Save point to register
C-x r j # Jump to register
```

### Bookmarks

```plaintext
C-x r m # Set bookmark
C-x r b # Jump to bookmark
C-x r l # List bookmarks
```

### Version Control

```plaintext
C-x v v # Version control next action
C-x v = # Show diff
C-x v l # Show log
C-x v ~ # Show specific version
C-x v g # Annotate (blame)
```

## Shell and Terminal

### Shell Commands

```plaintext
M-!     # Shell command
M-|# Shell command on region
C-u M-! # Insert shell command output
M-x shell           # Start shell
M-x eshell          # Start Eshell
M-x term            # Start terminal
```

### Eshell Commands

```plaintext
cd      # Change directory
ls      # List files
pwd     # Print working directory
clear   # Clear screen
exit    # Exit Eshell
```

## Useful Packages

### Popular Packages

```elisp
;; Ivy/Counsel/Swiper - completion framework
(use-package ivy
  :ensure t
  :config (ivy-mode 1))

;; Magit - Git interface
(use-package magit
  :ensure t
  :bind ("C-x g" . magit-status))

;; Company - completion
(use-package company
  :ensure t
  :config (global-company-mode))

;; Projectile - project management
(use-package projectile
  :ensure t
  :config (projectile-mode))

;; Which-key - key binding help
(use-package which-key
  :ensure t
  :config (which-key-mode))
```

## Troubleshooting

### Common Issues

```plaintext
C-g     # Cancel current command
M-x recover-session    # Recover crashed session
M-x toggle-debug-on-error # Debug errors
M-x emacs-version      # Check version
```

### Performance

```elisp
;; Increase garbage collection threshold
(setq gc-cons-threshold 100000000)

;; Reduce startup time
(setq package-enable-at-startup nil)

;; Profile startup
(use-package esup
  :ensure t
  :commands esup)
```

## Tips and Tricks

### Productivity Tips

```plaintext
C-x z   # Repeat last command
C-u     # Universal argument (prefix)
M-x     # Execute command by name
C-h k   # Find out what a key does
C-h f   # Find out what a function does
```

### Useful Commands

```plaintext
M-x occur           # Show lines matching pattern
M-x grep            # Search files
M-x rgrep           # Recursive grep
M-x find-name-dired # Find files by name
M-x calendar        # Calendar
M-x calculator      # Calculator
```

## Resources

- **Official Manual**: [gnu.org/software/emacs/manual](https://www.gnu.org/software/emacs/manual/)

- **Emacs Wiki**: [emacswiki.org](https://www.emacswiki.org/)

- **Package Archive**: [melpa.org](https://melpa.org/)

- **Tutorial**: `C-h t` within Emacs

Source: https://1337skills.com/cheatsheets/emacs/
