---
title: Kubernetes Orchestration Setup
description: Complete guide for Kubernetes cluster installation and management in homelab environments
---

# Kubernetes Orchestration Setup

Kubernetes (K8s) has become the de facto standard for container orchestration in modern homelabs. This comprehensive guide covers K8s installation, cluster management, application deployment, and best practices.

## ☸️ Kubernetes Fundamentals

### Kubernetes Architecture
```bash
# Kubernetes Cluster Components

Control Plane (Master Node):
  kube-apiserver:
    Role: Central management API
    Function: Authentication, authorization, admission control
    Port: 6443 (HTTPS)

  etcd:
    Role: Distributed key-value store
    Function: Cluster state persistence
    Storage: Consistent, highly available

  kube-scheduler:
    Role: Pod scheduling
    Function: Assigns pods to nodes
    Algorithm: Resource requirements, constraints

  kube-controller-manager:
    Role: Controller processes
    Functions: Replication, endpoints, namespaces
    Includes: Node controller, replication controller

Worker Nodes:
  kubelet:
    Role: Node agent
    Function: Manages pods and containers
    Communication: Reports to API server

  kube-proxy:
    Role: Network proxy
    Function: Service routing, load balancing
    Implementation: iptables, ipvs, eBPF

  Container Runtime:
    Role: Container execution
    Options: containerd, CRI-O, Docker
    Interface: Container Runtime Interface (CRI)
```

### Core Kubernetes Concepts
```bash
# Kubernetes Objects

Pod:
  Definition: Smallest deployable unit
  Contents: One or more containers
  Networking: Shared IP and storage
  Lifecycle: Ephemeral, replaceable

Service:
  Purpose: Network access to pods
  Types: ClusterIP, NodePort, LoadBalancer
  Discovery: DNS-based service discovery
  Load Balancing: Round-robin, session affinity

Deployment:
  Purpose: Declarative pod management
  Features: Replication, rolling updates
  Strategy: RollingUpdate, Recreate
  Health: Probes, readiness checks

ConfigMap & Secret:
  ConfigMap: Configuration data
  Secret: Sensitive data
  Mounting: Environment variables, volumes
  Updates: Hot-reload capabilities

PersistentVolume (PV):
  Purpose: Persistent storage
  Lifecycle: Independent of pods
  Types: Local, NFS, iSCSI, cloud
  Access: ReadWriteOnce, ReadOnlyMany, ReadWriteMany

PersistentVolumeClaim (PVC):
  Purpose: Storage request from user
  Binding: PV to PVC relationship
  Sizing: Requested storage capacity
  Access: Storage access modes
```

## 🔧 Kubernetes Installation

### System Requirements
```bash
# Minimum Requirements per Node
CPU: 2+ cores (4+ recommended)
RAM: 4GB+ (8GB+ recommended)
Storage: 20GB+ (50GB+ recommended)
Network: Gigabit Ethernet
OS: Ubuntu 20.04+, CentOS 8+, Debian 11+

# Recommended Homelab Cluster
Control Plane:
  Nodes: 1 (development), 3+ (production)
  CPU: 4+ cores per node
  RAM: 8GB+ per node
  Storage: 100GB+ SSD per node

Worker Nodes:
  Nodes: 2+ (production)
  CPU: 4+ cores per node
  RAM: 8GB+ per node
  Storage: 100GB+ per node
  GPU: Optional for ML workloads

# Network Requirements
- Flat network topology
- No overlapping IP ranges
- Open ports: 6443, 2379-2380, 10250, 10251, 10252
- DNS resolution between nodes
```

### kubeadm Cluster Setup
```bash
# Install Container Runtime (containerd)
cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

sudo sysctl --system

# Install containerd
sudo apt-get update
sudo apt-get install -y containerd.io

# Configure containerd
sudo mkdir -p /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
sudo systemctl restart containerd

# Install Kubernetes Components
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Initialize Control Plane
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Configure kubectl for regular user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install Network Plugin (Flannel)
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml

# Verify Cluster Status
kubectl get nodes
kubectl get pods --all-namespaces
```

### Worker Node Join
```bash
# On Worker Nodes (after kubeadm setup)
# Join cluster using token from control plane
sudo kubeadm join <control-plane-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>

# Verify node joined
kubectl get nodes

# Label nodes (optional)
kubectl label nodes <node-name> node-type=worker
kubectl label nodes <node-name> storage=ssd
```

## 🚀 Cluster Management

