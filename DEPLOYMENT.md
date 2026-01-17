# FlowForge Deployment Guide

## 🐳 Docker Containerization

This guide provides complete containerization and deployment instructions for the FlowForge application.

## 📋 Prerequisites

- Docker & Docker Compose
- Domain name (for production)
- SSL certificates (optional, for HTTPS)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend    │    │    Backend     │    │   PostgreSQL    │
│   (Nginx)    │    │   (FastAPI)    │    │    Database      │
│   Port 80/443 │    │   Port 8000    │    │   Port 5432     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┴─────────────────────┘
                    Nginx Reverse Proxy
```

## 🚀 Quick Start (Development)

```bash
# Clone the repository
git clone <repository-url>
cd flowforge

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🏭 Production Deployment

### 1. Environment Configuration

Create `.env` file:
```bash
# Database Configuration
POSTGRES_PASSWORD=your_secure_password_here
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# SSL Configuration (optional)
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
```

### 2. Production Deployment

```bash
# Deploy with production profile
docker-compose -f docker-compose.prod.yml --profile production up -d

# Deploy with SSL and reverse proxy
docker-compose -f docker-compose.prod.yml --profile production up -d
```

### 3. SSL Configuration (Optional)

Place SSL certificates in `./ssl/` directory:
- `cert.pem` - SSL certificate
- `key.pem` - Private key

Uncomment HTTPS section in `nginx/nginx.conf`

## 📊 Service Details

### Frontend (Nginx)
- **Image**: Custom build from Node.js + Nginx
- **Port**: 80 (HTTP), 443 (HTTPS)
- **Features**: 
  - Static file serving
  - Gzip compression
  - Security headers
  - Rate limiting
  - WebSocket support

### Backend (FastAPI)
- **Image**: Python 3.11 Alpine
- **Port**: 8000
- **Features**:
  - Auto-restart
  - Health checks
  - Non-root user
  - Volume mounts

### Database (PostgreSQL)
- **Image**: postgres:15-alpine
- **Port**: 5432
- **Features**:
  - Persistent data
  - Health checks
  - Automated initialization

### Cache (Redis) - Optional
- **Image**: redis:7-alpine
- **Port**: 6379
- **Features**:
  - Persistent data
  - Health checks

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_PASSWORD` | `secure_password_123` | Database password |
| `CORS_ORIGINS` | `http://localhost` | Allowed CORS origins |
| `ENVIRONMENT` | `development` | Application environment |

### Volume Mounts

| Path | Description |
|-------|-------------|
| `postgres_data` | PostgreSQL data persistence |
| `redis_data` | Redis data persistence |
| `./backend/uploads` | File uploads |
| `./backend/chroma_db` | Vector database |
| `./ssl` | SSL certificates |

## 🔍 Monitoring & Health Checks

### Health Check Endpoints

```bash
# Frontend health
curl http://localhost/health

# Backend health
curl http://localhost:8000/docs

# Database health
docker-compose exec postgres pg_isready -U flowforge_user -d flowforge_db

# Redis health
docker-compose exec redis redis-cli ping
```

### Monitoring Commands

```bash
# View all service status
docker-compose ps

# View resource usage
docker stats

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

## 🔒 Security Features

### Implemented Security Measures

1. **Network Isolation**: Custom Docker network
2. **Non-root Users**: Backend runs as non-privileged user
3. **Rate Limiting**: API endpoints protected
4. **Security Headers**: XSS, CSRF, clickjacking protection
5. **SSL/TLS**: HTTPS support with proper certificates
6. **CORS**: Configurable origin restrictions
7. **Health Checks**: Automated service monitoring

### Security Headers Applied

- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: no-referrer-when-downgrade`
- `Content-Security-Policy: restrictive policy`

## 📈 Scaling Options

### Horizontal Scaling

```bash
# Scale backend services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Scale with load balancer
docker-compose -f docker-compose.prod.yml --profile production up -d
```

### Performance Optimization

1. **Database Indexing**: Proper indexes on queries
2. **Redis Caching**: Session and response caching
3. **Gzip Compression**: Reduced bandwidth usage
4. **Static Asset Caching**: Long-term caching
5. **Connection Pooling**: Database connection management

## 🔄 Backup & Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U flowforge_user flowforge_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U flowforge_user flowforge_db < backup.sql

# Automated backup (cron)
0 2 * * * docker-compose exec postgres pg_dump -U flowforge_user flowforge_db > /backups/backup_$(date +\%Y\%m\%d).sql
```

### Volume Backup

```bash
# Backup all volumes
docker run --rm -v flowforge_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
docker run --rm -v flowforge_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**: Change port mappings in docker-compose.yml
2. **Permission Issues**: Ensure proper file permissions
3. **Database Connection**: Check network and credentials
4. **SSL Issues**: Verify certificate paths and formats
5. **Memory Issues**: Increase Docker memory limits

### Debug Commands

```bash
# Check container logs
docker-compose logs <service_name>

# Enter container for debugging
docker-compose exec backend sh
docker-compose exec postgres psql -U flowforge_user -d flowforge_db

# Rebuild services
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

## 🚀 Production Best Practices

1. **Use Production Profile**: `--profile production`
2. **Configure SSL**: Always use HTTPS in production
3. **Monitor Resources**: Set up monitoring and alerts
4. **Regular Backups**: Automated backup schedule
5. **Update Regularly**: Keep images and dependencies updated
6. **Environment Variables**: Use secure, unique passwords
7. **Network Security**: Configure firewall rules
8. **Load Balancing**: Use multiple backend instances

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: Environment variables
3. Test connectivity: Health check endpoints
4. Review this guide: Common issues section

---

**FlowForge is now fully containerized and ready for production deployment!** 🎉
