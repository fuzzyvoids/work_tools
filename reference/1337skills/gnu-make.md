# GNU Make Cheatsheet

## Installation

| Platform | Command |
| --- | --- |
| Ubuntu/Debian | `sudo apt-get install build-essential` or `sudo apt-get install make` |
| RHEL/CentOS/Fedora | `sudo yum groupinstall "Development Tools"` or `sudo dnf install make` |
| Arch Linux | `sudo pacman -S base-devel` or `sudo pacman -S make` |
| Alpine Linux | `apk add make` |
| macOS (Xcode) | `xcode-select --install` |
| macOS (Homebrew) | `brew install make` (installs as `gmake`) |
| Windows (Chocolatey) | `choco install make` |
| Windows (WSL) | `sudo apt-get install build-essential` |
| Verification | `make --version` |

## Basic Commands

| Command | Description |
| --- | --- |
| `make` | Build the first target in Makefile (usually 'all') |
| `make target_name` | Build a specific target (e.g., `make clean`, `make install`) |
| `make clean` | Remove generated files (must be defined in Makefile) |
| `make -n` | Dry run - show commands without executing them |
| `make -f custom.mk` | Use a specific makefile instead of default |
| `make -C /path/to/dir` | Change to directory before executing |
| `make CC=clang` | Set/override a variable from command line |
| `make CFLAGS="-O2 -Wall"` | Override compilation flags |
| `make -j4` | Run 4 jobs in parallel for faster builds |
| `make -j` | Use all available CPU cores for parallel builds |
| `make -s` | Silent mode - don't print commands being executed |
| `make -i` | Ignore errors and continue building |
| `make -k` | Keep going after errors, skip failed targets |
| `make -B` | Unconditionally rebuild all targets |
| `make -t` | Touch files to update timestamps without rebuilding |
| `make -q target` | Check if target needs rebuilding (exit code 0=no, 1=yes) |

## Advanced Commands

| Command | Description |
| --- | --- |
| `make -d` | Show detailed debug information during execution |
| `make --debug=basic` | Show basic debug information (less verbose) |
| `make -p` | Print all rules and variable values |
| `make -p -f /dev/null` | Show all built-in rules and variables |
| `make --warn-undefined-variables` | Warn when undefined variables are referenced |
| `make -j8 --load-average=4` | Parallel builds with system load limiting |
| `make -O` | Synchronize output for parallel builds |
| `make --output-sync=target` | Group output by target in parallel builds |
| `make --trace` | Show why each target is being remade |
| `make -e` | Environment variables override Makefile variables |
| `make -r` | Disable built-in implicit rules |
| `make -R` | Disable built-in variables |
| `make -L` | Check symlink times instead of target times |
| `make DEBUG=1 VERBOSE=1` | Set multiple variables from command line |
| `make -w` | Print working directory before and after execution |

## Makefile Syntax

### Basic Structure

```makefile
# Variable definitions
CC = gcc
CFLAGS = -Wall -O2
SOURCES = main.c utils.c
OBJECTS = $(SOURCES:.c=.o)

# Target: prerequisites
target: prerequisite1 prerequisite2
	command1    # Must use TAB, not spaces
	command2

# Phony targets (not actual files)
.PHONY: all clean install

all: program

program: $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) program
```

### Automatic Variables

| Variable | Description |
| --- | --- |
| `$@` | Target name |
| `$<` | First prerequisite |
| `$^` | All prerequisites (space-separated) |
| `$?` | Prerequisites newer than target |
| `$*` | Stem of pattern match |
| `$(@D)` | Directory part of target |
| `$(@F)` | File part of target |
| `$(<D)` | Directory part of first prerequisite |
| `$(<F)` | File part of first prerequisite |

### Built-in Functions

