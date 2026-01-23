# Record Safely in Production

## When to record in production

Record in production when:
- Bugs only appear with real data/traffic patterns
- Local reproduction is impossible
- You need to preserve the exact execution state for debugging

Don't record everything; use targeted recording based on your needs.

---

## Safety considerations

### Performance overhead

**Recording adds ~10-30% overhead** depending on:
- How much code crosses external boundaries
- Frequency of external calls (network, DB, filesystem)
- Size of data being serialized

**Mitigation strategies:**
- Sample traffic (record 1-10% of requests)
- Filter by specific conditions (error rates, specific endpoints)
- Record only during investigation windows

### Data sensitivity

Recording captures:
- Function arguments at external boundaries
- Return values from external calls
- Exception details

**Does NOT capture:**
- Pure internal computation
- Local variables that don't cross boundaries
- Credentials/tokens (if not passed through intercepted calls)

See [Security Model](../security-model.md) for full details.

---

## Recording strategies

### Strategy 1: Sample-based recording

Record a percentage of requests:

```python
import random
import os

# In your app initialization
if random.random() < 0.1:  # 10% sampling
    os.environ['RETRACE'] = '1'
    os.environ['RETRACE_RECORDING_PATH'] = f'recordings/{request_id}'
```

**Use when:** You want continuous coverage with minimal overhead.

### Strategy 2: Error-triggered recording

Record only when errors occur:

```python
import os

@app.errorhandler(Exception)
def handle_error(e):
    # Record this request
    recording_path = f'recordings/error_{request_id}'
    os.environ['RETRACE'] = '1'
    os.environ['RETRACE_RECORDING_PATH'] = recording_path
    # Re-execute with recording enabled
    # (implementation depends on your framework)
```

**Use when:** Overhead must be minimal; you only care about failures.

**Note:** This requires re-executing the request. Some frameworks make this easier than others.

### Strategy 3: Conditional recording

Record based on request attributes:

```python
import os

# Record specific customers, endpoints, or conditions
if request.headers.get('X-Debug') == 'record':
    os.environ['RETRACE'] = '1'
    os.environ['RETRACE_RECORDING_PATH'] = f'recordings/{request_id}'
```

**Use when:** Debugging specific issues or working with known problematic inputs.

### Strategy 4: Investigation windows

Enable recording manually for time-limited investigations:

```bash
# Enable for all traffic
export RETRACE=1
export RETRACE_RECORDING_PATH=/var/recordings

# Restart service
systemctl restart myapp

# ... investigate for 1 hour ...

# Disable
unset RETRACE
systemctl restart myapp
```

**Use when:** Chasing an intermittent issue with known time windows.

---

## Storage management

### Disk usage

Each recording creates:
- `trace.bin` (size depends on execution: typically 1MB - 100MB)
- `run/` directory (copy of source files)
- Metadata files (~10KB)

**Example:** Flask app handling 100 req/sec, recording 10%, ~50MB/recording average:
- 10 recordings/sec × 50MB = 500MB/sec = **1.8TB/hour**

**This is not sustainable.** Use filtering.

### Retention policy

Example retention script:

```bash
#!/bin/bash
# Keep recordings for 7 days, delete older ones
find /var/recordings -type d -mtime +7 -exec rm -rf {} +

# Keep only failed recordings longer term
# (implementation depends on how you mark failures)
```

**Recommended:**
- Keep error recordings: 30 days
- Keep sample recordings: 7 days
- Delete immediately after debugging: ad-hoc recordings

### Storage location

**Local disk:**
```bash
RETRACE_RECORDING_PATH=/var/retrace/recordings
```

**Network storage** (if supported by your infra):
```bash
RETRACE_RECORDING_PATH=/mnt/nfs/retrace/recordings
```

**S3/blob storage:**
After recording completes, upload trace.bin:
```bash
aws s3 cp /var/retrace/recordings/ s3://mybucket/retrace/ --recursive
```

---

## Deployment patterns

### Container/Docker

**Option 1: Environment variables in compose/k8s:**

```yaml
environment:
  - RETRACE=1
  - RETRACE_RECORDING_PATH=/recordings
volumes:
  - ./recordings:/recordings
```

**Option 2: Sidecar for storage:**

Run a sidecar container that syncs recordings to S3/NFS.

See [Deployment Topologies](../deployment-topologies.md) for detailed patterns.

### Kubernetes

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    env:
    - name: RETRACE
      value: "1"
    - name: RETRACE_RECORDING_PATH
      value: "/recordings"
    volumeMounts:
    - name: recordings
      mountPath: /recordings
  volumes:
  - name: recordings
    persistentVolumeClaim:
      claimName: retrace-recordings
```

### Serverless

⚠️ Limited support currently. Serverless environments often have:
- Ephemeral storage
- Cold start issues
- Limited control over execution environment

Coming soon.

---

## Monitoring

### What to watch

**Disk usage:**
```bash
du -sh /var/retrace/recordings
```

**Recording count:**
```bash
find /var/retrace/recordings -name trace.bin | wc -l
```

**Application metrics:**
- Response time (should increase by ~10-30% when recording)
- Error rates (should not change)
- CPU/memory (slight increase expected)

### Alerts

Set up alerts for:
- Disk usage > 80% on recording volume
- Recording overhead > 50% (suggests too much boundary crossing)
- Failed recordings (trace.bin not created)

---

## Troubleshooting

**Recording overhead too high (>50%)**
- Reduce sampling rate
- Profile which calls cross boundaries most often
- Consider recording only specific endpoints

**Disk filling up**
- Implement retention policy
- Reduce recording size by filtering unnecessary data
- Move to network storage

**Recordings incomplete or corrupted**
- Check disk space during recording
- Verify permissions on recording directory
- Look for application crashes during recording

**Can't reproduce issue in replay**
- Check if issue is time-dependent (clock skew, etc.)
- Verify all external dependencies were intercepted
- See [Troubleshooting guide](../troubleshooting.md)

---

## Security checklist

Before enabling in production:

- [ ] Review [Security Model](../security-model.md)
- [ ] Identify sensitive data that might be captured
- [ ] Implement retention policy
- [ ] Restrict access to recording storage
- [ ] Test in staging first
- [ ] Set up monitoring/alerts
- [ ] Document rollback procedure

---

## Next steps

- [Share recordings with your team](share-recording.md)
- [Deployment topologies](../deployment-topologies.md)
- [Troubleshooting](../troubleshooting.md)
```
