# Zig Cheat Sheet advanced

## Overview

Zig is a general-purpose systems programming language and toolchain designed for developing robust, high-performance software. It aims to be a better alternative to C by providing modern safety features without sacrificing performance or the ability to use C libraries. Zig has no hidden control flow, no hidden memory allocations, no garbage collector, and no undefined behavior, making it highly predictable and debuggable.

Created by Andrew Kelley in 2015, Zig has gained traction as a systems language that competes directly with C and C++. It features comptime (compile-time code execution), optional safety checks that can be disabled in release builds, and a built-in cross-compilation toolchain that can target over 30 architectures. Zig can also be used as a C/C++ compiler and build system, and its standard library is designed for zero-allocation patterns.

## Installation

### Package Managers

```bash
# macOS
brew install zig

# Ubuntu/Debian (snap)
snap install zig --classic --beta

# Arch Linux
pacman -S zig

# Windows (scoop)
scoop install zig
```

### Manual Installation

```bash
# Download from ziglang.org
wget https://ziglang.org/download/0.13.0/zig-linux-x86_64-0.13.0.tar.xz
tar xf zig-linux-x86_64-0.13.0.tar.xz
export PATH=$PATH:$PWD/zig-linux-x86_64-0.13.0

# Verify
zig version
zig zen  # Display Zig philosophy
```

## Core Language

### Variables and Types

```zig
const std = @import("std");

// Constants (preferred)
const x: i32 = 42;
const name = "Zig";  // Type inferred

// Variables (mutable)
var counter: u32 = 0;
counter += 1;

// Comptime values
comptime var ct_val: i32 = blk: {
    var result: i32 = 0;
    for (0..10) |i| {
        result += @as(i32, @intCast(i));
    }
    break :blk result;
};
```

### Primitive Types

| Type | Description | Example |
| --- | --- | --- |
| `i8` to `i128` | Signed integers | `const x: i32 = -42;` |
| `u8` to `u128` | Unsigned integers | `const x: u8 = 255;` |
| `f16`, `f32`, `f64`, `f128` | Floating point | `const pi: f64 = 3.14;` |
| `bool` | Boolean | `true`, `false` |
| `usize` | Pointer-sized unsigned | Platform-dependent |
| `comptime_int` | Compile-time integer | Unlimited precision |
| `void` | No value | `{}` |
| `noreturn` | Function never returns | `@panic()` |
| `?T` | Optional type | `null` or value |
| `!T` | Error union | Error or value |

### Functions

```zig
// Basic function
fn add(a: i32, b: i32) i32 {
    return a + b;
}

// Public function
pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("Hello, {s}!\n", .{"World"});
}

// Generic function (comptime)
fn max(comptime T: type, a: T, b: T) T {
    return if (a > b) a else b;
}

// Function pointers
const MathFn = *const fn (i32, i32) i32;
const op: MathFn = add;
const result = op(3, 4);

// Inline function
inline fn fastAdd(a: i32, b: i32) i32 {
    return a + b;
}
```

### Error Handling

```zig
// Error sets
const FileError = error{
    NotFound,
    PermissionDenied,
    IoError,
};

// Error union return type
fn readFile(path: []const u8) FileError![]u8 {
    const file = std.fs.cwd().openFile(path, .{}) catch |err| {
        return switch (err) {
            error.FileNotFound => FileError.NotFound,
            else => FileError.IoError,
        };
    };
    defer file.close();
    return file.readToEndAlloc(allocator, max_size);
}

// Try - propagate errors
fn processFile(path: []const u8) !void {
    const data = try readFile(path);
    defer allocator.free(data);
    // process data...
}

// Catch - handle errors
const value = getData() catch |err| {
    std.log.err("Failed: {}", .{err});
    return default_value;
};

// errdefer - cleanup on error only
fn createResource() !*Resource {
    const r = try allocator.create(Resource);
    errdefer allocator.destroy(r);  // Only runs if function returns error
    try r.init();
    return r;
}
```

### Optionals

```zig
// Optional type
var maybe_value: ?i32 = null;
maybe_value = 42;

// Unwrap with orelse
const value = maybe_value orelse 0;

// If-unwrap
if (maybe_value) |val| {
    std.debug.print("Value: {}\n", .{val});
} else {
    std.debug.print("No value\n", .{});
}

// While with optional
while (iterator.next()) |item| {
    process(item);
}
```

### Structs and Enums