```makefile
# Wildcard expansion
SOURCES = $(wildcard src/*.c)

# Pattern substitution
OBJECTS = $(patsubst %.c,%.o,$(SOURCES))
OBJECTS = $(SOURCES:.c=.o)  # Shorthand

# Directory/file operations
DIRS = $(dir $(SOURCES))
FILES = $(notdir $(SOURCES))
BASENAME = $(basename $(SOURCES))

# Shell execution
GIT_VERSION = $(shell git describe --tags)
FILE_COUNT = $(shell ls -1 *.c | wc -l)

# Conditional
BUILD_TYPE = $(if $(DEBUG),debug,release)

# Foreach loop
DIRS = src lib bin
ALL_SOURCES = $(foreach dir,$(DIRS),$(wildcard $(dir)/*.c))

# Filter operations
C_FILES = $(filter %.c,$(SOURCES))
NOT_TEST = $(filter-out %_test.c,$(SOURCES))

# String operations
UPPERCASE = $(shell echo $(PROJECT) | tr a-z A-Z)
JOINED = $(subst $(space),$(comma),$(LIST))
```

### Conditional Directives

```makefile
# ifdef/ifndef
ifdef DEBUG
CFLAGS += -g -DDEBUG
else
CFLAGS += -O2
endif

# ifeq/ifneq
ifeq ($(CC),gcc)
CFLAGS += -fno-strict-aliasing
endif

ifneq ($(PLATFORM),windows)
LDFLAGS += -lpthread
endif

# Comparing strings
ifeq ($(strip $(VERBOSE)),1)
Q =
else
Q = @
endif
```

### Pattern Rules

```makefile
# Basic pattern rule
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Multiple patterns
%: %.c
	$(CC) $(CFLAGS) $< -o $@

# Static pattern rules
OBJECTS = foo.o bar.o baz.o
$(OBJECTS): %.o: %.c
	$(CC) -c $(CFLAGS) $< -o $@

# With different directories
$(BUILDDIR)/%.o: $(SRCDIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@
```

## Configuration

### Standard Makefile Variables

```makefile
# Compilers
CC = gcc                    # C compiler
CXX = g++                   # C++ compiler
AS = as                     # Assembler
AR = ar                     # Archive tool
LD = ld                     # Linker

# Compiler flags
CFLAGS = -Wall -O2         # C compilation flags
CXXFLAGS = -Wall -O2       # C++ compilation flags
CPPFLAGS = -I./include     # Preprocessor flags
LDFLAGS = -L./lib          # Linker flags
LDLIBS = -lm -lpthread     # Libraries to link

# Installation directories
PREFIX = /usr/local
BINDIR = $(PREFIX)/bin
LIBDIR = $(PREFIX)/lib
INCLUDEDIR = $(PREFIX)/include

# Project structure
SRCDIR = src
BUILDDIR = build
OBJDIR = $(BUILDDIR)/obj
BINDIR_LOCAL = bin
```

### Multi-file Project Configuration

```makefile
# Project metadata
PROJECT = myapp
VERSION = 1.0.0
DESCRIPTION = My Application

# Source discovery
SOURCES = $(wildcard $(SRCDIR)/*.c)
HEADERS = $(wildcard $(SRCDIR)/*.h)
OBJECTS = $(patsubst $(SRCDIR)/%.c,$(OBJDIR)/%.o,$(SOURCES))

# Dependencies
DEPS = $(OBJECTS:.o=.d)

# Include dependency files
-include $(DEPS)

# Automatic dependency generation
$(OBJDIR)/%.o: $(SRCDIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(CPPFLAGS) -MMD -MP -c $< -o $@

# Target-specific variables
debug: CFLAGS += -g -DDEBUG -O0
debug: $(PROJECT)

release: CFLAGS += -O3 -DNDEBUG
release: $(PROJECT)
```

### Including External Configuration

```makefile
# Main Makefile
-include config.mk          # Optional local config
-include $(HOME)/.makerc    # User-specific settings
include rules.mk            # Required shared rules

# Export variables to sub-makes
export CC CXX CFLAGS LDFLAGS
```

### config.mk Example

