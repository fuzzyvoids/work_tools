# Kubernetes Cheatsheet advanced

Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications.

## Installation and Setup

### kubectl Installation

```bash
# Linux installation
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# macOS installation
brew install kubectl

# Windows installation (PowerShell)
curl.exe -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"

# Verify installation
kubectl version --client
```

### Cluster Setup Options

```bash
# Minikube (local development)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start

# Kind (Kubernetes in Docker)
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
kind create cluster

# kubeadm (production clusters)
sudo apt-get update && sudo apt-get install -y kubeadm kubelet kubectl
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```

### Configuration

```bash
# Set up kubeconfig
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# View current context
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context my-cluster

# Set default namespace
kubectl config set-context --current --namespace=my-namespace
```

## Basic Commands

### Cluster Information

```bash
# Cluster info
kubectl cluster-info

# Node information
kubectl get nodes
kubectl describe node <node-name>

# Cluster version
kubectl version

# API resources
kubectl api-resources

# API versions
kubectl api-versions
```

### Namespace Management

```bash
# List namespaces
kubectl get namespaces
kubectl get ns

# Create namespace
kubectl create namespace my-namespace

# Delete namespace
kubectl delete namespace my-namespace

# Set default namespace
kubectl config set-context --current --namespace=my-namespace
```

### Basic Resource Operations

```bash
# Get resources
kubectl get pods
kubectl get services
kubectl get deployments
kubectl get all

# Describe resources
kubectl describe pod <pod-name>
kubectl describe service <service-name>

# Create resources
kubectl create -f manifest.yaml
kubectl apply -f manifest.yaml

# Delete resources
kubectl delete pod <pod-name>
kubectl delete -f manifest.yaml
```

## Pod Management

### Pod Operations

```bash
# List pods
kubectl get pods
kubectl get pods -o wide
kubectl get pods --all-namespaces

# Create pod from image
kubectl run nginx --image=nginx

# Get pod details
kubectl describe pod <pod-name>

# Get pod logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>  # Follow logs
kubectl logs <pod-name> -c <container-name>  # Multi-container pod

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/bash
kubectl exec <pod-name> -- ls /app

# Port forwarding
kubectl port-forward <pod-name> 8080:80

# Copy files
kubectl cp <pod-name>:/path/to/file ./local-file
kubectl cp ./local-file <pod-name>:/path/to/file
```

### Pod Manifest Example

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    env:
    - name: ENV_VAR
      value: "production"
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

## Deployments

### Deployment Operations

```bash
# Create deployment
kubectl create deployment nginx --image=nginx:1.21

# Scale deployment
kubectl scale deployment nginx --replicas=3

# Update deployment image
kubectl set image deployment/nginx nginx=nginx:1.22

# Rollout status
kubectl rollout status deployment/nginx

# Rollout history
kubectl rollout history deployment/nginx

# Rollback deployment
kubectl rollout undo deployment/nginx
kubectl rollout undo deployment/nginx --to-revision=2

# Delete deployment
kubectl delete deployment nginx
```

### Deployment Manifest

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Services

### Service Types and Operations

```bash
# Expose deployment as service
kubectl expose deployment nginx --port=80 --type=ClusterIP

# Create service from manifest
kubectl apply -f service.yaml

# List services
kubectl get services
kubectl get svc

# Describe service
kubectl describe service nginx

# Delete service
kubectl delete service nginx
```

### Service Manifests

```yaml
# ClusterIP Service
apiVersion: v1
kind: Service
metadata:
  name: nginx-clusterip
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP

---
# NodePort Service
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
    nodePort: 30080
  type: NodePort

---
# LoadBalancer Service
apiVersion: v1
kind: Service
metadata:
  name: nginx-loadbalancer
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

## ConfigMaps and Secrets

### ConfigMap Operations

```bash
# Create ConfigMap from literal
kubectl create configmap app-config --from-literal=database_url=mysql://localhost:3306

# Create ConfigMap from file
kubectl create configmap app-config --from-file=config.properties

# Create ConfigMap from directory
kubectl create configmap app-config --from-file=config/

# Get ConfigMap
kubectl get configmap app-config -o yaml

# Delete ConfigMap
kubectl delete configmap app-config
```

### ConfigMap Manifest

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "mysql://localhost:3306"
  debug_mode: "true"
  config.properties:|
    database.host=localhost
    database.port=3306
    database.name=myapp
```

### Secret Operations

```bash
# Create secret from literal
kubectl create secret generic app-secret --from-literal=password=mysecretpassword

# Create secret from file
kubectl create secret generic app-secret --from-file=ssh-privatekey=~/.ssh/id_rsa

# Create TLS secret
kubectl create secret tls tls-secret --cert=tls.crt --key=tls.key

# Get secret (base64 encoded)
kubectl get secret app-secret -o yaml

# Decode secret
kubectl get secret app-secret -o jsonpath='\\\\{.data.password\\\\}'|base64 --decode
```

### Secret Manifest

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded 'admin'
  password: MWYyZDFlMmU2N2Rm  # base64 encoded password
