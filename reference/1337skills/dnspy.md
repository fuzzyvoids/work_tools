# dnSpy intermediate

dnSpy is an open-source .NET debugger and assembly editor. It can decompile .NET assemblies to C# or Visual Basic, debug .NET applications without source code, edit IL and metadata, and save modified assemblies. Note: dnSpy is Windows-only and targets .NET Framework and .NET Core assemblies.

## Installation

```bash
# Download from GitHub releases (Windows only)
# https://github.com/dnSpy/dnSpy/releases
# Extract and run dnSpy.exe (no installation required)

# Alternative: dnSpyEx (actively maintained fork)
# https://github.com/dnSpyEx/dnSpy/releases

# For .NET 6+ assemblies, use dnSpyEx which has updated support
```

## Opening Assemblies

```text
# Open via File menu
File > Open (Ctrl+O)
# Select .exe, .dll, or .nupkg files

# Open from command line
dnSpy.exe C:\path\to\assembly.dll

# Open multiple assemblies
dnSpy.exe assembly1.dll assembly2.dll

# Drag and drop files onto the dnSpy window

# Open from GAC (Global Assembly Cache)
File > Open from GAC (Ctrl+Shift+O)
```

## Decompilation

### C# Decompilation

```text
# Navigate the assembly tree in the left panel
Assembly > Namespace > Class > Method

# View decompiled C# code (default)
Right-click > Decompile to C#

# Example decompiled output:
# public class Program
# {
#     public static void Main(string[] args)
#     {
#         Console.WriteLine("Hello, World!");
#     }
# }

# Change decompiler version
View > Options > Decompiler > C# version
```

### IL View

```text
# Switch to IL (Intermediate Language) view
Right-click on method > Show IL Code

# Or toggle via menu
View > Show IL Code

# IL view shows raw opcodes:
# .method public hidebysig static void Main(string[] args)
# {
#     .maxstack 8
#     IL_0000: ldstr "Hello, World!"
#     IL_0005: call void [mscorlib]System.Console::WriteLine(string)
#     IL_000a: ret
# }
```

## Debugging

### Start Debugging

```text
# Debug a .NET executable
Debug > Start Debugging (F5)
# Select the executable to debug

# Attach to running process
Debug > Attach to Process (Ctrl+Alt+P)
# Select the .NET process from the list

# Debug a .NET Core application
Debug > Start Debugging > Select .NET Core
# Browse to the .dll or .exe
```

### Breakpoints

```text
# Set breakpoint on a line
Click the margin (left of line numbers)
# Or press F9 on the current line

# Conditional breakpoint
Right-click breakpoint > Edit Breakpoint
# Enter condition: args.Length > 0

# View all breakpoints
Debug > Windows > Breakpoints (Ctrl+Alt+B)

# Break on exceptions
Debug > Windows > Exception Settings
# Check specific exception types
```

### Stepping Through Code

```text
F5          Continue execution
F10         Step Over (execute current line)
F11         Step Into (enter method calls)
Shift+F11   Step Out (exit current method)
F9          Toggle breakpoint
Ctrl+F5     Start without debugging

# View variables during debugging
Debug > Windows > Locals (Alt+4)
Debug > Windows > Watch (Alt+2)
Debug > Windows > Call Stack (Alt+7)
```

## Editing Assemblies

### Edit Method Body (C#)

```text
# Edit C# code directly
Right-click on method > Edit Method Body (C#)
# Modify the C# code in the editor
# Click Compile to apply changes

# Example: modify a check
# Original:  if (isLicensed) { ... }
# Modified:  if (true) { ... }
```

### Edit IL Instructions

```text
# Edit raw IL code
Right-click on method > Edit IL Instructions
# Modify opcodes directly in the IL editor

# Common IL modifications:
# Change branch: brfalse -> brtrue (invert condition)
# Remove check: replace with nop
# Change constant: ldc.i4.0 -> ldc.i4.1
```

### Edit Class

```text
# Edit class properties and fields
Right-click on class > Edit Class (C#)
# Add, remove, or modify members

# Edit metadata
Right-click on member > Edit Metadata
# Change visibility, name, attributes
```

### Save Modified Assembly

```text
# Save changes to disk
File > Save Module (Ctrl+Shift+S)

# Save with options
File > Save Module
# Choose: save to same file, new file, or directory
# Options: preserve tokens, keep old maxstack
```

## Search and Analysis

### Global Search

```text
# Search across all loaded assemblies
Edit > Search Assemblies (Ctrl+Shift+K)

# Search types:
# - Type (class, struct, enum)
# - Method
# - Field
# - Property
# - Event
# - String literal
# - Number literal
```

### Analyzer

```text
# Analyze usage of a type or member
Right-click > Analyze (Ctrl+R)

# Shows:
# - Used By: what references this member
# - Uses: what this member references
# - Instantiated By: where type is created
# - Exposed By: public API surface
# - Extended By: derived types
```

## Hex Editor

```text
# View raw bytes
Right-click > Show in Hex Editor

# Edit bytes directly
# Click on a byte value and type new value

# Go to specific offset
Ctrl+G in hex editor > Enter offset

# Find byte pattern
Ctrl+F > Enter hex bytes: 48 65 6C 6C 6F
```

## Metadata Tables

```text
# View PE metadata
View > Metadata > Tables

# Important tables:
# TypeDef     - All types defined in the assembly
# MethodDef   - All methods
# Field       - All fields
# MemberRef   - External references
# AssemblyRef - Referenced assemblies
# CustomAttribute - Attributes and decorations

# View metadata headers
View > Metadata > Headers
# Shows PE headers, CLR headers, streams
```

## Useful Keyboard Shortcuts

```text
Ctrl+O          Open assembly
Ctrl+Shift+O    Open from GAC
Ctrl+G          Go to token/address
Ctrl+T          Go to type
Ctrl+Shift+K    Search assemblies
Ctrl+R          Analyze member
F5              Start/continue debugging
F9              Toggle breakpoint
F10             Step over
F11             Step into
Ctrl+Shift+S    Save module
Ctrl+Z          Undo edit
Ctrl+C          Copy selected text
Ctrl+F          Find in current document
F12             Go to definition
```

## Tips

```text
# Decompile entire project to disk
File > Export to Project (Ctrl+Shift+E)
# Creates a Visual Studio solution with all decompiled source

# Load debug symbols
File > Open > Select .pdb file alongside assembly

# Handle obfuscated assemblies
# 1. Look for string decryption methods in Analyze view
# 2. Set breakpoints after decryption to read plaintext
# 3. Use Edit IL to bypass integrity checks

# Compare assemblies
# Open both assemblies side by side in separate tabs
# Use Analyze to track differences in method calls
```

Source: https://1337skills.com/cheatsheets/dnspy/
