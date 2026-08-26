# cert-manager intermediate

## Installation

| Platform | Command |
| --- | --- |
| **kubectl (Static Manifests)** | `kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml` |
| **Helm (Recommended)** | `helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --set installCRDs=true` |
| **macOS (cmctl CLI)** | `brew install cmctl` |
| **Linux (cmctl CLI)** | `curl -sSL https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cmctl-linux-amd64.tar.gz \| tar xz && sudo mv cmctl /usr/local/bin` |
| **Windows (cmctl CLI)** | `curl.exe -L -o cmctl.exe https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cmctl-windows-amd64.exe` |
| **Verify Installation** | `kubectl get pods -n cert-manager` |

### Helm Repository Setup

```bash
# Add Jetstack Helm repository
helm repo add jetstack https://charts.jetstack.io

# Update repository
helm repo update

# Install with custom values
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.3 \
  --values custom-values.yaml
```

## Basic Commands

| Command | Description |
| --- | --- |
| `kubectl get certificates` | List all certificates in current namespace |
| `kubectl get certificates -A` | List certificates across all namespaces |
| `kubectl describe certificate <name>` | Show detailed certificate information |
| `kubectl get certificate <name> -o yaml` | View certificate in YAML format |
| `kubectl get issuer` | List all issuers in current namespace |
| `kubectl get clusterissuer` | List all cluster-wide issuers |
| `kubectl describe issuer <name>` | Show detailed issuer information |
| `kubectl get certificaterequest` | List certificate requests |
| `kubectl get order` | View ACME certificate orders |
| `kubectl get challenge` | View ACME challenges for domain validation |
| `kubectl logs -n cert-manager deployment/cert-manager` | View cert-manager controller logs |
| `kubectl logs -n cert-manager deployment/cert-manager-webhook` | View webhook logs |
| `kubectl logs -n cert-manager deployment/cert-manager-cainjector` | View CA injector logs |
| `cmctl check api` | Verify cert-manager API is available |
| `cmctl version` | Display cert-manager version information |
| `cmctl status certificate <name>` | Check certificate status and readiness |
| `cmctl inspect secret <secret-name>` | Inspect TLS secret created by cert-manager |
| `cmctl renew <cert-name>` | Manually trigger certificate renewal |
| `kubectl get crd \| grep cert-manager` | List all cert-manager Custom Resource Definitions |
| `kubectl get events --field-selector involvedObject.name=<cert-name>` | View events related to specific certificate |

## Advanced Usage

| Command | Description |
| --- | --- |
| `cmctl approve <certificaterequest-name>` | Manually approve a certificate request |
| `cmctl deny <certificaterequest-name>` | Deny a certificate request |
| `cmctl create certificaterequest test --from-certificate-file=cert.yaml` | Create certificate request from file |
| `cmctl convert --output-format=pem --input-file=cert.yaml` | Convert certificate to PEM format |
| `cmctl experimental create acmeaccount --server=<url> --email=<email>` | Test ACME account registration |
| `kubectl annotate certificate <name> cert-manager.io/issue-temporary-certificate="true" --overwrite` | Force immediate certificate renewal |
| `kubectl delete certificaterequest <name>` | Remove failed certificate request |
| `kubectl delete order <name>` | Delete ACME order |
| `kubectl delete challenge <name>` | Remove stuck ACME challenge |
| `kubectl get certificate <name> -o jsonpath='{.status.conditions}'` | Extract certificate status conditions |
| `kubectl get secret <tls-secret> -o jsonpath='{.data.tls\.crt}' \| base64 -d \| openssl x509 -text -noout` | Decode and view certificate details |
| `kubectl get secret <tls-secret> -o jsonpath='{.data.tls\.crt}' \| base64 -d \| openssl x509 -noout -dates` | Check certificate expiration dates |
| `helm upgrade cert-manager jetstack/cert-manager --namespace cert-manager --version v1.13.3` | Upgrade cert-manager to new version |
| `kubectl rollout restart deployment -n cert-manager` | Restart all cert-manager components |
| `kubectl scale deployment cert-manager -n cert-manager --replicas=2` | Scale cert-manager for high availability |
| `kubectl get certificate --watch` | Watch certificate status changes in real-time |
| `kubectl patch certificate <name> --type merge -p '{"spec":{"renewBefore":"720h"}}'` | Modify certificate renewal window |
| `kubectl delete secret <tls-secret>` | Delete certificate secret (triggers recreation) |
| `cmctl experimental install` | Install cert-manager using cmctl tool |
| `cmctl experimental uninstall` | Uninstall cert-manager and clean up resources |

## Configuration

### Self-Signed ClusterIssuer

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-issuer
spec:
  selfSigned: {}
```

### Let's Encrypt Staging (HTTP-01 Challenge)

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Let's Encrypt Production (DNS-01 Challenge)

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - dns01:
        cloudDNS:
          project: my-gcp-project
          serviceAccountSecretRef:
            name: clouddns-dns01-solver
            key: key.json
```

