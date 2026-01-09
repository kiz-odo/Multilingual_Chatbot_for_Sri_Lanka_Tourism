# 🚀 Deployment Documentation

Complete guide for deploying the backend to production.

## Overview

The backend can be deployed using Docker, Kubernetes, or directly on servers. This guide covers all deployment methods.

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Kubernetes cluster (for K8s deployment)
- Server with Python 3.9+ (for direct deployment)
- MongoDB 6.0+ (or MongoDB Atlas)
- Redis 7.0+ (or Redis Cloud)

## Deployment Methods

### 1. Docker Deployment

#### Build Docker Image

```bash
# Build production image
docker build -t sri-lanka-tourism-chatbot:latest -f docker/backend/Dockerfile .

# Tag for registry
docker tag sri-lanka-tourism-chatbot:latest your-registry/sri-lanka-tourism-chatbot:v1.0.0
```

#### Docker Compose Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Restart services
docker-compose restart backend
```

#### Docker Compose Configuration

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - mongodb
      - redis
    restart: unless-stopped

  mongodb:
    image: mongo:6.0
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  mongodb_data:
  redis_data:
```

### 2. Kubernetes Deployment

#### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods

# View logs
kubectl logs -f deployment/backend

# Scale deployment
kubectl scale deployment backend --replicas=3
```

#### Kubernetes Manifests

**Location**: `kubernetes/`

- `deployment.yaml` - Backend deployment
- `service.yaml` - Service definition
- `configmap.yaml` - Configuration
- `secret.yaml` - Secrets (create from .env)
- `ingress.yaml` - Ingress configuration

### 3. Direct Server Deployment

#### Server Setup

```bash
# Install dependencies
sudo apt update
sudo apt install python3.9 python3-pip nginx

# Create virtual environment
python3 -m venv /opt/backend/venv
source /opt/backend/venv/bin/activate

# Install application
cd /opt/backend
git clone <repository-url> .
pip install -r requirements.txt

# Configure environment
cp env.example .env
nano .env  # Edit configuration
```

#### Systemd Service

**/etc/systemd/system/backend.service**:
```ini
[Unit]
Description=Sri Lanka Tourism Chatbot Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/backend
Environment="PATH=/opt/backend/venv/bin"
ExecStart=/opt/backend/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start Service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable backend
sudo systemctl start backend
sudo systemctl status backend
```

#### Nginx Reverse Proxy

**/etc/nginx/sites-available/backend**:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable Site**:
```bash
sudo ln -s /etc/nginx/sites-available/backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Configuration

### Production Environment Variables

**Required Variables**:
```bash
# Application
APP_NAME="Sri Lanka Tourism Chatbot"
DEBUG=false
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Security (IMPORTANT: Generate secure key!)
SECRET_KEY="<generate-secure-key>"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
MONGODB_URL="mongodb://user:password@host:27017/dbname?authSource=admin"
DATABASE_NAME="sri_lanka_tourism_bot"

# Redis
REDIS_URL="redis://host:6379/0"

# External APIs (Optional but recommended)
GOOGLE_TRANSLATE_API_KEY=""
GOOGLE_MAPS_API_KEY=""
OPENWEATHER_API_KEY=""
CURRENCYLAYER_API_KEY=""

# Monitoring
SENTRY_DSN=""
PROMETHEUS_ENABLED=true

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Generate Secure Secret Key

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database Setup

### MongoDB Setup

#### Local MongoDB

```bash
# Install MongoDB
sudo apt install mongodb

# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Create database user
mongo
use admin
db.createUser({
  user: "admin",
  pwd: "secure-password",
  roles: ["root"]
})
```

#### MongoDB Atlas (Cloud)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create cluster
3. Create database user
4. Whitelist IP addresses
5. Get connection string

**Connection String**:
```
mongodb+srv://username:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority
```

### Redis Setup

#### Local Redis

```bash
# Install Redis
sudo apt install redis-server

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Test connection
redis-cli ping
```

#### Redis Cloud

1. Create account at https://redis.com/cloud
2. Create database
3. Get connection string

## Pre-Deployment Checklist

### Security

- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Set DEBUG=false
- [ ] Configure firewall rules
- [ ] Enable database authentication
- [ ] Review CORS settings
- [ ] Set up rate limiting
- [ ] Configure security headers

### Configuration

- [ ] Set environment variables
- [ ] Configure database connection
- [ ] Configure Redis connection
- [ ] Set up external API keys
- [ ] Configure logging
- [ ] Set up monitoring

### Database

- [ ] Run migrations
- [ ] Create indexes
- [ ] Seed initial data (if needed)
- [ ] Set up backups
- [ ] Test database connection

### Testing

- [ ] Run all tests
- [ ] Test API endpoints
- [ ] Test authentication
- [ ] Test rate limiting
- [ ] Load testing

## Deployment Steps

### 1. Pre-Deployment

```bash
# Run tests
pytest backend/tests/ -v