### Node Management
```bash
# Node Operations
kubectl get nodes                          # List all nodes
kubectl describe node <node-name>            # Node details
kubectl cordon <node-name>                  # Mark unschedulable
kubectl uncordon <node-name>                # Mark schedulable
kubectl drain <node-name> --ignore-daemonsets # Evict pods

# Node Maintenance
kubectl top nodes                          # Resource usage
kubectl get events --field-selector involvedObject.name=<node-name>

# Node Labels and Taints
kubectl label nodes <node-name> environment=production
kubectl taint nodes <node-name> environment=production:NoSchedule

# Remove node from cluster
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
kubectl delete node <node-name>
```

### Namespace Management
```bash
# Namespace Operations
kubectl create namespace development
kubectl create namespace production
kubectl get namespaces
kubectl delete namespace test

# Context and Namespace
kubectl config set-context --current --namespace=development
kubectl config get-contexts
kubectl config use-context <context-name>

# Resource Quotas
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    persistentvolumeclaims: "2"
EOF
```

## 📦 Application Deployment

### Pod Management
```yaml
# Pod Example (nginx-pod.yaml)
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
    tier: frontend
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    ports:
    - containerPort: 80
      name: http
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
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
    name: http
  type: ClusterIP
```

### Deployment Management
```yaml
# Deployment Example (app-deployment.yaml)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: myapp:1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
          readOnly: true
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: config-volume
        configMap:
          name: app-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: app-data-pvc
```

### Service Types
```yaml
# ClusterIP Service (internal only)
apiVersion: v1
kind: Service
metadata:
  name: internal-service
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP

# NodePort Service (external access)
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 3000
    nodePort: 30080
  type: NodePort

# LoadBalancer Service (cloud provider)
apiVersion: v1
kind: Service
metadata:
  name: load-balancer-service
spec:
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

## 💾 Storage Management

### Persistent Storage Setup
```yaml
# PersistentVolume (local-storage.yaml)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv
  labels:
    type: local
    storage: ssd
spec:
  storageClassName: manual
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  local:
    path: /mnt/data
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values: ["worker-node-1"]

---
# PersistentVolumeClaim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-pvc
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  selector:
    matchLabels:
      type: local
      storage: ssd
```

### Storage Classes
```yaml
# StorageClass (local-storage-class.yaml)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete

# NFS StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-storage
provisioner: nfs.csi.k8s.io
parameters:
  server: nfs-server.local
  share: /path/to/share
volumeBindingMode: Immediate
allowVolumeExpansion: true
```

## 🌐 Networking

### Ingress Configuration
```yaml
# Ingress Controller (nginx-ingress.yaml)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - app.homelab.local
    secretName: app-tls
  rules:
  - host: app.homelab.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
  - host: api.homelab.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

### Network Policies
```yaml
# Network Policy (default-deny.yaml)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

# Allow specific traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web-to-api
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web
    ports:
    - protocol: TCP
      port: 8080
```

## 🔧 Configuration and Secrets

### ConfigMap Management
```yaml
# ConfigMap (app-config.yaml)
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.json: |
    {
      "database": {
        "host": "postgres-service",
        "port": 5432
      },
      "redis": {
        "host": "redis-service",
        "port": 6379
      },
      "logging": {
        "level": "info",
        "format": "json"
      }
    }
  nginx.conf: |
    server {
        listen 80;
        server_name _;
        
        location / {
            proxy_pass http://web-service:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api {
            proxy_pass http://api-service:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

# Imperative ConfigMap creation
kubectl create configmap app-config \
  --from-file=config.json=./config.json \
  --from-file=nginx.conf=./nginx.conf
```

### Secret Management
```yaml
# Secret (app-secrets.yaml)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-url: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0BkYXRhYmFzZTo1NDMyL215eXk= # base64 encoded
  api-key: YXBpLWtleS12MzQ1Njc4OTA= # base64 encoded

# Imperative Secret creation
kubectl create secret generic app-secrets \
  --from-literal=database-url="postgresql://user:pass@database:5432/mydb" \
  --from-literal=api-key="api-key-1234567890"

# TLS Secret
kubectl create secret tls app-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

## 📊 Monitoring and Logging

### Prometheus Monitoring Stack
```yaml
# Prometheus Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.40.0
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config-volume
          mountPath: /etc/prometheus
        - name: data-volume
          mountPath: /prometheus
      volumes:
      - name: config-volume
        configMap:
          name: prometheus-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: prometheus-pvc
```

### Logging with Fluentd
```yaml
# Fluentd DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      serviceAccount: fluentd
      serviceAccountName: fluentd
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd
        image: fluent/fluentd:v1.15-debian-1
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch-service"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
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

