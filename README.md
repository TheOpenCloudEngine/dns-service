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

* Storage: pdns-postgres-data-persistentvolumeclaim.yaml (DB 저장 공간 확보)
* Database: pdns-db-deployment.yaml (PostgreSQL 실행)
* Server: pdns-server-deployment.yaml & pdns-server-service.yaml (PowerDNS 실행)
* Admin UI: pdns-admin-deployment.yaml & pdns-admin-service.yaml (관리 화면 실행)

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
