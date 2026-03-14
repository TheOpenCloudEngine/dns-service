# PowerDNS Service

## Deploy to Docker

```
docker-compose up -d
```

## Deploy to K8S

### Type

* Storage: pdns-postgres-data-persistentvolumeclaim.yaml (DB 저장 공간 확보)
* Database: pdns-db-deployment.yaml (PostgreSQL 실행)
* Server: pdns-server-deployment.yaml & pdns-server-service.yaml (PowerDNS 실행)
* Admin UI: pdns-admin-deployment.yaml & pdns-admin-service.yaml (관리 화면 실행)

## Convert

```
kompose convert -f docker-compose.yml
```

### Run

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

### 주의사항

* Service Type 확인: 기본적으로 kompose는 서비스를 ClusterIP로 만듭니다. 외부에서 DNS 쿼리를 하거나 Admin UI에 접속하려면 서비스 타입을 NodePort나 LoadBalancer로 수정해야 할 수도 있습니다.
  * pdns-admin-service.yaml을 열어 type: ClusterIP를 type: NodePort로 바꾸면 외부 포트를 통해 UI 접속이 가능해집니다.
* 데이터 보존: pdns-postgres-data-persistentvolumeclaim.yaml이 생성되었지만, 실제 클러스터에 이 요청을 들어줄 StorageClass가 설정되어 있어야 합니다. 만약 Pod가 Pending 상태에서 멈춰있다면 kubectl describe pvc로 확인해 보세요.
* DNS 포트 (53번): 쿠버네티스 노드 자체에서 이미 DNS를 사용 중일 수 있습니다. pdns-server의 서비스 타입이 LoadBalancer가 아니라면 포트 충돌이 날 수 있으니 확인이 필요합니다.
