# Kubernetes Pod replacement lab

This optional lab runs the same Flask app under Kubernetes. A Deployment requests two application replicas; its ReplicaSet creates replacements when Pods are deleted. The database also uses a Deployment with one replica and a persistent volume claim. The cluster and its controllers must be running and have sufficient resources.

Downloading the ZIP alone does not enable self-healing. Deploy this Kubernetes configuration first. Docker Compose remains a separate exercise and does not recreate deliberately deleted containers.

## 1 Prepare Minikube inside Ubuntu

Use the existing Ubuntu amd64 VM with Docker installed. Suggested VM allocation for this extension: 4 vCPUs, 6 GB RAM and 30 GB disk, with at least 4 GB available for Minikube. Stop the Compose stack if resources are tight; omit `-v` to retain its database:

```bash
docker compose -f compose.yaml -f compose.lb.yaml down
```

Install Minikube if it is not installed (internet required):

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version
minikube start -p campus-workshop --driver=docker --cpus=2 --memory=4096
```

Run Minikube as your regular Docker-enabled Ubuntu user, not root. The Docker driver does not require nested virtualization. A separate kubectl installation is optional; this lab uses Minikube's bundled client. The first start downloads cluster components.

In each terminal define:

```bash
k() { minikube -p campus-workshop kubectl -- "$@"; }
k get nodes
k get storageclass
```

Minikube normally enables its default storage provisioner. If no default StorageClass exists, enable `storage-provisioner` and `default-storageclass` with `minikube -p campus-workshop addons enable ADDON_NAME`, then check again.

## 2 Deploy from the downloaded project folder

```bash
bash scripts/deploy-kubernetes.sh
```

This builds and loads the application image into the named cluster, applies the YAML, and waits for the database and application. No published GHCR application image is needed. PostgreSQL is pulled from its public registry. The demo Secret contains intentionally public lab credentials; it is not suitable for production. Compose .env settings are not used here; change kubernetes/01-config.yaml instead.

The equivalent manual steps are:

```bash
docker build -t campus-feedback:k8s-v1 .
minikube -p campus-workshop image load campus-feedback:k8s-v1
k apply -f kubernetes/00-namespace.yaml
k apply -f kubernetes/01-config.yaml
k apply -f kubernetes/02-database.yaml
k -n campus-workshop rollout status deployment/campus-db --timeout=180s
k apply -f kubernetes/03-application.yaml
k -n campus-workshop rollout status deployment/campus-app --timeout=180s
k -n campus-workshop get pods,svc,pvc
```

Expect two Ready application Pods, one Ready database Pod and a Bound PVC. This is a new database; existing Compose feedback is not migrated.

## 3 Open the application

```bash
minikube -p campus-workshop service campus-app -n campus-workshop --url
```

Open the printed URL **inside the Ubuntu VM**. Leave the command running if it establishes a tunnel. The Kubernetes Service provides access to Ready application replicas; this lab does not deploy NGINX. A persistent connection need not alternate between Pods.

Alternative for browser access only:

```bash
k -n campus-workshop port-forward service/campus-app 8082:80
```

Open http://localhost:8082 inside Ubuntu. Port-forward selects one Pod and can stop if that Pod is deleted; rerun it after replacement. Use the Minikube Service URL for the deletion demonstration.

## 4 Delete one application Pod

Terminal 1:

```bash
k -n campus-workshop get pods -l app=campus-app -w
```

Terminal 2, after defining the k function there too:

```bash
pod=$(k -n campus-workshop get pods -l app=campus-app -o jsonpath='{.items[0].metadata.name}')
k -n campus-workshop delete pod "$pod"
```

Watch a new Pod name appear and become Ready. The desired count remains two. Requests in flight may fail; this is not a zero-downtime guarantee. Ctrl+C stops the watch without affecting Pods.

For an automated check that compares Pod UIDs and waits for readiness:

```bash
bash scripts/verify-self-healing.sh
```

The script deliberately deletes one application Pod. Delete the Pod, **not the Deployment or namespace**. Deleting the Deployment removes the controller that maintains the replicas. A container crash usually causes a restart inside its existing Pod; deleting a Pod creates a new Pod with a new UID.

## 5 Verify database persistence

Submit a distinctive feedback entry, then inspect it:

```bash
k -n campus-workshop exec deployment/campus-db -- psql -U campus -d campus -c 'SELECT * FROM feedback ORDER BY id DESC LIMIT 10;'
```

Optional: delete the database Pod by its name from `k -n campus-workshop get pods`. It will be replaced and reuse the same PVC. There is an outage while the single database replica recovers. Wait for database and app readiness and query the same record again. Do not delete the PVC. This is local storage on one Minikube node, not protection against node/disk loss.

## 6 Manual scaling and troubleshooting

```bash
k -n campus-workshop scale deployment campus-app --replicas=3
k -n campus-workshop get pods -l app=campus-app
k -n campus-workshop scale deployment campus-app --replicas=2
k -n campus-workshop get events --sort-by=.metadata.creationTimestamp
k -n campus-workshop logs deployment/campus-app --tail=50
k -n campus-workshop describe pods -l app=campus-app
```

Pending: inspect resources and PVC binding. ImagePullBackOff: confirm the image was loaded into the campus-workshop profile. Not Ready: inspect PostgreSQL logs and credentials. Reapplying the app YAML resets replicas to two. This extension provides self-healing and manual scaling; load-based autoscaling is not configured.

After rebuilding an existing image tag and loading it again, run `k -n campus-workshop rollout restart deployment/campus-app` to replace existing app Pods. Changing ConfigMap or Secret environment values also requires a rollout restart. Changing PostgreSQL credentials does not change credentials already stored in an existing database volume.

## Stop and cleanup

`minikube stop -p campus-workshop` stops the lab while retaining its cluster data. Start the same profile to resume. Deleting the namespace/PVC or running `minikube delete -p campus-workshop` can destroy database data; these are not routine stop commands.

## Verification status and references

YAML structure, selectors, schema consistency and shell syntax are checked during preparation. The authoring environment has no Docker or Kubernetes runtime, so a live cluster deletion test must be run with the supplied verification script on the Ubuntu VM before teaching.

- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- https://minikube.sigs.k8s.io/docs/start/
- https://minikube.sigs.k8s.io/docs/handbook/pushing/
