# Deployment Topologies

## Overview

This guide covers common deployment patterns for Retrace in different infrastructure environments.

**Key decisions:**
1. Where to record (which services/containers)
2. Where to store recordings (local, network, cloud)
3. How to enable/disable recording (env vars, config, dynamic)
4. How to access recordings (dev machines, shared storage)

---

## Basic patterns

### Pattern 1: Single server / VM

**Use case:** Traditional server deployment, monolithic app.

```
┌─────────────────────────────┐
│  Application Server         │
│  ┌───────────────────────┐  │
│  │  App Process          │  │
│  │  RETRACE=1            │  │
│  │  RETRACE_RECORDING_   │  │
│  │    PATH=/var/retrace  │  │
│  └───────────────────────┘  │
│           ↓                  │
│  /var/retrace/recordings/   │
│  ├── 2026-01-21-001/        │
│  ├── 2026-01-21-002/        │
│  └── ...                     │
└─────────────────────────────┘
```

**Setup:**

```bash
# Create recording directory
sudo mkdir -p /var/retrace/recordings
sudo chown appuser:appuser /var/retrace/recordings

# Set env vars in systemd service
cat > /etc/systemd/system/myapp.service <<EOF
[Service]
Environment="RETRACE=1"
Environment="RETRACE_RECORDING_PATH=/var/retrace/recordings"
ExecStart=/usr/bin/python3.11 /opt/myapp/app.py
User=appuser
EOF

# Enable and start
sudo systemctl enable myapp
sudo systemctl start myapp
```

**Accessing recordings:**

```bash
# Copy to dev machine
scp -r server:/var/retrace/recordings/2026-01-21-001/ ./
```

---

### Pattern 2: Docker container

**Use case:** Containerized app, single container.

```
┌─────────────────────────────┐
│  Docker Container           │
│  ┌───────────────────────┐  │
│  │  App Process          │  │
│  │  env: RETRACE=1       │  │
│  └───────────────────────┘  │
│           ↓                  │
│  /recordings (volume)       │
└──────────┬──────────────────┘
           ↓
    Host: ./recordings/
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  app:
    build: .
    environment:
      - RETRACE=1
      - RETRACE_RECORDING_PATH=/recordings
    volumes:
      - ./recordings:/recordings
    ports:
      - "5000:5000"
```

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Retrace
RUN pip install --upgrade pip && \
    pip install retracesoftware.proxy requests && \
    python -m retracesoftware.autoenable

# Copy app
COPY . .

CMD ["python", "app.py"]
```

**Accessing recordings:**

```bash
# Recordings appear in ./recordings/ on host
ls ./recordings/
```

---

### Pattern 3: Kubernetes pod

**Use case:** K8s deployment, cloud-native.

```
┌─────────────────────────────┐
│  Kubernetes Pod             │
│  ┌───────────────────────┐  │
│  │  App Container        │  │
│  │  env: RETRACE=1       │  │
│  └───────────────────────┘  │
│           ↓                  │
│  PersistentVolumeClaim      │
└──────────┬──────────────────┘
           ↓
    PersistentVolume
    (EBS, NFS, etc.)
```

**deployment.yaml:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: retrace-recordings
spec:
  accessModes:
    - ReadWriteMany  # Allow multiple pods to write
  resources:
    requests:
      storage: 100Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:latest
        env:
        - name: RETRACE
          value: "1"
        - name: RETRACE_RECORDING_PATH
          value: "/recordings"
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        volumeMounts:
        - name: recordings
          mountPath: /recordings
      volumes:
      - name: recordings
        persistentVolumeClaim:
          claimName: retrace-recordings
```

**Per-pod naming:**

To avoid recording collisions across pods, include pod name in path:

```yaml
# In deployment.yaml
env:
- name: RETRACE_RECORDING_PATH
  value: "/recordings/$(POD_NAME)"
```

**Accessing recordings:**

```bash
# From a pod
kubectl exec -it myapp-abc123 -- ls /recordings

# Copy to local
kubectl cp myapp-abc123:/recordings/crash-001 ./crash-001
```

---

## Storage strategies

### Local disk

**Pros:**
- Fast
- Simple setup
- No network dependencies

**Cons:**
- Lost if container/pod dies
- Not shared across instances
- Disk space limits

**Use when:** Development, short-term debugging.

### Network storage (NFS, EFS)

