# Volumes, PV, PVC and StorageClass

How Kubernetes keeps data alive when Pods and containers come and go.

---

## Table of Contents

1. [The Problem](#the-problem)
2. [Volumes: volumes and volumeMounts](#volumes-volumes-and-volumemounts)
3. [emptyDir](#emptydir)
4. [PersistentVolume and PersistentVolumeClaim](#persistentvolume-and-persistentvolumeclaim)
5. [Static Provisioning: PV, PVC, Pod](#static-provisioning-pv-pvc-pod)
6. [Reading the Spec of a PV](#reading-the-spec-of-a-pv)
7. [Life Cycle and Reclaim Policy](#life-cycle-and-reclaim-policy)
8. [StorageClass and Dynamic Provisioning](#storageclass-and-dynamic-provisioning)
9. [Troubleshooting](#troubleshooting)
10. [Quick Reference](#quick-reference)

---

## The Problem

A container's own filesystem is temporary.

- Delete a Pod and its containers are removed, along with everything they wrote.
- Even when only a container restarts (for example after a crash), the new container starts fresh from the image.

You can see it yourself:

```bash
kubectl run data-test --image=busybox --command -- sleep 3600
kubectl exec data-test -- sh -c "echo hello > /tmp/note.txt"
kubectl delete pod data-test
kubectl run data-test --image=busybox --command -- sleep 3600
kubectl exec data-test -- cat /tmp/note.txt     # No such file or directory
```

Same name and same image, but a completely new Pod. For databases, uploads, or anything you must keep, the data has to live **outside** the container.

You already know the idea from Docker: a named volume or bind mount keeps the data outside the container, and removing the container leaves the data alone.

---

## Volumes: volumes and volumeMounts

Kubernetes splits the idea into two parts of the Pod YAML:

| Field | Where | Meaning |
|-------|-------|---------|
| `volumes:` | Pod level (`spec`) | Declares what storage exists and its type |
| `volumeMounts:` | Inside a container | Says where that storage appears in the container |

The two are linked by the volume's `name`.

```yaml
spec:
  containers:
    - name: app
      image: busybox
      volumeMounts:
        - name: data              # must match a volume name below
          mountPath: /data        # where it appears inside the container
  volumes:
    - name: data
      emptyDir: {}                # the type of volume
```

Think of `volumes` as the storage and `volumeMounts` as the window into it.

---

## emptyDir

An empty directory created when the Pod starts.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: data-test
spec:
  containers:
    - name: test
      image: busybox
      command: ['sh', '-c', 'echo run >> /data/log.txt; sleep 20; exit 1']
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      emptyDir: {}
```

This container deliberately exits after 20 seconds, so it restarts over and over. Every start appends a line, so after a few restarts `cat /data/log.txt` shows several `run` lines.

| Event | Data in emptyDir |
|-------|------------------|
| Container restarts (Pod stays) | **Survives** |
| Pod deleted or rescheduled | **Gone** |

`emptyDir` is good for scratch space, caches, and for sharing files between containers in one Pod. It is **not** good for a database.

> Note: you cannot reliably test a container restart with `kubectl exec ... kill 1`. Linux generally ignores signals sent to PID 1 from inside its own namespace. A container that exits by itself, as above, is a reliable test.

---

## PersistentVolume and PersistentVolumeClaim

To keep data beyond a Pod's life, storage must be its own object. Kubernetes uses two:

| Object | What it is | Analogy |
|--------|------------|---------|
| **PersistentVolume (PV)** | The actual storage (a disk, a directory, a cloud volume). Cluster-wide, no namespace. | The flat the landlord owns |
| **PersistentVolumeClaim (PVC)** | A request for storage ("I need 500Mi, read-write"). Created in a namespace. | The tenant's request |

The Pod never points at the disk directly. It points at the **claim**:

```
Pod → PVC (the request) → PV (the real storage) → disk
```

This also separates roles. The developer says what is needed (size, access mode), and the admin or the cloud decides where it comes from.

**Binding.** Kubernetes matches a claim to a PV that has:
- the same `storageClassName`
- compatible `accessModes`
- at least the requested size

A PV binds to **one claim as a whole**. If you ask for 500Mi and the matching PV has 1Gi, the claim shows 1Gi and the extra space cannot be used by another claim.

---

## Static Provisioning: PV, PVC, Pod

Here you create the PV by hand.

**1. PV**

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data
```

**2. PVC**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
  storageClassName: manual
```

**3. Pod using the claim**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pvc-test
  namespace: default
spec:
  containers:
    - name: test
      image: busybox
      command: ['sh', '-c', 'echo "hello from persistent storage" >> /data/log.txt; sleep 3600']
      volumeMounts:
        - name: storage
          mountPath: /data
  volumes:
    - name: storage
      persistentVolumeClaim:
        claimName: my-pvc
```

Test it:

```bash
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl get pv,pvc                              # both Bound
kubectl apply -f pvc-test.yaml
kubectl exec pvc-test -- cat /data/log.txt      # 1 line
kubectl delete pod pvc-test
kubectl apply -f pvc-test.yaml
kubectl exec pvc-test -- cat /data/log.txt      # 2 lines, the data survived
```

Only the Pod was deleted, and the storage is its own object, so the data is still there.

---

## Reading the Spec of a PV

```yaml
  capacity:
    storage: 1Gi
```
How big the volume is. `Gi` (gibibyte, powers of 1024) is not the same as `G`.

```yaml
  accessModes:
    - ReadWriteOnce
```
How the volume can be mounted. It is a list.

| Mode | Short | Meaning |
|------|-------|---------|
| `ReadWriteOnce` | RWO | Read-write by Pods on **one node** |
| `ReadOnlyMany` | ROX | Read-only by many nodes |
| `ReadWriteMany` | RWX | Read-write by many nodes |
| `ReadWriteOncePod` | RWOP | Read-write by exactly **one Pod** |

```yaml
  persistentVolumeReclaimPolicy: Retain
```
What happens to the PV after its PVC is deleted (next section).

```yaml
  storageClassName: manual
```
A label used for matching. A PVC binds only to a PV with the same class name. `manual` is just our name for "created by hand".

```yaml
  hostPath:
    path: /mnt/data
```
Where the storage physically is: a directory on the **node**. In Minikube the node is the Minikube container, so you can check the file with `minikube ssh` and `cat /mnt/data/log.txt`. `hostPath` is for local learning only. A Pod rescheduled to another node would not find it. Real clusters use cloud disks or network storage.

---

## Life Cycle and Reclaim Policy

PV status values you will see:

| Status | Meaning |
|--------|---------|
| `Available` | Free, not bound to any claim |
| `Bound` | Attached to a PVC |
| `Released` | The PVC was deleted, but the PV has not been reclaimed yet |

The **reclaim policy** is a setting on the PV that says what Kubernetes does with the storage after the PVC that used it is deleted.

| Policy | What happens |
|--------|--------------|
| `Retain` | The PV and its data stay (status `Released`). An admin must clean up before reuse. |
| `Delete` | The PV **and the real storage** are deleted with the claim. The data is gone. |
| `Recycle` | Deprecated. Ignore it. |

**Use `Delete`** for temporary or easily recreated data (caches, test environments).
**Use `Retain`** for data you cannot lose (production databases).

Change it on an existing PV:

```bash
kubectl patch pv <pv-name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
```

### Reusing a Released PV

With `Retain`, deleting the PVC leaves the PV `Released`, and its `CLAIM` column still shows the old claim. If you create a new PVC with the same name, it stays `Pending`, because the PV's `claimRef` records the old claim's **unique ID**, and the new claim has a different one. Kubernetes will not hand over a PV that still holds a previous owner's data automatically.

Clear the stale reference:

```bash
kubectl edit pv my-pv        # delete the whole claimRef: block
# or in one line:
kubectl patch pv my-pv --type=json -p='[{"op":"remove","path":"/spec/claimRef"}]'
```

The PV goes back to `Available`, and the pending claim binds within a minute.

> Careful: once the PV is `Available`, do not delete and recreate the PVC again. Each delete of a bound claim returns the PV to `Released`, with a new stale `claimRef`.

---

## StorageClass and Dynamic Provisioning

Nobody writes PVs by hand in real clusters. A **StorageClass** describes a kind of storage, and when a PVC asks for it, the cluster **creates the PV automatically**.

```bash
kubectl get storageclass
```

```
NAME                 PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE
standard (default)   k8s.io/minikube-hostpath   Delete          Immediate
```

| Column | Meaning |
|--------|---------|
| `(default)` | Used when a PVC names no class |
| `PROVISIONER` | The component that creates the PVs (in the cloud: AWS EBS, GCE PD and so on) |
| `RECLAIMPOLICY` | The policy given to PVs this class creates |
| `VOLUMEBINDINGMODE` | `Immediate` binds as soon as the claim exists. `WaitForFirstConsumer` waits until a Pod uses it. |

A PVC without `storageClassName`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: auto-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 200Mi
```

```bash
kubectl apply -f auto-pvc.yaml
kubectl get pv,pvc
```

Within seconds a new PV appears (named `pvc-<uid>`), sized exactly **200Mi**, class `standard`, reclaim policy `Delete`, already `Bound`. Delete the PVC and the PV disappears with it.

| | Static (`my-pv`) | Dynamic |
|---|---|---|
| Who creates the PV | You | The StorageClass |
| Size | Whatever the PV has (the claim gets all of it) | Exactly what was requested |
| Default reclaim policy | What you set | From the class (usually `Delete`) |

---

## Troubleshooting

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| `exec` says "pod does not have a host assigned" | The Pod is `Pending`, often because its PVC is not bound | `kubectl get pv,pvc`, then `kubectl describe pod <pod>` and read `Events:` |
| PVC stuck in `Pending` | No PV matches (class, access mode or size), or a Released PV still has a stale `claimRef` | Compare PV and PVC fields; clear `claimRef` if the PV is `Released` |
| Data disappeared after deleting a PVC | Reclaim policy was `Delete` | Set `Retain` **before** deleting claims you care about |
| Data missing after a Pod restart | Used `emptyDir` instead of a PVC | Use a PVC for data that must survive |

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `kubectl get pv,pvc` | Check storage objects and their status |
| `kubectl describe pvc <name>` | Why a claim is Pending (see `Events:`) |
| `kubectl get storageclass` | List classes and the default |
| `kubectl patch pv <name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'` | Protect a PV's data |
| `kubectl patch pv <name> --type=json -p='[{"op":"remove","path":"/spec/claimRef"}]'` | Make a Released PV Available again |
| `kubectl explain pv.spec` | Look up fields (allowed in practice) |

---

## Summary

```
emptyDir  → lives and dies with the Pod; survives container restarts
PV        → the real storage, its own object, cluster-wide
PVC       → a request for storage; the Pod points at this
Bind      → class + access mode + size match; the claim gets the whole PV
Retain    → PV and data stay after the PVC is deleted
Delete    → PV and data go with the PVC
StorageClass → creates PVs automatically (dynamic provisioning)
```
