# Kubernetes Deployment Guide

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Helm 3 (optional)
- Storage provisioner configured
- Ingress controller (NGINX recommended)

## Quick Start

### 1. Deploy Core Infrastructure

```bash
# Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Create configmaps and secrets
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml  # IMPORTANT: Update secrets first!

# Deploy storage class
kubectl apply -f kubernetes/storage-class.yaml

# Apply security policies
kubectl apply -f kubernetes/pod-security-policy.yaml
kubectl apply -f kubernetes/network-policy.yaml

# Deploy databases
kubectl apply -f kubernetes/mongodb-statefulset.yaml
kubectl apply -f kubernetes/redis-deployment.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=tourism-mongodb -n tourism-chatbot --timeout=300s
kubectl wait --for=condition=ready pod -l app=tourism-redis -n tourism-chatbot --timeout=300s

# Deploy backend application
kubectl apply -f kubernetes/backend-deployment.yaml

# Deploy ingress
kubectl apply -f kubernetes/ingress.yaml

# Deploy autoscaling
kubectl apply -f kubernetes/hpa.yaml
```

### 2. Verify Deployment

```bash
# Check all resources
kubectl get all -n tourism-chatbot

# Check pod status
kubectl get pods -n tourism-chatbot

# Check logs
kubectl logs -f -l app=tourism-backend -n tourism-chatbot

# Check ingress
kubectl get ingress -n tourism-chatbot
```

### 3. Access Application

```bash
# Port forward for local testing
kubectl port-forward svc/tourism-backend 8000:8000 -n tourism-chatbot

# Access
curl http://localhost:8000/health
```

## Configuration

### Update Secrets

Before deploying, update `kubernetes/secrets.yaml` with actual values:

```bash
# Generate SECRET_KEY
python -c 'import secrets; print(secrets.token_urlsafe(32))'

# Update secrets.yaml with generated key
# Add all API keys and credentials
```

### Configure Ingress

Update `kubernetes/ingress.yaml`:
- Replace `api.tourism.lk` with your domain
- Configure TLS certificates
- Adjust rate limits

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment tourism-backend --replicas=5 -n tourism-chatbot

# Scale MongoDB
kubectl scale statefulset tourism-mongodb --replicas=5 -n tourism-chatbot
```

### Autoscaling

Autoscaling is configured via HPA:
- Backend: 3-10 replicas (CPU 70%, Memory 80%)
- MongoDB: 3-5 replicas (CPU 75%, Memory 85%)

## Monitoring

```bash
# Watch HPA
kubectl get hpa -n tourism-chatbot -w

# Check resource usage
kubectl top pods -n tourism-chatbot
kubectl top nodes
```

## Troubleshooting

### Pod Not Starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n tourism-chatbot

# Check events
kubectl get events -n tourism-chatbot --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Check MongoDB logs
kubectl logs -l app=tourism-mongodb -n tourism-chatbot

# Test connection
kubectl exec -it <backend-pod> -n tourism-chatbot -- mongosh $MONGODB_URL
```

### Ingress Not Working

```bash
# Check ingress
kubectl describe ingress tourism-ingress -n tourism-chatbot

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

## Rollback

```bash
# View deployment history
kubectl rollout history deployment/tourism-backend -n tourism-chatbot

# Rollback to previous version
kubectl rollout undo deployment/tourism-backend -n tourism-chatbot

# Rollback to specific revision
kubectl rollout undo deployment/tourism-backend --to-revision=2 -n tourism-chatbot
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace tourism-chatbot
```
