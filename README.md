# PowerDNS Service

## Run

```
docker-compose up -d
```

## Convert K8S

```
kompose convert -f docker-compose.yml
```

## Deploy to K8S

```
kubectl apply -f .

OR

# PVC와 DB 먼저 배포
kubectl apply -f pdns-postgres-data-persistentvolumeclaim.yaml
kubectl apply -f pdns-db-deployment.yaml

# 조금 기다린 후 나머지도 배포
kubectl apply -f pdns-server-service.yaml -f pdns-server-deployment.yaml
kubectl apply -f pdns-admin-service.yaml -f pdns-admin-deployment.yaml
```