```zig
// Struct
const Point = struct {
    x: f64,
    y: f64,

    pub fn distance(self: Point, other: Point) f64 {
        const dx = self.x - other.x;
        const dy = self.y - other.y;
        return @sqrt(dx * dx + dy * dy);
    }

    pub fn origin() Point {
        return .{ .x = 0, .y = 0 };
    }
};

// Tagged union (sum type)
const Token = union(enum) {
    number: f64,
    string: []const u8,
    plus,
    minus,
    eof,

    pub fn isOperator(self: Token) bool {
        return switch (self) {
            .plus, .minus => true,
            else => false,
        };
    }
};

// Enum
const Color = enum(u8) {
    red = 0,
    green = 1,
    blue = 2,

    pub fn toHex(self: Color) []const u8 {
        return switch (self) {
            .red => "#FF0000",
            .green => "#00FF00",
            .blue => "#0000FF",
        };
    }
};
```

### Slices and Arrays

```zig
// Array (fixed size)
const arr = [_]i32{ 1, 2, 3, 4, 5 };
const zeroes = [_]u8{0} ** 256;  // 256 zeros

// Slice (pointer + length)
const slice: []const i32 = arr[1..4]; // [2, 3, 4]

// Iterate
for (arr) |value| {
    std.debug.print("{}\n", .{value});
}

for (arr, 0..) |value, index| {
    std.debug.print("[{}] = {}\n", .{ index, value });
}

// Sentinel-terminated
const str: [:0]const u8 = "hello"; // null-terminated
```

## Memory Management

```zig
// Using allocators
const allocator = std.heap.page_allocator;

// Allocate and free
const buffer = try allocator.alloc(u8, 1024);
defer allocator.free(buffer);

// ArrayList
var list = std.ArrayList(i32).init(allocator);
defer list.deinit();
try list.append(42);
try list.appendSlice(&[_]i32{ 1, 2, 3 });

// HashMap
var map = std.StringHashMap(i32).init(allocator);
defer map.deinit();
try map.put("key", 42);
if (map.get("key")) |value| {
    std.debug.print("Value: {}\n", .{value});
}
```

## Build System

### build.zig

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "my-app",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    b.installArtifact(exe);

    const run_cmd = b.addRunArtifact(exe);
    const run_step = b.step("run", "Run the application");
    run_step.dependOn(&run_cmd.step);

    const tests = b.addTest(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&b.addRunArtifact(tests).step);
}
```

### Build Commands

| Command | Description |
| --- | --- |
| `zig build` | Build project |
| `zig build run` | Build and run |
| `zig build test` | Run tests |
| `zig build -Doptimize=ReleaseFast` | Optimized release build |
| `zig build -Dtarget=x86_64-linux` | Cross-compile |
| `zig cc main.c -o main` | Use Zig as C compiler |
| `zig fmt src/` | Format Zig source |
| `zig test src/main.zig` | Run file tests directly |

## Advanced Usage

### Comptime (Compile-Time Execution)

```zig
// Compile-time function execution
fn fibonacci(comptime n: u32) u32 {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Type-level programming
fn Matrix(comptime T: type, comptime rows: usize, comptime cols: usize) type {
    return struct {
        data: [rows][cols]T,

        const Self = @This();

        pub fn init() Self {
            return .{ .data = [_][cols]T{[_]T{0} ** cols} ** rows };
        }
    };
}

const Mat4x4 = Matrix(f32, 4, 4);
var m = Mat4x4.init();
```

### C Interop

```zig
const c = @cImport({
    @cInclude("stdio.h");
    @cInclude("stdlib.h");
});

pub fn main() void {
    _ = c.printf("Hello from C!\n");
    const ptr = c.malloc(100) orelse @panic("OOM");
    defer c.free(ptr);
}
```

### Testing

```zig
const std = @import("std");
const testing = std.testing;

test "basic addition" {
    try testing.expectEqual(@as(i32, 4), add(2, 2));
}

test "string contains" {
    const haystack = "hello world";
    try testing.expect(std.mem.indexOf(u8, haystack, "world") != null);
}
```

## Troubleshooting

| Problem | Solution |
| --- | --- |
| `error: use of undeclared identifier` | Check import statements and variable scope |
| `error: integer overflow` | Use `@intCast` or widen type; check overflow in debug |
| Segfault | Enable safety checks (`-Doptimize=Debug`); check pointer validity |
| `OutOfMemory` | Check allocator; ensure `defer free/deinit` patterns |
| Compile errors in comptime | Add `@compileLog()` to debug comptime values |
| C header import failures | Install system headers; check `@cImport` paths |
| Cross-compilation issues | Specify correct target triple; check libc availability |
| Build cache issues | Delete `zig-cache/` directory and rebuild |

Source: https://1337skills.com/cheatsheets/zig/