```makefile
# Local machine-specific configuration
# This file is not committed to version control

# Override compiler
CC = clang
CXX = clang++

# Add sanitizers for development
CFLAGS += -fsanitize=address -fsanitize=undefined
LDFLAGS += -fsanitize=address -fsanitize=undefined

# Custom installation prefix
PREFIX = /opt/myapp

# Enable verbose output
VERBOSE = 1
```

## Common Use Cases

### Use Case 1: C/C++ Project Build System

```makefile
# Makefile for C project with separate source/build directories
PROJECT = myprogram
CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2
LDFLAGS = -lm

SRCDIR = src
BUILDDIR = build
BINDIR = bin

SOURCES = $(wildcard $(SRCDIR)/*.c)
OBJECTS = $(patsubst $(SRCDIR)/%.c,$(BUILDDIR)/%.o,$(SOURCES))
DEPS = $(OBJECTS:.o=.d)

.PHONY: all clean install

all: $(BINDIR)/$(PROJECT)

$(BINDIR)/$(PROJECT): $(OBJECTS)
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)
	@echo "Build complete: $@"

$(BUILDDIR)/%.o: $(SRCDIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -MMD -MP -c $< -o $@

clean:
	rm -rf $(BUILDDIR) $(BINDIR)

install: $(BINDIR)/$(PROJECT)
	install -m 0755 $< /usr/local/bin/

-include $(DEPS)
```

```bash
# Build commands
make                    # Build project
make clean             # Remove build artifacts
make install           # Install to system
make -j4               # Parallel build with 4 jobs
```

### Use Case 2: Multi-Target Build with Debug/Release

```makefile
PROJECT = myapp
SRCDIR = src
BUILDDIR_DEBUG = build/debug
BUILDDIR_RELEASE = build/release

SOURCES = $(wildcard $(SRCDIR)/*.c)
OBJECTS_DEBUG = $(patsubst $(SRCDIR)/%.c,$(BUILDDIR_DEBUG)/%.o,$(SOURCES))
OBJECTS_RELEASE = $(patsubst $(SRCDIR)/%.c,$(BUILDDIR_RELEASE)/%.o,$(SOURCES))

CC = gcc
CFLAGS_COMMON = -Wall -Wextra -std=c11
CFLAGS_DEBUG = $(CFLAGS_COMMON) -g -O0 -DDEBUG
CFLAGS_RELEASE = $(CFLAGS_COMMON) -O3 -DNDEBUG

.PHONY: all debug release clean

all: debug release

debug: $(BUILDDIR_DEBUG)/$(PROJECT)

release: $(BUILDDIR_RELEASE)/$(PROJECT)

$(BUILDDIR_DEBUG)/$(PROJECT): $(OBJECTS_DEBUG)
	@mkdir -p $(dir $@)
	$(CC) $^ -o $@

$(BUILDDIR_RELEASE)/$(PROJECT): $(OBJECTS_RELEASE)
	@mkdir -p $(dir $@)
	$(CC) $^ -o $@

$(BUILDDIR_DEBUG)/%.o: $(SRCDIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS_DEBUG) -c $< -o $@

$(BUILDDIR_RELEASE)/%.o: $(SRCDIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS_RELEASE) -c $< -o $@

clean:
	rm -rf build
```

```bash
# Usage
make debug             # Build debug version
make release           # Build release version
make all               # Build both versions
```

### Use Case 3: Testing and Code Quality

