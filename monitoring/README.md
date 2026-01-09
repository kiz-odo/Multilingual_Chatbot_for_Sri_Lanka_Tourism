# Distributed Tracing and APM Integration

## Overview

This setup includes:
- Jaeger for distributed tracing
- OpenTelemetry for instrumentation
- Sentry for error tracking
- Prometheus for metrics
- Grafana for visualization

## Installation

### 1. Install OpenTelemetry

```bash
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-instrumentation-pymongo
pip install opentelemetry-instrumentation-redis
pip install opentelemetry-instrumentation-requests
pip install opentelemetry-exporter-jaeger
pip install opentelemetry-exporter-prometheus
```

### 2. Install Sentry

```bash
pip install sentry-sdk[fastapi]
```

## Configuration

### Environment Variables

```bash
# Jaeger
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831
JAEGER_SAMPLER_TYPE=probabilistic
JAEGER_SAMPLER_PARAM=0.1

# Sentry
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# OpenTelemetry
OTEL_SERVICE_NAME=tourism-chatbot
OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14268/api/traces
```

## Kubernetes Deployment

```bash
kubectl apply -f monitoring/jaeger-deployment.yaml
kubectl apply -f monitoring/sentry-relay.yaml
```

## Usage

All instrumentation is automatic. Traces and errors will be sent to respective backends.

### Access Jaeger UI

```bash
kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring
# Open http://localhost:16686
```

### Access Sentry

Visit your Sentry dashboard at https://sentry.io