### CA Issuer (Internal PKI)

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: ca-issuer
  namespace: default
spec:
  ca:
    secretName: ca-key-pair
```

### Certificate Resource

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com
  namespace: default
spec:
  secretName: example-com-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - example.com
  - www.example.com
  duration: 2160h      # 90 days
  renewBefore: 360h    # 15 days before expiry
```

### Wildcard Certificate

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: wildcard-cert
  namespace: default
spec:
  secretName: wildcard-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - "*.example.com"
  - example.com
```

### Vault Issuer

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: vault-issuer
  namespace: default
spec:
  vault:
    server: https://vault.example.com
    path: pki/sign/example-dot-com
    auth:
      kubernetes:
        mountPath: /v1/auth/kubernetes
        role: cert-manager
        secretRef:
          name: vault-token
          key: token
```

### Helm Values Configuration

```yaml
# custom-values.yaml
installCRDs: true
replicaCount: 2

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi

prometheus:
  enabled: true
  servicemonitor:
    enabled: true

webhook:
  replicaCount: 2

cainjector:
  replicaCount: 2
```

## Common Use Cases

### Use Case 1: Secure Ingress with Let's Encrypt

```bash
# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Create Ingress with TLS annotation
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - example.com
    secretName: example-com-tls
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: example-service
            port:
              number: 80
EOF

# Verify certificate creation
kubectl get certificate
kubectl describe certificate example-com-tls
```

### Use Case 2: Internal Service mTLS

```bash
# Create self-signed CA
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-issuer
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: my-ca
  namespace: cert-manager
spec:
  isCA: true
  commonName: my-ca
  secretName: my-ca-secret
  privateKey:
    algorithm: ECDSA
    size: 256
  issuerRef:
    name: selfsigned-issuer
    kind: ClusterIssuer
EOF

# Create CA issuer from generated CA
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: my-ca-issuer
spec:
  ca:
    secretName: my-ca-secret
EOF

# Issue service certificates
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: service-a-cert
  namespace: default
spec:
  secretName: service-a-tls
  duration: 8760h
  renewBefore: 720h
  subject:
    organizations:
    - my-org
  commonName: service-a.default.svc.cluster.local
  dnsNames:
  - service-a.default.svc.cluster.local
  issuerRef:
    name: my-ca-issuer
    kind: ClusterIssuer
EOF
```

### Use Case 3: Wildcard Certificate with DNS-01

```bash
# Create DNS provider secret (example: Cloudflare)
kubectl create secret generic cloudflare-api-token \
  --from-literal=api-token=YOUR_CLOUDFLARE_API_TOKEN

# Create ClusterIssuer with DNS-01 solver
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-dns
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-dns
    solvers:
    - dns01:
        cloudflare:
          email: admin@example.com
          apiTokenSecretRef:
            name: cloudflare-api-token
            key: api-token
EOF

# Request wildcard certificate
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: wildcard-example
  namespace: default
spec:
  secretName: wildcard-example-tls
  issuerRef:
    name: letsencrypt-dns
    kind: ClusterIssuer
  dnsNames:
  - "*.example.com"
  - example.com
EOF

# Monitor certificate issuance
kubectl get certificate wildcard-example -w
```

### Use Case 4: Securing Kubernetes Webhooks

```bash
# Create certificate for webhook
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: webhook-cert
  namespace: webhook-system
spec:
  secretName: webhook-server-cert
  duration: 8760h
  renewBefore: 720h
  issuerRef:
    name: selfsigned-issuer
    kind: ClusterIssuer
  dnsNames:
  - webhook-service.webhook-system.svc
  - webhook-service.webhook-system.svc.cluster.local
EOF

# Reference in webhook configuration
kubectl apply -f - <<EOF
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: my-webhook
  annotations:
    cert-manager.io/inject-ca-from: webhook-system/webhook-cert
webhooks:
- name: webhook.example.com
  clientConfig:
    service:
      name: webhook-service
      namespace: webhook-system
      path: "/validate"
    caBundle: "" # Injected by cert-manager
EOF
```

### Use Case 5: Certificate Rotation and Renewal

```bash
# Create certificate with short duration for testing
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: short-lived-cert
  namespace: default
spec:
  secretName: short-lived-tls
  duration: 24h
  renewBefore: 8h
  issuerRef:
    name: selfsigned-issuer
    kind: ClusterIssuer
  dnsNames:
  - test.example.com
EOF

# Monitor renewal
kubectl get certificate short-lived-cert -w

# Force immediate renewal
kubectl annotate certificate short-lived-cert \
  cert-manager.io/issue-temporary-certificate="true" \
  --overwrite

# Check renewal history
kubectl get certificaterequest -l cert-manager.io/certificate-name=short-lived-cert

# Verify new certificate
cmctl inspect secret short-lived-tls
```

## Best Practices

-