**Pros:**
- Shared across instances
- Survives pod restarts
- Centralized access

**Cons:**
- Network latency
- Requires NFS server/EFS setup
- Cost (for managed services)

**Kubernetes example (EFS):**

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: retrace-efs
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: fs-abc123.efs.us-east-1.amazonaws.com
    path: /retrace-recordings
```

**Use when:** Production, multi-instance deployments.

### Cloud storage (S3, GCS, Azure Blob)

**Pros:**
- Unlimited capacity
- Managed service
- Retention/lifecycle policies
- Access from anywhere

**Cons:**
- Must upload after recording completes
- Slower access
- Additional cost

**Pattern: Record locally, upload to S3**

```python
# In your app shutdown hook
import os
import boto3

def upload_recording():
    recording_path = os.environ['RETRACE_RECORDING_PATH']
    s3 = boto3.client('s3')
    
    # Upload entire recording directory
    for root, dirs, files in os.walk(recording_path):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = f"recordings/{os.path.basename(recording_path)}/{file}"
            s3.upload_file(local_path, 'my-recordings-bucket', s3_key)

# Register shutdown hook
import atexit
atexit.register(upload_recording)
```

**Kubernetes sidecar pattern:**

```yaml
# Sidecar container that syncs recordings to S3
- name: s3-sync
  image: amazon/aws-cli
  command:
  - /bin/sh
  - -c
  - |
    while true; do
      aws s3 sync /recordings s3://my-recordings-bucket/recordings/
      sleep 300  # Sync every 5 minutes
    done
  volumeMounts:
  - name: recordings
    mountPath: /recordings
  env:
  - name: AWS_ACCESS_KEY_ID
    valueFrom:
      secretKeyRef:
        name: aws-credentials
        key: access-key-id
  - name: AWS_SECRET_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: aws-credentials
        key: secret-access-key
```

**Use when:** Long-term retention, multi-team access, unlimited storage needed.

---

## Recording control strategies

### Strategy 1: Always-on recording

**Config:**

```yaml
env:
- name: RETRACE
  value: "1"
- name: RETRACE_RECORDING_PATH
  value: "/recordings"
```

**Pros:**
- Simple
- Captures everything
- No missed bugs

**Cons:**
- High storage usage
- Constant overhead
- Most recordings never used

**Use when:** Early testing, low traffic services.

---

### Strategy 2: ConfigMap toggle

**Config:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: retrace-config
data:
  enabled: "true"  # Toggle this to enable/disable
  recording_path: "/recordings"
---
apiVersion: apps/v1
kind: Deployment
# ...
spec:
  template:
    spec:
      containers:
      - name: app
        envFrom:
        - configMapRef:
            name: retrace-config
```

**Enable/disable:**

```bash
# Disable
kubectl edit configmap retrace-config
# Change enabled: "false"

# Restart pods
kubectl rollout restart deployment myapp
```

**Pros:**
- Central control
- No code changes
- Can toggle per environment