```makefile
PROJECT = myapp
TEST_DIR = tests
TEST_SOURCES = $(wildcard $(TEST_DIR)/*_test.c)
TEST_BINS = $(patsubst $(TEST_DIR)/%.c,$(TEST_DIR)/bin/%,$(TEST_SOURCES))

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -I./src
LDFLAGS = -lcheck -lm

.PHONY: all test coverage lint clean

all: $(PROJECT)

test: $(TEST_BINS)
	@echo "Running tests..."
	@for test in $(TEST_BINS); do \
		echo "Running $$test..."; \
		$$test || exit 1; \
	done
	@echo "All tests passed!"

$(TEST_DIR)/bin/%: $(TEST_DIR)/%.c src/*.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

coverage: CFLAGS += --coverage
coverage: LDFLAGS += --coverage
coverage: clean test
	gcov src/*.c
	lcov --capture --directory . --output-file coverage.info
	genhtml coverage.info --output-directory coverage_html

lint:
	cppcheck --enable=all --suppress=missingIncludeSystem src/
	clang-tidy src/*.c -- $(CFLAGS)

clean:
	rm -rf $(TEST_DIR)/bin *.gcda *.gcno *.gcov coverage.info coverage_html
```

```bash
# Usage
make test              # Run all tests
make coverage          # Generate coverage report
make lint              # Run static analysis
```

### Use Case 4: Documentation Generation

```makefile
PROJECT = myapp
DOC_DIR = docs
BUILD_DOC_DIR = $(DOC_DIR)/build

SOURCES = $(wildcard src/*.c src/*.h)
MD_FILES = $(wildcard $(DOC_DIR)/*.md)

.PHONY: docs docs-html docs-pdf clean-docs

docs: docs-html docs-pdf

docs-html: $(BUILD_DOC_DIR)/html/index.html

docs-pdf: $(BUILD_DOC_DIR)/$(PROJECT).pdf

# Generate HTML documentation with Doxygen
$(BUILD_DOC_DIR)/html/index.html: $(SOURCES) Doxyfile
	@mkdir -p $(BUILD_DOC_DIR)
	doxygen Doxyfile

# Generate PDF from Markdown
$(BUILD_DOC_DIR)/$(PROJECT).pdf: $(MD_FILES)
	@mkdir -p $(BUILD_DOC_DIR)
	pandoc $(MD_FILES) -o $@ \
		--toc \
		--number-sections \
		-V geometry:margin=1in

# Generate man pages
$(BUILD_DOC_DIR)/man/$(PROJECT).1: $(DOC_DIR)/$(PROJECT).1.md
	@mkdir -p $(dir $@)
	pandoc $< -s -t man -o $@

clean-docs:
	rm -rf $(BUILD_DOC_DIR)
```

```bash
# Usage
make docs              # Generate all documentation
make docs-html         # Generate HTML docs only
make docs-pdf          # Generate PDF docs only
```

### Use Case 5: Asset Processing Pipeline

```makefile
SRC_IMG_DIR = assets/images
DIST_IMG_DIR = dist/images
SRC_CSS_DIR = assets/css
DIST_CSS_DIR = dist/css
SRC_JS_DIR = assets/js
DIST_JS_DIR = dist/js

PNG_SOURCES = $(wildcard $(SRC_IMG_DIR)/*.png)
PNG_OPTIMIZED = $(patsubst $(SRC_IMG_DIR)/%.png,$(DIST_IMG_DIR)/%.png,$(PNG_SOURCES))

SCSS_SOURCES = $(wildcard $(SRC_CSS_DIR)/*.scss)
CSS_FILES = $(patsubst $(SRC_CSS_DIR)/%.scss,$(DIST_CSS_DIR)/%.css,$(SCSS_SOURCES))

JS_SOURCES = $(wildcard $(SRC_JS_DIR)/*.js)
JS_MINIFIED = $(patsubst $(SRC_JS_DIR)/%.js,$(DIST_JS_DIR)/%.min.js,$(JS_SOURCES))

.PHONY: all assets images css js clean

all: assets

assets: images css js

images: $(PNG_OPTIMIZED)

css: $(CSS_FILES)

js: $(JS_MINIFIED)

# Optimize PNG images
$(DIST_IMG_DIR)/%.png: $(SRC_IMG_DIR)/%.png
	@mkdir -p $(dir $@)
	optipng -o7 $< -out $@

# Compile SCSS to CSS
$(DIST_CSS_DIR)/%.css: $(SRC_CSS_DIR)/%.scss
	@mkdir -p $(dir $@)
	sass --style=compressed $< $@

# Minify JavaScript
$(DIST_JS_DIR)/%.min.js: $(SRC_JS_DIR)/%.js
	@mkdir -p $(dir $@)
	uglifyjs $< -c -m -o $@

clean:
	rm -rf dist
```

