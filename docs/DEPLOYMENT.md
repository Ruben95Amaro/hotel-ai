# Deployment Guide

## Overview

This guide covers deploying the Hotel AI Assistant to production environments.

## Prerequisites

- Docker & Docker Compose v2+
- Production API keys (Groq, Google Gemini)
- Domain name (optional, for HTTPS)
- SSL certificates (Let's Encrypt recommended)

## Quick Production Deploy

```bash
# 1. Prepare environment
cp .env.production.example .env.production
# Edit .env.production with production values

# 2. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 3. Verify
curl -H "X-API-Key: your-prod-key" https://your-domain.com/health
```

## Environment Configuration

### Required Production Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_API_KEY` | Groq production API key | `gsk_...` |
| `EMBEDDING_API_KEY` | Google Gemini production key | `AIza...` |
| `API_KEYS` | Comma-separated valid keys | `["key1","key2"]` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |

### Hotel Configuration

```env
HOTEL_NAME=Grand Ocean Hotel
HOTEL_LOCATION=Lisbon
HOTEL_STARS=4
HOTEL_PHONE=+351 21 123 4567
HOTEL_EMAIL=reservations@grandoceanhotel.com
```

### Security Settings

```env
# Generate secure random keys (openssl rand -hex 32)
API_KEYS=["prod-key-1","prod-key-2","prod-key-3"]

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=minute
```

## Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Commands
```bash
# View logs
docker-compose logs -f app

# Restart
docker-compose restart app

# Update
docker-compose pull && docker-compose up -d

# Backup ChromaDB
docker run --rm -v hotel-ai_chroma_data:/data -v $(pwd):/backup alpine tar czf /backup/chroma_backup.tar.gz /data
```

## Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Correlation-ID $http_x_correlation_id;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check bypass auth
    location /health {
        proxy_pass http://app:8000;
        access_log off;
    }
}
```

## SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (cron)
0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### Prometheus Config (`prometheus.yml`)
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'hotel-ai'
    static_configs:
      - targets: ['app:8000']
```

### Key Metrics to Monitor
| Metric | Alert Threshold |
|--------|-----------------|
| `http_requests_total` (5xx) | > 1% |
| `http_request_duration_seconds` | p99 > 5s |
| `active_connections` | > 1000 |
| `chromadb_documents` | < 1 (ingestion failed) |

## Log Aggregation

### Loki + Promtail
```yaml
services:
  loki:
    image: grafana/loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail
    volumes:
      - ./promtail-config.yaml:/etc/promtail/config.yaml
      - /var/log:/var/log
```

## Backup & Recovery

### ChromaDB Backup
```bash
# Create backup
docker run --rm -v hotel-ai_chroma_data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/chroma_$(date +%Y%m%d).tar.gz /data

# Restore
docker run --rm -v hotel-ai_chroma_data:/data -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/chroma_20240115.tar.gz -C /
```

### Redis Backup (RDB)
```bash
# Trigger save
docker exec hotel-ai-redis redis-cli BGSAVE

# Copy RDB file
docker cp hotel-ai-redis:/data/dump.rdb ./backups/redis_$(date +%Y%m%d).rdb
```

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.scale.yml
services:
  app:
    deploy:
      replicas: 3
    depends_on:
      - redis
      - chromadb
```

### Load Balancer (HAProxy)
```
frontend http_front
    bind *:80
    default_backend app_back

backend app_back
    balance roundrobin
    server app1 app1:8000 check
    server app2 app2:8000 check
    server app3 app3:8000 check
```

## Health Checks

```bash
# App health
curl http://localhost:8000/health

# Dependencies
curl http://localhost:8000/health | jq .dependencies

# Prometheus metrics
curl http://localhost:8000/metrics | grep http_requests_total
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| App won't start | Check logs: `docker logs hotel-ai-app` |
| ChromaDB connection failed | Verify `CHROMA_PATH` and network |
| Redis connection failed | Check `REDIS_URL` and Redis health |
| API key rejected | Verify `API_KEYS` in `.env.production` |
| Rate limited | Increase `RATE_LIMIT_REQUESTS` |
| Slow responses | Check Groq/Gemini API latency |

## Rollback Procedure

```bash
# 1. Tag current image
docker tag hotel-ai-app:latest hotel-ai-app:backup-$(date +%Y%m%d)

# 2. Deploy new version
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 3. If issues, rollback
docker-compose -f docker-compose.prod.yml down
docker tag hotel-ai-app:backup-20240115 hotel-ai-app:latest
docker-compose -f docker-compose.prod.yml up -d
```

## Security Checklist

- [ ] Strong `API_KEYS` generated
- [ ] HTTPS enabled with valid cert
- [ ] Rate limiting configured
- [ ] Firewall: only 80/443 open
- [ ] `.env.production` not in git
- [ ] Regular dependency updates
- [ ] Log aggregation configured
- [ ] Backup schedule active