# Check code quality
black --check backend/
ruff check backend/

# Build Docker image (if using Docker)
docker build -t sri-lanka-tourism-chatbot:latest .
```

### 2. Database Migration

```bash
# Run migrations
python -m backend.app.core.migrations migrate

# Verify indexes
python -m backend.app.core.migrations status
```

### 3. Deploy Application

```bash
# Docker Compose
docker-compose up -d

# Or Kubernetes
kubectl apply -f kubernetes/

# Or systemd
sudo systemctl restart backend
```

### 4. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health/ready

# API test
curl http://localhost:8000/api/v1/attractions

# Check logs
docker-compose logs -f backend
# Or
sudo journalctl -u backend -f
```

## Monitoring

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/health/ready

# Detailed status
curl http://localhost:8000/health/detailed
```

### Logs

```bash
# Docker
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/backend

# Systemd
sudo journalctl -u backend -f
```

### Metrics

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Sentry**: Error tracking dashboard

## Scaling

### Horizontal Scaling

```bash
# Docker Compose (multiple instances)
docker-compose up -d --scale backend=3

# Kubernetes
kubectl scale deployment backend --replicas=3
```

### Load Balancing

Use Nginx or cloud load balancer:

```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

## Backup and Recovery

### Database Backup

```bash
# MongoDB backup
mongodump --uri="mongodb://user:pass@host:27017/db" --out=/backup/$(date +%Y%m%d)

# Redis backup
redis-cli --rdb /backup/redis-$(date +%Y%m%d).rdb
```

### Automated Backups

```bash
# Cron job for daily backups
0 2 * * * /usr/local/bin/backup-database.sh
```

### Recovery

```bash
# MongoDB restore
mongorestore --uri="mongodb://user:pass@host:27017/db" /backup/20240101/db

# Redis restore
redis-cli --rdb /backup/redis-20240101.rdb
```

## SSL/TLS Configuration

### Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check service is running
   - Verify port is open
   - Check firewall rules

2. **Database Connection Failed**
   - Verify connection string
   - Check database is running
   - Verify credentials

3. **High Memory Usage**
   - Check for memory leaks
   - Optimize queries
   - Increase server resources

4. **Slow Response Times**
   - Check database indexes
   - Verify caching is working
   - Check external API response times

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart service
sudo systemctl restart backend
```

## Rollback

### Docker

```bash
# Rollback to previous image
docker-compose down
docker-compose up -d --image sri-lanka-tourism-chatbot:v0.9.0
```

### Kubernetes

```bash
# Rollback deployment
kubectl rollout undo deployment/backend

# Check rollout status
kubectl rollout status deployment/backend
```

## Production Best Practices

1. **Use Environment Variables**: Never hardcode secrets
2. **Enable HTTPS**: Always use SSL/TLS in production
3. **Monitor Resources**: Set up alerts for CPU, memory, disk
4. **Regular Backups**: Automated daily backups
5. **Log Rotation**: Configure log rotation
6. **Rate Limiting**: Enable rate limiting
7. **Security Headers**: Configure security headers
8. **Update Dependencies**: Regularly update dependencies
9. **Health Checks**: Configure health check endpoints
10. **Documentation**: Keep deployment docs updated

## Cloud Deployment

### AWS

- **EC2**: Virtual servers
- **ECS**: Container orchestration
- **EKS**: Kubernetes service
- **RDS**: Managed MongoDB (via DocumentDB)
- **ElastiCache**: Managed Redis

### Google Cloud

- **Compute Engine**: Virtual machines
- **Cloud Run**: Serverless containers
- **GKE**: Kubernetes service
- **MongoDB Atlas**: Managed MongoDB
- **Memorystore**: Managed Redis

### Azure

- **Virtual Machines**: VMs
- **Container Instances**: Containers
- **AKS**: Kubernetes service
- **Cosmos DB**: NoSQL database
- **Redis Cache**: Managed Redis

## Future Enhancements

1. **CI/CD Pipeline**: Automated deployment
2. **Blue-Green Deployment**: Zero-downtime deployments
3. **Canary Releases**: Gradual rollout
4. **Auto-Scaling**: Automatic scaling based on load
5. **Multi-Region**: Deploy to multiple regions