**Cons:**
- Requires pod restart
- Not dynamic (can't toggle for single request)

**Use when:** You want manual control, infrequent recording.

---

### Strategy 3: Sampling via code

**Config:**

```python
import os
import random

# In request handler
if random.random() < 0.1:  # 10% sampling
    os.environ['RETRACE'] = '1'
    os.environ['RETRACE_RECORDING_PATH'] = f'/recordings/request-{request_id}'
```

**Pros:**
- Dynamic per-request
- Configurable sampling rate
- No infrastructure changes

**Cons:**
- Requires code changes
- More complex

**Use when:** High-traffic production, want to sample.

---

### Strategy 4: Feature flag integration

**Config:**

```python
import os
from launchdarkly import ldclient

ld_client = ldclient.get()

# In request handler
if ld_client.variation('enable-retrace', user, False):
    os.environ['RETRACE'] = '1'
    os.environ['RETRACE_RECORDING_PATH'] = f'/recordings/user-{user.id}'
```

**Pros:**
- Remote control
- Per-user/tenant targeting
- Gradual rollout

**Cons:**
- Requires feature flag service
- More complexity

**Use when:** SaaS product, want fine-grained control.

---

## CI/CD integration

### Pattern 1: Record on test failure

**GitHub Actions example:**

```yaml
name: Tests with Retrace

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install retracesoftware.proxy
        python -m retracesoftware.autoenable
    
    - name: Run tests with Retrace
      run: |
        RETRACE=1 RETRACE_RECORDING_PATH=./test-recordings pytest
      continue-on-error: true
    
    - name: Upload recordings on failure
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: test-recordings
        path: test-recordings/
```

**Accessing recordings:**

Download from GitHub Actions artifacts, replay locally.

---

### Pattern 2: Record integration tests

**GitLab CI example:**

```yaml
test:
  stage: test
  image: python:3.11
  script:
    - pip install retracesoftware.proxy
    - python -m retracesoftware.autoenable
    - RETRACE=1 RETRACE_RECORDING_PATH=./recordings pytest tests/integration
  artifacts:
    when: on_failure
    paths:
      - recordings/
    expire_in: 7 days
```

---

## Multi-service architectures

### Microservices challenge

Each service needs recording, but how to correlate?

**Pattern: Trace ID propagation**

```python
# Service A
import uuid
trace_id = str(uuid.uuid4())

os.environ['RETRACE'] = '1'
os.environ['RETRACE_RECORDING_PATH'] = f'/recordings/{trace_id}/service-a'

# Call Service B with trace ID
requests.post('http://service-b/api', headers={'X-Trace-ID': trace_id})
```

```python
# Service B
trace_id = request.headers.get('X-Trace-ID')

os.environ['RETRACE'] = '1'
os.environ['RETRACE_RECORDING_PATH'] = f'/recordings/{trace_id}/service-b'
```

**Result:**

```
recordings/
└── abc-123-def-456/
    ├── service-a/
    │   └── trace.bin
    └── service-b/
        └── trace.bin
```

Now you can replay both services' recordings to debug the full flow.

---

## Scaling considerations

### Storage capacity planning

**Example calculation:**

- 100 requests/second
- 10% sampling = 10 recordings/second
- 50MB average per recording
- Storage: 10 rec/sec × 50MB = 500MB/sec = **1.8TB/hour**

**Mitigation:**
- Reduce sampling rate
- Implement aggressive retention (7 days max)
- Upload to S3, delete local copies
- Filter which services record

### Performance at scale

**Overhead distribution:**

```
Service with 1000 req/sec:
- No recording: 100ms avg latency
- 10% recording: 103ms avg latency (3% increase)
- 100% recording: 125ms avg latency (25% increase)
```

**Recommendation:** Keep recording <30% of traffic.

---

## Security considerations

### Network isolation

**Recordings contain production data.** Ensure storage is protected:

```yaml
# Kubernetes NetworkPolicy - limit access to recording volume
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: retrace-storage-policy
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: developer
```

### Encryption at rest

**If using S3:**

```yaml
# Enable default encryption
aws s3api put-bucket-encryption \
  --bucket my-recordings-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

**If using EFS:**

```yaml
# Enable encryption
aws efs create-file-system \
  --encrypted \
  --kms-key-id alias/aws/elasticfilesystem
```

---

## Troubleshooting

### Recordings not appearing

**Check:**
1. Environment variables set: `kubectl exec pod -- env | grep RETRACE`
2. Directory writable: `kubectl exec pod -- touch /recordings/test`
3. Retrace installed: `kubectl exec pod -- python -c "import retracesoftware.proxy"`

### Disk full

**Solutions:**
- Implement retention policy
- Move to network/cloud storage
- Reduce sampling rate

### Network storage slow

**Solutions:**
- Use local disk for recording, background upload to S3
- Increase network bandwidth
- Use faster storage tier (EFS provisioned throughput)

---

## Reference architectures

### Small team (1-5 developers)

- **Recording:** Docker Compose, local volumes
- **Storage:** Shared NFS mount
- **Access:** Direct filesystem access

### Medium team (10-50 developers)

- **Recording:** Kubernetes, PVC
- **Storage:** EFS or S3 (with lifecycle policies)
- **Access:** kubectl cp or S3 download

### Enterprise (100+ developers)

- **Recording:** Kubernetes, per-service sampling
- **Storage:** S3 with intelligent tiering
- **Access:** Self-service portal, S3 pre-signed URLs
- **Retention:** Automated cleanup, compliance-aware

---

## Next steps

- [Record in production](guides/record-in-production.md) - safety guidelines
- [Security model](security-model.md) - data handling
- [Troubleshooting](troubleshooting.md)
```