## 🚀 Advanced Features

### Horizontal Pod Autoscaling
```yaml
# HPA Example
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Custom Resource Definitions
```yaml
# CRD Example
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: websites.mycompany.com
spec:
  group: mycompany.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              domain:
                type: string
              replicas:
                type: integer
  scope: Namespaced
  names:
    plural: websites
    singular: website
    kind: Website
```

### Jobs and CronJobs
```yaml
# Job Example
apiVersion: batch/v1
kind: Job
metadata:
  name: backup-job
spec:
  template:
    spec:
      containers:
      - name: backup
        image: backup-tool:latest
        env:
        - name: BACKUP_DESTINATION
          value: "s3://backups"
      restartPolicy: OnFailure
  backoffLimit: 4

# CronJob Example
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-tool:latest
          restartPolicy: OnFailure
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
```

## 🔒 Security Best Practices

### Pod Security Policies
```yaml
# Pod Security Policy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

### RBAC Configuration
```yaml
# ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account
  namespace: production

---
# Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]

---
# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-role-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: production
roleRef:
  kind: Role
  name: app-role
  apiGroup: rbac.authorization.k8s.io
```

## 🚨 Troubleshooting

### Common Issues and Solutions
```bash
# Pod Issues
kubectl describe pod <pod-name>                    # Pod details and events
kubectl logs <pod-name>                           # Pod logs
kubectl logs <pod-name> --previous                 # Previous container logs
kubectl exec -it <pod-name> -- /bin/bash          # Debug container

# Service Issues
kubectl describe service <service-name>              # Service details
kubectl get endpoints <service-name>                # Check endpoints
kubectl port-forward <service-name> 8080:80        # Forward port for testing

# Node Issues
kubectl describe node <node-name>                  # Node details
kubectl get events --field-selector involvedObject.name=<node-name>
kubectl top nodes                                  # Resource usage

# Network Issues
kubectl run -it --rm debug --image=nicolaka/netshoot   # Network debugging
kubectl exec -it <pod-name> -- nslookup service-name  # DNS resolution
kubectl exec -it <pod-name> -- curl service-name     # Connectivity test
```

### Debug Tools
```bash
# Resource Issues
kubectl top pods --all-namespaces                 # Resource usage
kubectl describe node <node-name> | grep Allocated   # Resource allocation
kubectl get resourcequotas                          # Quota usage

# Storage Issues
kubectl get pv,pvc                                # Persistent volumes
kubectl describe pvc <pvc-name>                     # PVC details
kubectl get events --field-selector involvedObject.kind=PersistentVolume

# Authentication Issues
kubectl auth can-i create pods --namespace=dev     # Permission check
kubectl get rolebindings,clusterrolebindings        # RBAC bindings
kubectl describe clusterrole cluster-admin          # Role details
```

## 📋 Backup and Recovery

### Velero Backup Solution
```bash
# Install Velero
curl -fsSL -o velero-v1.10.0-linux-amd64.tar.gz https://github.com/vmware-tanzu/velero/releases/download/v1.10.0/velero-v1.10.0-linux-amd64.tar.gz
tar -xvf velero-v1.10.0-linux-amd64.tar.gz
sudo mv velero-v1.10.0-linux-amd64/velero /usr/local/bin/

# Configure Velero with S3
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.4.0 \
  --bucket velero-backups \
  --backup-location-config region=us-west-2 \
  --snapshot-location-config region=us-west-2

# Create backup
velero backup create cluster-backup --include-namespaces=production

# Restore from backup
velero restore create --from-backup cluster-backup

# Scheduled backups
velero schedule create daily-backup --schedule="0 2 * * *" --ttl=72h
```

### etcd Backup
```bash
# Backup etcd data
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Restore etcd data
ETCDCTL_API=3 etcdctl snapshot restore /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --data-dir /var/lib/etcd \
  --initial-cluster-token etcd-cluster \
  --initial-advertise-peer-urls https://<node-ip>:2380 \
  --name <node-name>
```

## 📖 Further Reading

### Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubeadm Reference](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/)
- [kubectl Reference](https://kubernetes.io/docs/reference/generated/kubectl/)

### Communities
- Reddit: r/kubernetes, r/k8s, r/homelab
- Kubernetes Slack Community
- CNCF Discord Server

### Advanced Topics
- Service Mesh (Istio, Linkerd)
- GitOps (ArgoCD, Flux)
- Multi-cluster management
- Edge computing with K3s

---

**Ready to dive deeper?** Check our [Virtualization](index.md) overview for comprehensive virtualization planning!