```bash
# Usage
make assets            # Process all assets
make images            # Optimize images only
make css               # Compile SCSS only
make js                # Minify JavaScript only
make -j4 assets        # Process in parallel
```

## Best Practices

-

**Use `.PHONY` targets**: Declare targets that don't create files as `.PHONY` to avoid conflicts with actual files and improve performance

```makefile
.PHONY: all clean install test
```

-

**Generate dependencies automatically**: Use compiler flags like `-MMD -MP` to automatically track header file dependencies, preventing incomplete rebuilds

```makefile
DEPS = $(OBJECTS:.o=.d)
-include $(DEPS)
$(CC) $(CFLAGS) -MMD -MP -c $< -o $@
```

-

**Create directories automatically**: Use `@mkdir -p $(dir $@)` before creating output files to ensure target directories exist

```makefile
$(BUILDDIR)/%.o: $(SRCDIR)/%.c
    @mkdir -p $(dir $@)
    $(CC) -c $< -o $@
```

-

**Use variables for flexibility**: Define compiler, flags, and paths as variables at the top of your Makefile for easy customization and maintenance

```makefile
CC = gcc
CFLAGS = -Wall -O2
PREFIX = /usr/local
```

-

**Leverage parallel builds**: Use `make -j` for faster builds on multi-core systems, especially for large projects with independent compilation units

-

**Separate source and build directories**: Keep generated files in a separate `build/` directory to maintain clean source trees and simplify `.gitignore` management

-

**Use pattern rules over explicit rules**: Pattern rules like `%.o: %.c` are more maintainable and scalable than writing individual rules for each file

-

**Provide informative output**: Use `@echo` to provide build progress messages while suppressing command echoing with `@` for cleaner output

```makefile
$(TARGET): $(OBJECTS)
    @echo "Linking $@..."
    @$(CC) $^ -o $@
```

## Troubleshooting

| Issue | Solution |
| --- | --- |
| **"missing separator" error** | Ensure recipe lines are indented with TAB characters, not spaces. Configure your editor to insert tabs in Makefiles |
| **Target always rebuilds** | Check file timestamps with `ls -l`. Use `make -d` to debug why Make thinks rebuild is needed. Verify prerequisites exist and have correct timestamps |
| **Variables are empty** | Use `make -p` to print all variables and their values. Check for typos in variable names. Verify variable assignment syntax (`=` vs `:=` vs `?=`) |
| **Parallel build failures** | Some targets may have missing dependencies. Run `make -j1` to identify the issue, then add proper prerequisites. Use order-only prerequisites (` |
| **"No rule to make target" error** | Verify the target name is spelled correctly. Check that prerequisite files exist. Use `make -p` to see all available targets |
| **Commands not found** | Ensure required tools are installed and in PATH. Use full paths for commands or check with `which command`. Prefix with `@` to suppress output and see actual errors |
| **Recursive make issues** | Use `$(MAKE)` instead of `make` in recipes. Export necessary variables with `export`. Consider using `-C` to change directories instead of recursive makes |
| **Pattern rules not matching** | Verify pattern syntax (`%` placement). Check that source files exist in expected locations. Use `make -d` to see rule matching process |
| **Changes not detected** | Ensure file modification times are correct. Use `make -B` to force rebuild. Check if using `-t` touched files incorrectly. Verify dependencies are listed correctly |
| **Windows path issues** | Use forward slashes `/` instead of backslashes. Consider using MSYS2 or WSL for better compatibility. Use `$(subst \,/,$(PATH))` to convert paths if needed |

Source: https://1337skills.com/cheatsheets/gnu-make/
