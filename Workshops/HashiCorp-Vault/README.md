# HashiCorp Vault Workshop

This workshop is based on these public resources:

- [Vault on Kubernetes deployment guide](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-raft-deployment-guide)
- [Injecting secrets into Kubernetes pods via Vault Agent containers](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-sidecar#inject-secrets-into-the-pod)

and will install Vault inside an existing Kubernete cluster.

TBD: extend also with the [Kubernetes using an External Vault](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-external-vault).

## Kubernetes installation

TBD: extend Kind installation.

```console
$ kind create cluster --name hcp-vault-test
Creating cluster "hcp-vault-test" ...
 ✓ Ensuring node image (kindest/node:v1.29.2) 🖼
 ✓ Preparing nodes 📦  
 ✓ Writing configuration 📜 
 ✓ Starting control-plane 🕹️ 
 ✓ Installing CNI 🔌 
 ✓ Installing StorageClass 💾 
Set kubectl context to "kind-hcp-vault-test"
You can now use your cluster with:

kubectl cluster-info --context kind-hcp-vault-test

Have a question, bug, or feature request? Let us know! https://kind.sigs.k8s.io/#community 🙂

$ kubectl get nodes
NAME                           STATUS   ROLES           AGE   VERSION
hcp-vault-test-control-plane   Ready    control-plane   68s   v1.29.
```

## Install Vault

```console
$ kubectl create namespace vault
namespace/vault created

$ helm repo add hashicorp https://helm.releases.hashicorp.com

$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "hashicorp" chart repository
Update Complete. ⎈Happy Helming!⎈

$ helm search repo hashicorp/vault
NAME                            	CHART VERSION	APP VERSION	DESCRIPTION                          
hashicorp/vault                 	0.28.0       	1.16.1     	Official HashiCorp Vault Chart       
hashicorp/vault-secrets-operator	0.5.2        	0.5.2      	Official Vault Secrets Operator Chart

$ helm install vault hashicorp/vault --namespace vault
NAME: vault
LAST DEPLOYED: Fri Apr 19 16:04:51 2024
NAMESPACE: vault
STATUS: deployed
REVISION: 1
NOTES:
Thank you for installing HashiCorp Vault!

Now that you have deployed Vault, you should look over the docs on using
Vault with Kubernetes available here:

https://developer.hashicorp.com/vault/docs


Your release is named vault. To learn more about the release, try:

  $ helm status vault
  $ helm get manifest vault

$ kubectl -n vault get all
NAME                                        READY   STATUS              RESTARTS   AGE
pod/vault-0                                 0/1     ContainerCreating   0          14s
pod/vault-agent-injector-8497dd4457-rsqlb   1/1     Running             0          14s

NAME                               TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
service/vault                      ClusterIP   10.96.188.11   <none>        8200/TCP,8201/TCP   14s
service/vault-agent-injector-svc   ClusterIP   10.96.28.216   <none>        443/TCP             14s
service/vault-internal             ClusterIP   None           <none>        8200/TCP,8201/TCP   14s

NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/vault-agent-injector   1/1     1            1           14s

NAME                                              DESIRED   CURRENT   READY   AGE
replicaset.apps/vault-agent-injector-8497dd4457   1         1         1       14s

NAME                     READY   AGE
statefulset.apps/vault   0/1     14s
```

## Initialize Vault

Vault needs to be initialized (from inside its container):

```console
$ kubectl -n vault exec --stdin=true --tty=true vault-0 -- vault operator init
Unseal Key 1: MCrlmsOrN8OZ/Vap5LdlZYWnMts0aoY1Fbe33zaAa81u
Unseal Key 2: MQvupyVmFOYhgm4OgiTg7eNoWB3l5Kr5IpD+/lnjwig2
Unseal Key 3: MlOPVhKgLUaBcao9y+6TJewmjE5c0PDJNnlqElP5wWZI
Unseal Key 4: cpU13edvVKOKXzyFyBgO7OVNzgP7irhmu85ltifAyR/G
Unseal Key 5: ApoiCM/UP1jTrX5ClCtI06+jIIB/OP1DL1AiMPZOUo12

Initial Root Token: hvs.GXFHQwN3uz4AQdHBiFWbRhqB

Vault initialized with 5 key shares and a key threshold of 3. Please securely
distribute the key shares printed above. When the Vault is re-sealed,
restarted, or stopped, you must supply at least 3 of these keys to unseal it
before it can start servicing requests.

Vault does not store the generated root key. Without at least 3 keys to
reconstruct the root key, Vault will remain permanently sealed!

It is possible to generate new unseal keys, provided you have a quorum of
existing unseal keys shares. See "vault operator rekey" for more information.
```

**These keys are critical to both the security and the operation of Vault and
should be treated as per your company's sensitive data policy.**

## Unseal

The unsealing process in HashiCorp Vault is a critical step in initializing and
activating a Vault instance. When Vault starts up, it's in a sealed state,
meaning it's not yet accessible and its cryptographic keys are not fully
initialized.

Unsealing is the process of providing Vault with the necessary keys to decrypt
the master key and make the Vault operational.

In practice these steps are necessary to move the Vault pod to ready:

```console
$ kubectl -n vault exec --stdin=true --tty=true vault-0 -- vault operator unseal
Unseal Key (will be hidden): 
Key                Value
---                -----
Seal Type          shamir
Initialized        true
Sealed             true
Total Shares       5
Threshold          3
Unseal Progress    1/3
Unseal Nonce       2ad2ef78-b8d6-2605-611f-e7ed384ec156
Version            1.16.1
Build Date         2024-04-03T12:35:53Z
Storage Type       file
HA Enabled         false

$ kubectl get pods --selector='app.kubernetes.io/name=vault' --namespace='vault'
NAME      READY   STATUS    RESTARTS   AGE
vault-0   0/1     Running   0          3m55s

$ kubectl -n vault exec --stdin=true --tty=true vault-0 -- vault operator unseal
Unseal Key (will be hidden): 
Key                Value
---                -----
Seal Type          shamir
Initialized        true
Sealed             true
Total Shares       5
Threshold          3
Unseal Progress    2/3
Unseal Nonce       2ad2ef78-b8d6-2605-611f-e7ed384ec156
Version            1.16.1
Build Date         2024-04-03T12:35:53Z
Storage Type       file
HA Enabled         false

$ kubectl get pods --selector='app.kubernetes.io/name=vault' --namespace='vault'
NAME      READY   STATUS    RESTARTS   AGE
vault-0   0/1     Running   0          3m55s

$ kubectl -n vault exec --stdin=true --tty=true vault-0 -- vault operator unseal
Unseal Key (will be hidden): 
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    5
Threshold       3
Version         1.16.1
Build Date      2024-04-03T12:35:53Z
Storage Type    file
Cluster Name    vault-cluster-dc48e82c
Cluster ID      e3134e0d-a2c0-915b-4696-da35f5c6f3da
HA Enabled      false

$ kubectl get pods --selector='app.kubernetes.io/name=vault' --namespace='vault'
NAME      READY   STATUS    RESTARTS   AGE
vault-0   1/1     Running   0          4m33s
```

### Test 1: inject secrets in a txt file

Enable Kubernetes secrets engine in Vault:

```console
$ kubectl -n vault exec -it vault-0 -- /bin/sh
/ $ vault login
Token (will be hidden): 
Success! You are now authenticated. The token information displayed below
is already stored in the token helper. You do NOT need to run "vault login"
again. Future Vault requests will automatically use this token.

Key                  Value
---                  -----
token                hvs.GXFHQwN3uz4AQdHBiFWbRhqB
token_accessor       vpNnzX35Fxw2TcPGitbArXMd
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]

/ $ vault secrets enable -path=internal kv-v2
Success! Enabled the kv-v2 secrets engine at: internal/
```

Create a sample key inside Vault under `internal/database/config`:

```console
/ $ vault kv put internal/database/config username="myuser" password="mysupersecretpassword"
======== Secret Path ========
internal/data/database/config

======= Metadata =======
Key                Value
---                -----
created_time       2024-04-19T15:25:58.893363499Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1

/ $ exit
```

Configure Vault to authenticate Kubernetes and enable read for the policy 
named `internal-policy` associated with the service account `internal-app`:

```console
$ kubectl -n vault exec -it vault-0 -- /bin/sh
/ $  vault auth enable kubernetes
Success! Enabled kubernetes auth method at: kubernetes/

/ $ echo $KUBERNETES_PORT_443_TCP_ADDR
10.96.0.1

/ $ vault write auth/kubernetes/config kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"
Success! Data written to: auth/kubernetes/config

/ $ vault policy write internal-app - <<EOF
> path "internal/data/database/config" {
>    capabilities = ["read"]
> }
> EOF
Success! Uploaded policy: internal-app

/ $ vault write auth/kubernetes/role/internal-app \
>       bound_service_account_names=internal-app \
>       bound_service_account_namespaces=default \
>       policies=internal-app \
>       ttl=24h
Success! Data written to: auth/kubernetes/role/internal-app

/ $ exit
```

Create the service account in the `default` Kubernetes namespace:

```console
$ kubectl create sa internal-app
serviceaccount/internal-app created
```

Create a deployment (check [deployment-orgchart.yaml](deployment-orgchart.yaml)):

```console
$ cat <<EOF > deployment-orgchart.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orgchart
  labels:
    app: orgchart
spec:
  selector:
    matchLabels:
      app: orgchart
  replicas: 1
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: 'true'
        vault.hashicorp.com/role: 'internal-app'
        vault.hashicorp.com/agent-inject-secret-database-config.txt: 'internal/data/database/config'
      labels:
        app: orgchart
    spec:
      serviceAccountName: internal-app
      containers:
      - name: orgchart
        image: jweissig/app:0.0.1
EOF

$ kubectl create -f deployment-orgchart.yaml 
deployment.apps/orgchart created

$ kubectl get pods
NAME                        READY   STATUS    RESTARTS   AGE
orgchart-7467ffbb9f-swq85   1/1     Running   0          18s

$ kubectl exec orgchart-7467ffbb9f-swq85 -- cat /vault/secrets/database-config.txt
data: map[password:mysupersecretpassword username:myuser]
metadata: map[created_time:2024-04-19T15:25:58.893363499Z custom_metadata:<nil> deletion_time: destroyed:false version:1]
```

### Test 2: use secrets as environment variables

Create a new deployment (check [deployment-bash-env.yaml](deployment-bash-env.yaml)):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: index-php
  labels:
    app: webserver
data:
  index.php: |
    Application info:<br />
    USERNAME: <b><?=getenv('USERNAME', true);?></b><br />
    PASSWORD: <b><?=getenv('PASSWORD', true);?></b><br />
    Node name: <b><?=getenv('NODE_NAME', true);?></b><br />
    Node IP: <b><?=getenv('NODE_IP', true);?></b><br />
    Pod namespace: <b><?=getenv('POD_NAMESPACE', true);?></b><br />
    Pod name: <b><?=getenv('POD_NAME', true);?></b><br />
    Pod IP: <b><?=getenv('POD_IP', true);?></b><br />
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webserver
  labels:
    app: webserver
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webserver
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: 'true'
        vault.hashicorp.com/role: 'internal-app'
        vault.hashicorp.com/agent-inject-template-config: |
          {{ with secret "internal/data/database/config" -}}
          export USERNAME="{{ .Data.data.username }}"
          export PASSWORD="{{ .Data.data.password }}"
          {{- end }}
      labels:
        app: webserver
    spec:
      serviceAccountName: internal-app
      containers:
      - name: webserver
        image: php:apache
        env:
        - name: BASH_ENV
          value: /vault/secrets/config
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: NODE_IP
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        volumeMounts:
        - name: docroot
          mountPath: /var/www/html
      volumes:
      - name: docroot
        configMap:
          name: index-php
---
apiVersion: v1
kind: Service
metadata:
  name: webserver
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: webserver
```

Create it:

```console
$ kubectl apply -f deployment.yaml 
configmap/index-php configured
deployment.apps/webserver configured
service/webserver configured
```

And test:

```console
$ kubectl port-forward webserver-7bdf868887-b94m8 8080:80
Forwarding from 127.0.0.1:8080 -> 80
Forwarding from [::1]:8080 -> 80
```

On another console:

```console
$ lynx -dump localhost:8080
   Application info:
   USERNAME: myuser
   PASSWORD: mysupersecretpassword
   Node name: hcp-vault-test-control-plane
   Node IP: 172.18.0.2
   Pod namespace: default
   Pod name: webserver-7bdf868887-b94m8
   Pod IP: 10.244.0.14

$ kubectl exec webserver-7bdf868887-b94m8 -c webserver -it -- /bin/bash
root@webserver-7bdf868887-b94m8:/var/www/html#

root@webserver-7bdf868887-b94m8:/var/www/html# source /vault/secrets/config
(no output)

root@webserver-7bdf868887-b94m8:/var/www/html# env | egrep 'USERNAME|PASSWORD'
USERNAME=myuser
PASSWORD=mysupersecretpassword
```

## Using Vault Kubernetes Opertator

The Vault Operator that will point to the local Vault instance by using a
specific values file (check [vault-operator-values.yaml](vault-operator-values.yaml)):

```console
defaultVaultConnection:
  enabled: true
  address: "http://vault.vault.svc.cluster.local:8200"
  skipTLSVerify: false
```

And will be installed using `helm`:

```console
$ helm install vault-secrets-operator hashicorp/vault-secrets-operator -n vault-secrets-operator-system --create-namespace --values vault-operator-values.yaml
NAME: vault-secrets-operator
LAST DEPLOYED: Tue Apr 30 16:23:55 2024
NAMESPACE: vault-secrets-operator-system
STATUS: deployed
REVISION: 1

$ kubectl -n vault-secrets-operator-system get all
NAME                                                             READY   STATUS    RESTARTS   AGE
pod/vault-secrets-operator-controller-manager-7c689d54b4-sfr5b   2/2     Running   0          6m6s

NAME                                             TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
service/vault-secrets-operator-metrics-service   ClusterIP   10.96.58.5   <none>        8443/TCP   6m6s

NAME                                                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/vault-secrets-operator-controller-manager   1/1     1            1           6m6s

NAME                                                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/vault-secrets-operator-controller-manager-7c689d54b4   1         1         1       6m6s
```

The first thing to be created will be the Custom Resource `VaultAuth` element:

```console
$ cat <<EOF | kubectl apply -f -
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultAuth
metadata:
  name: static-auth
spec:
  method: kubernetes
  mount: kubernetes
  kubernetes:
    role: internal-app
    serviceAccount: internal-app
    audiences:
      - vault
EOF
vaultauth.secrets.hashicorp.com/static-auth created
```

This will activate the link between the `serviceAccount` and the Vault service.
Then to create the effective secret a `VaultStaticSecret` Custom Resource
containing all the Vault's secret specifics should be created as well:

```console
$ cat <<EOF | kubectl apply -f -
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultStaticSecret
metadata:
  name: vault-kv-app
spec:           
  type: kv-v2
  # mount path
  mount: internal
  # path of the secret
  path: database/config
  # dest k8s secret
  destination:
    name: secretkv
    create: true
  # static secret refresh interval
  refreshAfter: 30s
  # Name of the CRD to authenticate to Vault
  vaultAuthRef: static-auth
EOF                        
vaultstaticsecret.secrets.hashicorp.com/vault-kv-app created
```

This will lead to the secret creation:

```console
$ kubectl get secret secretkv
NAME       TYPE     DATA   AGE
secretkv   Opaque   3      40s

$ kubectl get secret secretkv -o yaml
apiVersion: v1
data:
  _raw: eyJkYXRhIjp7InBhc3N3b3JkIjoibXlzdXBlcnNlY3JldHBhc3N3b3JkIiwidXNlcm5hbWUiOiJteXVzZXIifSwibWV0YWRhdGEiOnsiY3JlYXRlZF90aW1lIjoiMjAyNC0wNC0xOVQxNToyNTo1OC44OTMzNjM0OTlaIiwiY3VzdG9tX21ldGFkYXRhIjpudWxsLCJkZWxldGlvbl90aW1lIjoiIiwiZGVzdHJveWVkIjpmYWxzZSwidmVyc2lvbiI6MX19
  password: bXlzdXBlcnNlY3JldHBhc3N3b3Jk
  username: bXl1c2Vy
kind: Secret
metadata:
  creationTimestamp: "2024-04-30T15:01:08Z"
  labels:
    app.kubernetes.io/component: secret-sync
    app.kubernetes.io/managed-by: hashicorp-vso
    app.kubernetes.io/name: vault-secrets-operator
    secrets.hashicorp.com/vso-ownerRefUID: 62ead748-9085-4aae-bd2e-9830f3bf07b8
  name: secretkv
  namespace: default
  ownerReferences:
  - apiVersion: secrets.hashicorp.com/v1beta1
    kind: VaultStaticSecret
    name: vault-kv-app
    uid: 62ead748-9085-4aae-bd2e-9830f3bf07b8
  resourceVersion: "83311"
  uid: 5ad098af-5682-4985-9766-323eb8818ae8
type: Opaque
```

The secret will be usable by a deployment (check [deployment-secret.yaml](deployment-secret.yaml)):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webserver-secret
  labels:
    app: webserver-secret
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webserver-secret
  template:
    metadata:
      labels:
        app: webserver-secret
    spec:
      serviceAccountName: internal-app
      containers:
      - name: webserver-secret
        image: php:apache
        envFrom:
        - secretRef:
            name: secretkv
        env:
        - name: USERNAME
          valueFrom:
            secretKeyRef:
              name: secretkv
              key: username
        - name: PASSWORD
          valueFrom:
            secretKeyRef:
              name: secretkv
              key: password
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: NODE_IP
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        volumeMounts:
        - name: docroot
          mountPath: /var/www/html
      volumes:
      - name: docroot
        configMap:
          name: index-php
      - name: secretkv
        secret:
          secretName: secretkv
---
apiVersion: v1
kind: Service
metadata:
  name: webserver-secret
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: webserver-secret
```

That will be created:

```console
$ kubectl create -f deployment-secret.yaml 
deployment.apps/webserver-secret created
service/webserver-secret created

$ kubectl port-forward webserver-secret-857666696c-p2g7b 8080:80
Forwarding from 127.0.0.1:8080 -> 80
Forwarding from [::1]:8080 -> 80
```

And tested:

```console
$  lynx -dump localhost:8080
   Application info:
   USERNAME: myuser
   PASSWORD: mysupersecretpassword
   Node name: hcp-vault-test-control-plane
   Node IP: 172.18.0.2
   Pod namespace: default
   Pod name: webserver-secret-857666696c-p2g7b
   Pod IP: 10.244.0.11
```
