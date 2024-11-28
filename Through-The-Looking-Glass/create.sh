#!/bin/bash

CTLP="ctlplane"
TEST="test"
PROD="prod"

cat <<EOF > kind-${CTLP}-config.yml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  apiServerAddress: "172.18.0.1"
  apiServerPort: 6443
nodes:
- role: control-plane
  image: kindest/node:v1.31.0
EOF

cat <<EOF > kind-${TEST}-config.yml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  apiServerAddress: "172.18.0.1"
  apiServerPort: 7443
nodes:
- role: control-plane
  image: kindest/node:v1.31.0
EOF

cat <<EOF > kind-${PROD}-config.yml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  apiServerAddress: "172.18.0.1"
  apiServerPort: 8443
nodes:
- role: control-plane
  image: kindest/node:v1.31.0
EOF

for K8S in ${CTLP} ${TEST} ${PROD}; do
  kind create cluster --name ${K8S} --config kind-${K8S}-config.yml
done

export METALLB_VERSION='v0.14.8'
for K8S in ${CTLP} ${TEST} ${PROD}; do
  kubectl config use-context kind-${K8S}
  kubectl get configmap kube-proxy -n kube-system -o yaml | sed -e "s/strictARP: false/strictARP: true/" | kubectl apply -f - -n kube-system
  kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/${METALLB_VERSION}/config/manifests/metallb-native.yaml
  kubectl wait --namespace metallb-system --for=condition=ready pod --selector=app=metallb --timeout=90s
done

cat <<EOF > kind-${CTLP}-metallb-pools.yml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: mypool
  namespace: metallb-system
spec:
  addresses:
  - 172.18.0.100-172.18.0.110
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: mypool
  namespace: metallb-system
spec:
  ipAddressPools:
  - mypool
EOF

cat <<EOF > kind-${TEST}-metallb-pools.yml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: mypool
  namespace: metallb-system
spec:
  addresses:
  - 172.18.0.120-172.18.0.130
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: mypool
  namespace: metallb-system
spec:
  ipAddressPools:
  - mypool
EOF

cat <<EOF > kind-${PROD}-metallb-pools.yml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: mypool
  namespace: metallb-system
spec:
  addresses:
  - 172.18.0.140-172.18.0.150
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: mypool
  namespace: metallb-system
spec:
  ipAddressPools:
  - mypool
EOF

for K8S in ${CTLP} ${TEST} ${PROD}; do
  kubectl config use-context kind-${K8S}
  kubectl apply -f kind-${K8S}-metallb-pools.yml
done

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update


# PROMETHEUS
cat <<EOF > helm-prometheus-override.yml
grafana:
  enabled: false

alertmanager:
  enabled: false
EOF

for K8S in ${TEST} ${PROD}; do
  kubectl config use-context kind-${K8S}
  # Install
  helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace --values helm-prometheus-override.yml
  kubectl -n monitoring expose service prometheus-kube-prometheus-prometheus --name=prometheus-kube-prometheus-prometheus-lb --type=LoadBalancer
  eval "PROMETHEUS_${K8S}=$(kubectl -n monitoring get svc prometheus-kube-prometheus-prometheus-lb -o jsonpath='{.status.loadBalancer.ingress[0].ip}:{.spec.ports[0].port}')"
done

# FEDERATION
# https://stackoverflow.com/questions/64918491/prometheus-for-k8s-multi-clusters
# https://prometheus.io/docs/prometheus/latest/federation/#configuring-federation
cat <<EOF> helm-prometheus-${CTLP}.yml
grafana:
  enabled: false

alertmanager:
  enabled: false

prometheus:
  prometheusSpec:
    additionalScrapeConfigs:
      - job_name: 'federate'
        scrape_interval: 15s
      
        honor_labels: true
        metrics_path: '/federate'
      
        params:
          'match[]':
            - '{job="prometheus"}'
            - '{__name__=~"job:.*"}'
      
        static_configs:
          - targets:
            - '$(eval "echo \${PROMETHEUS_${TEST}}")'
            - '$(eval "echo \${PROMETHEUS_${PROD}}")'
EOF

kubectl config use-context kind-${CTLP}
# PROMETHEUS
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace --values helm-prometheus-ctlplane.yml
kubectl -n monitoring expose service prometheus-kube-prometheus-prometheus --name=prometheus-kube-prometheus-prometheus-lb --type=LoadBalancer
eval "PROMETHEUS_${CTLP}=$(kubectl -n monitoring get svc prometheus-kube-prometheus-prometheus-lb -o jsonpath='{.status.loadBalancer.ingress[0].ip}:{.spec.ports[0].port}')"

#### Fix metrics expositions
###for K8S in ${CTLP} ${TEST} ${PROD}; do
###  # Check https://artifacthub.io/packages/helm/kube-prometheus-stack-oci/kube-prometheus-stack/14.2.0#kubeproxy
###  kubectl -n kube-system get cm kube-proxy -o yaml | sed 's/metricsBindAddress:.*$/metricsBindAddress: 0.0.0.0:10249/' | kubectl apply -f -
###  # Force pod recreation
###  kubectl -n kube-system delete pod -l k8s-app=kube-proxy
###  
### 
###done

# GRAFANA
helm install --namespace grafana --create-namespace grafana grafana/grafana
kubectl -n grafana patch svc grafana -p '{"spec": {"type": "LoadBalancer"}}'
GRAFANA_UI=$(kubectl -n grafana get svc grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}:{.spec.ports[0].port}')
GRAFANA_PW=$(kubectl get secret --namespace grafana grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo4 --decode)

echo "(${CTLP}) Grafana web interface: ${GRAFANA_UI}"
echo "(${CTLP}) Grafana admin password: ${GRAFANA_PW}"
for K8S in ${CTLP} ${TEST} ${PROD}; do
  echo -n "(${K8S}) Prometheus: "
  eval "echo \${PROMETHEUS_${K8S}}"
done

# Dashboards: https://github.com/dotdc/grafana-dashboards-kubernetes