**Use ClusterIssuers for shared certificates**: ClusterIssuers can be referenced from any namespace, reducing configuration duplication across your cluster

-

**Start with Let's Encrypt staging**: Always test with staging environment first to avoid hitting production rate limits (50 certificates per domain per week)

-

**Set appropriate renewal windows**: Configure `renewBefore` to at least 1/3 of certificate duration to allow multiple retry attempts before expiration

-

**Monitor certificate expiration**: Enable Prometheus metrics and set up alerts for certificates expiring within 7-14 days using `certmanager_certificate_expiration_timestamp_seconds`

-

**Use DNS-01 for wildcards and internal services**: DNS-01 challenge is required for wildcard certificates and works better for services not exposed to internet

-

**Implement proper RBAC**: Restrict access to Issuers and certificate secrets using Kubernetes RBAC to prevent unauthorized certificate creation

-

**Version control your configurations**: Store Certificate and Issuer manifests in Git to track changes and enable GitOps workflows

-

**Use separate issuers per environment**: Create different issuers for dev/staging/prod to isolate credentials and prevent cross-environment certificate issues

-

**Enable CA injection for webhooks**: Use `cert-manager.io/inject-ca-from` annotation to automatically inject CA bundles into webhook configurations

-

**Plan for disaster recovery**: Backup CA private keys and ACME account credentials stored in Kubernetes secrets to external secure storage

## Troubleshooting

| Issue | Solution |
| --- | --- |
| **Certificate stuck in "Pending"** | Check certificate request: `kubectl describe certificaterequest <name>`. Look for ACME challenge failures or issuer configuration errors |
| **ACME HTTP-01 challenge failing** | Verify ingress is accessible: `curl http://<domain>/.well-known/acme-challenge/test`. Check ingress class matches solver configuration |
| **DNS-01 challenge timeout** | Confirm DNS provider credentials: `kubectl get secret <dns-secret> -o yaml`. Verify DNS propagation: `dig TXT _acme-challenge.<domain>` |
| **"Too many certificates" rate limit** | Switch to Let's Encrypt staging server or wait 7 days. Check rate limits: [https://letsencrypt.org/docs/rate-limits/](https://letsencrypt.org/docs/rate-limits/) |
| **Certificate not renewing automatically** | Check `renewBefore` setting and cert-manager logs: `kubectl logs -n cert-manager deployment/cert-manager`. Verify controller is running |
| **Webhook connection failures** | Verify webhook service is running: `kubectl get svc -n cert-manager`. Check webhook certificate validity: `cmctl check api` |
| **CA injection not working** | Ensure cainjector is running: `kubectl get pods -n cert-manager`. Verify annotation syntax: `cert-manager.io/inject-ca-from: namespace/certificate` |
| **Certificate shows "Ready=False"** | Get detailed status: `cmctl status certificate <name>`. Check events: `kubectl get events --field-selector involvedObject.name=<cert-name>` |
| **Order stuck in "Pending"** | Delete order to retry: `kubectl delete order <order-name>`. Certificate controller will create new order automatically |
| **Secret not created after certificate ready** | Check secret name matches `secretName` in Certificate spec. Verify namespace: `kubectl get secret <name> -n <namespace>` |
| **Wildcard certificate validation fails** | Ensure DNS-01 solver is configured (HTTP-01 doesn't support wildcards). Verify DNS provider permissions for TXT record creation |
| **Certificate shows wrong issuer** | Delete certificate request: `kubectl delete certificaterequest <name>`. Update Certificate spec with correct `issuerRef` |
| **High memory usage** | Reduce certificate count or increase resources: `kubectl set resources deployment cert-manager -n cert-manager --limits=memory=512Mi` |
| **Duplicate certificates created** | Check for multiple Certificate resources with same `secretName`. Remove duplicates to prevent conflicts |
| **ACME account registration fails** | Verify email format in issuer spec. Check ACME server URL is correct. Review cert-manager logs for detailed error messages |

### Debug Command Sequence

```bash
# Complete troubleshooting workflow
kubectl describe certificate <cert-name>
kubectl get certificaterequest -l cert-manager.io/certificate-name=<cert-name>
kubectl describe certificaterequest <request-name>
kubectl get order
kubectl describe order <order-name>
kubectl get challenge
kubectl describe challenge <challenge-name>
kubectl logs -n cert-manager deployment/cert-manager --tail=100
```

### Common Log Patterns

```bash
# Search for specific certificate errors
kubectl logs -n cert-manager deployment/cert-manager | grep "certificate=<cert-name>"

# Find ACME challenge errors
kubectl logs -n cert-manager deployment/cert-manager | grep "challenge"

# Check for rate limit errors
kubectl logs -n cert-manager deployment/cert-manager | grep "rate limit"

# Monitor certificate renewal attempts
kubectl logs -n cert-manager deployment/cert-manager -f | grep "renewal"
```

Source: https://1337skills.com/cheatsheets/cert-manager/