```

### Using ConfigMaps and Secrets in Pods

```yaml
# pod-with-config.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: nginx
    env:
    - name: DATABASE_URL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_url
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: password
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: config-volume
    configMap:
      name: app-config
  - name: secret-volume
    secret:
      secretName: app-secret
```

## Persistent Volumes

### PersistentVolume and PersistentVolumeClaim

```yaml
# persistent-volume.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-storage
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-storage
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: manual
```

### Using PVC in Pod

```yaml
# pod-with-pvc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-storage
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: storage
      mountPath: /usr/share/nginx/html
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: pvc-storage
```

## Ingress

### Ingress Controller Setup

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Verify installation
kubectl get pods -n ingress-nginx
kubectl get services -n ingress-nginx
```

### Ingress Manifest

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: tls-secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

## Monitoring and Debugging

### Resource Monitoring

```bash
# Resource usage
kubectl top nodes
kubectl top pods
kubectl top pods --containers

# Events
kubectl get events
kubectl get events --sort-by=.metadata.creationTimestamp

# Describe for debugging
kubectl describe pod <pod-name>
kubectl describe node <node-name>

# Logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # Previous container logs
kubectl logs -l app=nginx  # Logs from all pods with label
```

### Troubleshooting Commands

```bash
# Check pod status
kubectl get pods -o wide

# Debug pod issues
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl exec -it <pod-name> -- /bin/sh

# Network debugging
kubectl run debug --image=busybox --rm -it -- /bin/sh
kubectl run debug --image=nicolaka/netshoot --rm -it -- /bin/bash

# DNS debugging
kubectl run debug --image=busybox --rm -it -- nslookup kubernetes.default

# Check resource quotas
kubectl describe resourcequota
kubectl describe limitrange
```

## Advanced Features

### Jobs and CronJobs

```yaml
# job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi-calculation
spec:
  template:
    spec:
      containers:
      - name: pi
        image: perl
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
  backoffLimit: 4

---
# cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-tool
            command: ["/bin/sh", "-c", "backup-script.sh"]
          restartPolicy: OnFailure
```

### DaemonSet

```yaml
# daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-daemonset
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluentd:v1.14
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

### StatefulSet

```yaml
# statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-statefulset
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "rootpassword"
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: mysql-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

## Security

### RBAC (Role-Based Access Control)

```yaml
# rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: \\\\{\\\\}
  policyTypes:
  - Ingress
  - Egress

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-nginx
spec:
  podSelector:
    matchLabels:
      app: nginx
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 80
```

### Pod Security Standards

```yaml
# pod-security.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    image: nginx
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /var/cache/nginx
  volumes:
  - name: tmp
    emptyDir: \\\\{\\\\}
  - name: cache
    emptyDir: \\\\{\\\\}
```

## Helm Package Manager

### Helm Installation

```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3|bash

# Add repository
helm repo add stable https://charts.helm.sh/stable
helm repo update

# Search charts
helm search repo nginx

# Install chart
helm install my-nginx stable/nginx-ingress

# List releases
helm list

# Upgrade release
helm upgrade my-nginx stable/nginx-ingress

# Uninstall release
helm uninstall my-nginx
```

### Creating Helm Charts

```bash
# Create new chart
helm create my-app

# Chart structure
my-app/
|-- Chart.yaml
|-- values.yaml
|-- templates/
|   |-- deployment.yaml
|   |-- service.yaml
|   `-- ingress.yaml
`-- charts/
```

## Best Practices

### Resource Management

```yaml
# Always specify resource requests and limits
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"

# Use appropriate restart policies
restartPolicy: Always  # For Deployments
restartPolicy: OnFailure  # For Jobs
restartPolicy: Never  # For one-time tasks
```

### Health Checks

```yaml
# Liveness and readiness probes
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Labels and Annotations

```yaml
# Use consistent labeling
metadata:
  labels:
    app: myapp
    version: v1.0.0
    component: frontend
    part-of: myapp-system
    managed-by: helm
  annotations:
    deployment.kubernetes.io/revision: "1"
    description: "Frontend component of myapp"
```

## Useful Commands Reference

```bash
# Quick reference commands
kubectl get all                           # Get all resources
kubectl get pods -o wide                  # Detailed pod info
kubectl describe pod <name>               # Pod details
kubectl logs -f <pod>                     # Follow logs
kubectl exec -it <pod> -- /bin/bash      # Shell into pod
kubectl port-forward <pod> 8080:80       # Port forward
kubectl apply -f manifest.yaml           # Apply manifest
kubectl delete -f manifest.yaml          # Delete from manifest
kubectl scale deployment <name> --replicas=3  # Scale deployment
kubectl rollout restart deployment <name>     # Restart deployment
kubectl get events --sort-by=.metadata.creationTimestamp  # Recent events
kubectl top nodes                        # Node resource usage
kubectl top pods                         # Pod resource usage
```

## Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)

- [kubectl Reference](https://kubernetes.io/docs/reference/kubectl/)

- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)

- [Helm Documentation](https://helm.sh/docs/)

- [Kubernetes Community](https://kubernetes.io/community/)

Source: https://1337skills.com/cheatsheets/kubernetes/
