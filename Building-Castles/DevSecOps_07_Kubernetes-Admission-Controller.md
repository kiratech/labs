# Lab | Implement a Kubernetes Admission Controller using Trivy

1. This exercise is base upon the container [https://quay.io/repository/mmul/trivy-admission-webhook](https://quay.io/repository/mmul/trivy-admission-webhook)
   that has been created starting from [this article by Abhijeet Kasurde](https://medium.com/@AbhijeetKasurde/using-kubernetes-admission-controllers-1e5ba5cc30c0).
   Everything relies on Kubernetes [Dynamic Admission Control](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#webhook-configuration).

2. First we will create the initial yaml files for two basic elements: the
   webhook and its configuration.

   The webhook deployment will be in `trivy-admission-webhook.yaml`:

   ```yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: trivy-system
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     labels:
       app: trivy-admission-webhook
     name: trivy-admission-webhook
     namespace: trivy-system
   spec:
     replicas: 1
     selector:                                                                     
       matchLabels:                                                                
         app: trivy-admission-webhook
     template:
       metadata:
         labels:
           app: trivy-admission-webhook
       spec:
         containers:
           - image: quay.io/mmul/trivy-admission-webhook
             name: trivy-admission-webhook
             volumeMounts:
              - name: certs
                mountPath: "/certs"
                readOnly: true
         volumes:
           - name: certs
             secret:
               secretName: trivy-admission-webhook-certs
               optional: true
   ---
   apiVersion: v1
   kind: Service
   metadata:
     labels:
       app: trivy-admission-webhook
     name: trivy-admission-webhook
     namespace: trivy-system
   spec:
     ports:
       - name: 443-443
         port: 443
         protocol: TCP
         targetPort: 443
     selector:
       app: trivy-admission-webhook
   ```

   The webhook configuration will be in `taw-validating-webhook-configuration.yaml`:

   ```yaml
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingWebhookConfiguration
   metadata:
     name: "trivy-admission-webhook.trivy-system.svc"
   webhooks:
   - name: "trivy-admission-webhook.trivy-system.svc"
     rules:
     - apiGroups:   [""]
       apiVersions: ["v1"]
       operations:  ["CREATE"]
       resources:   ["pods"]
       scope:       "Namespaced"
     clientConfig:
       service:
         namespace: "trivy-system"
         name: "trivy-admission-webhook"
         path: /validate
         port: 443
     admissionReviewVersions: ["v1", "v1beta1"]
     sideEffects: None
     timeoutSeconds: 30
   ```

3. The service will rely on certificates, so we can use the one used by Kuberentes,
   downloading them from the server:

   ```console
   > scp kubernetes-1:ca* .
   Warning: Permanently added 'kubernetes-1' (ED25519) to the list of known hosts.
   ca.crt                                             100% 1099     1.4MB/s   00:00    
   ca.key                                             100% 1675     2.4MB/s   00:00
   ```

   We will then create the certificates for the webhook, using `openssl`:

   ```console
   > openssl genrsa -out taw-webhook.key 2048
   > servicename=trivy-admission-webhook.trivy-system.svc
   > openssl req -new -key taw-webhook.key -out taw-webhook.csr -subj "/CN=$servicename"
   > openssl x509 -req -extfile <(printf "subjectAltName=DNS:$servicename") -days 3650 -in taw-webhook.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out taw-webhook.crt
   Certificate request self-signature ok
   subject=CN = trivy-admission-webhook.trivy-system.svc
   ```

   And then we will store them inside Kubernetes, as a `secret`:

   ```console
   > kubectl -n trivy-system create secret tls trivy-admission-webhook-certs --key="taw-webhook.key" --cert="taw-webhook.crt"
   secret/trivy-admission-webhook-certs created
   ```

   With the secret in place, it is time to create the webhook deploynment:

   ```console
   > kubectl create -f trivy-admission-webhook.yaml
   deployment.apps/trivy-admission-webhook created
   ...
   
   rasca@catastrofe [~/Labs/trivy-wa]> kubectl -n trivy-system get all -l app=trivy-admission-webhook
   NAME                                           READY   STATUS    RESTARTS   AGE
   pod/trivy-admission-webhook-7c888d7d86-jsrhh   1/1     Running   0          73s
   
   NAME                              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
   service/trivy-admission-webhook   ClusterIP   10.111.238.91   <none>        443/TCP   18h
   
   NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
   deployment.apps/trivy-admission-webhook   1/1     1            1           73s
   
   NAME                                                 DESIRED   CURRENT   READY   AGE
   replicaset.apps/trivy-admission-webhook-7c888d7d86   1         1         1       73s
   ```

   And finally the webhook itself, patching the `validatingwebhookconfiguration`
   resource by adding the `ca.crt` certificate that has been used for the
   certificate generation:

   ```console
   > kubectl create -f taw-validating-webhook-configuration.yaml 
   validatingwebhookconfiguration.admissionregistration.k8s.io/trivy-admission-webhook.trivy-system.svc created
   
   > export CABUNDLE=$(cat ca.crt|base64 -w 0)

   > export JSONPATCH="{\"webhooks\":[{\"name\":\"trivy-admission-webhook.trivy-system.svc\", \"clientConfig\":{\"caBundle\":\"$CABUNDLE\"}}]}"

   > kubectl patch validatingwebhookconfigurations.admissionregistration.k8s.io trivy-admission-webhook.trivy-system.svc --patch="$JSONPATCH"
   ```

4. Doing effective tests is as simple as this:

   ```console
   rasca@catastrofe [~/Labs/trivy-wa]> kubectl -n myns create deployment nginx-latest --image public.ecr.aws/nginx/nginx:latest
   deployment.apps/nginx-latest created
   
   rasca@catastrofe [~/Labs/trivy-wa]> kubectl -n myns create deployment nginx-insecure --image public.ecr.aws/nginx/nginx:1.18
   deployment.apps/nginx-insecure created
   ```
   
   The two used images are different because one has CRITICAL vulnerabilities
   (`nginx:1.18`) and the `latest` not.
   So the events sequence will be:
   
   ```console
   rasca@catastrofe [~/Labs/trivy-wa]> kubectl -n myns get events --sort-by='.metadata.creationTimestamp' -A
   NAMESPACE      LAST SEEN   TYPE      REASON              OBJECT                                          MESSAGE
   ...
   ...
   myns           43s         Warning   FailedCreate        replicaset/nginx-insecure-79b595ff9b            Error creating: admission webhook "trivy-admission-webhook.trivy-system.svc" denied the request: Not all containers secure, failing ...
   myns           2m8s        Normal    ScalingReplicaSet   deployment/nginx-latest                         Scaled up replica set nginx-latest-785b998d5d to 1
   myns           2m5s        Normal    Pulling             pod/nginx-latest-785b998d5d-66tvk               Pulling image "public.ecr.aws/nginx/nginx:latest"
   myns           2m5s        Normal    Scheduled           pod/nginx-latest-785b998d5d-66tvk               Successfully assigned myns/nginx-latest-785b998d5d-66tvk to kubernetes-2
   myns           2m5s        Normal    SuccessfulCreate    replicaset/nginx-latest-785b998d5d              Created pod: nginx-latest-785b998d5d-66tvk
   myns           2m4s        Normal    Pulled              pod/nginx-latest-785b998d5d-66tvk               Successfully pulled image "public.ecr.aws/nginx/nginx:latest" in 831.767789ms (831.77442ms including waiting)
   myns           2m4s        Normal    Created             pod/nginx-latest-785b998d5d-66tvk               Created container nginx
   myns           2m4s        Normal    Started             pod/nginx-latest-785b998d5d-66tvk               Started container nginx
   ```

5. Bonus: doing everything in Minikube:

   ```console
   course@ubuntu-jammy:~$ openssl genrsa -out webhook.key 2048
   course@ubuntu-jammy:~$ servicename=trivy-admission-webhook.trivy-system.svc
   course@ubuntu-jammy:~$ openssl req -new -key webhook.key -out webhook.csr -subj "/CN=$servicename"
   course@ubuntu-jammy:~$ openssl x509 -req -extfile <(printf "subjectAltName=DNS:$servicename") -days 3650 -in webhook.csr -CA .minikube/ca.crt -CAkey .minikube/ca.key -CAcreateserial -out webhook.crt
   Certificate request self-signature ok
   subject=CN = trivy-admission-webhook.trivy-system.svc
   
   course@ubuntu-jammy:~$ kubectl create namespace trivy-system
   namespace/trivy-system created
   
   course@ubuntu-jammy:~$ kubectl -n trivy-system create secret tls trivy-admission-webhook-certs --key="webhook.key" --cert="webhook.crt"
   secret/trivy-admission-webhook-certs created
   
   course@ubuntu-jammy:~$ kubectl create -f trivy-admission-webhook.yaml
   deployment.apps/trivy-admission-webhook created
   service/trivy-admission-webhook created
   
   course@ubuntu-jammy:~$ kubectl -n trivy-system get all
   NAME                                           READY   STATUS    RESTARTS   AGE
   pod/trivy-admission-webhook-6d965d5c78-cwxnv   1/1     Running   0          13m
   
   NAME                              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
   service/trivy-admission-webhook   ClusterIP   10.98.90.165   <none>        443/TCP   20m
   
   NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
   deployment.apps/trivy-admission-webhook   1/1     1            1           20m
   
   NAME                                                 DESIRED   CURRENT   READY   AGE
   replicaset.apps/trivy-admission-webhook-6d965d5c78   1         1         1       20m
   
   course@ubuntu-jammy:~$ kubectl create -f webhook.yaml           
   
   course@ubuntu-jammy:~$ kubectl get ValidatingWebhookConfiguration trivy-admission-webhook.trivy-system.svc
   NAME                                       WEBHOOKS   AGE
   trivy-admission-webhook.trivy-system.svc   1          7m23s
   ```

   Same tests can be made:

   ```console
   course@ubuntu-jammy:~$ kubectl -n myns create deployment nginx-latest --image public.ecr.aws/nginx/nginx:latest
   deployment.apps/nginx-latest created
   
   course@ubuntu-jammy:~$ kubectl -n myns create deployment nginx-insecure --image public.ecr.aws/nginx/nginx:1.18
   deployment.apps/nginx-insecure created
   
   course@ubuntu-jammy:~$ kubectl -n myns get all
   NAME                                READY   STATUS    RESTARTS   AGE
   pod/nginx-latest-8586ccc94b-9slg8   1/1     Running   0          103s
   
   NAME                             READY   UP-TO-DATE   AVAILABLE   AGE
   deployment.apps/nginx-insecure   0/1     0            0           94s
   deployment.apps/nginx-latest     1/1     1            1           103s
   
   NAME                                        DESIRED   CURRENT   READY   AGE
   replicaset.apps/nginx-insecure-5785468788   1         0         0       94s
   replicaset.apps/nginx-latest-8586ccc94b     1         1         1       103s
   
   course@ubuntu-jammy:~$ kubectl -n myns get events --sort-by='.metadata.creationTimestamp' -A
   NAMESPACE      LAST SEEN   TYPE      REASON                    OBJECT                                          MESSAGE
   ...
   ...
   myns           25s         Normal    ScalingReplicaSet         deployment/nginx-latest                         Scaled up replica set nginx-latest-8586ccc94b to 1
   myns           23s         Normal    SuccessfulCreate          replicaset/nginx-latest-8586ccc94b              Created pod: nginx-latest-8586ccc94b-9slg8
   myns           23s         Normal    Scheduled                 pod/nginx-latest-8586ccc94b-9slg8               Successfully assigned myns/nginx-latest-8586ccc94b-9slg8 to minikube
   myns           22s         Normal    Pulling                   pod/nginx-latest-8586ccc94b-9slg8               Pulling image "nginx:latest"
   myns           21s         Normal    Started                   pod/nginx-latest-8586ccc94b-9slg8               Started container nginx
   myns           21s         Normal    Created                   pod/nginx-latest-8586ccc94b-9slg8               Created container nginx
   myns           21s         Normal    Pulled                    pod/nginx-latest-8586ccc94b-9slg8               Successfully pulled image "nginx:latest" in 1.291453932s (1.291487398s including waiting)
   myns           16s         Normal    ScalingReplicaSet         deployment/nginx-insecure                       Scaled up replica set nginx-insecure-5785468788 to 1
   myns           1s          Warning   FailedCreate              replicaset/nginx-insecure-5785468788            Error creating: admission webhook "trivy-admission-webhook.trivy-system.svc" denied the request: Not all containers secure, failing ...
   ```
