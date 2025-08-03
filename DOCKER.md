# DevOps Agentic AI - Docker Deployment Guide

This guide explains how to run the DevOps Agentic AI system using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)
- Git (for cloning repositories)

## Quick Start

### 1. Build and Run Status Check

```bash
./docker-run.sh status
```

### 2. Run in Interactive Mode

```bash
./docker-run.sh interactive
```

### 3. Run with Full Stack (Recommended)

```bash
# Setup environment variables first
cp .env.example .env
# Edit .env with your actual credentials

# Start full stack with monitoring
./docker-run.sh stack
```

## Available Services

When running the full stack, the following services are available:

| Service | Port | Description | Access URL |
|---------|------|-------------|------------|
| DevOps Agent | 8080 | Main AI agent | http://localhost:8080 |
| Grafana | 3000 | Metrics visualization | http://localhost:3000 |
| Prometheus | 9090 | Metrics collection | http://localhost:9090 |
| PostgreSQL | 5432 | Database | localhost:5432 |
| Redis | 6379 | Cache & state | localhost:6379 |

### Default Credentials

- **Grafana**: admin / admin123
- **PostgreSQL**: devopsagent / devopsagent123

## Usage Examples

### Build Docker Image

```bash
./docker-run.sh build
```

### Run Status Check

```bash
./docker-run.sh status
```

### Run Interactive Mode

```bash
./docker-run.sh interactive
```

### Run Batch Mode

```bash
./docker-run.sh batch https://github.com/user/repository
```

### Start Full Stack

```bash
./docker-run.sh stack
```

### View Logs

```bash
# View main agent logs
./docker-run.sh logs

# View specific service logs
./docker-run.sh logs redis
./docker-run.sh logs prometheus
./docker-run.sh logs grafana
```

### Stop Services

```bash
./docker-run.sh stop
```

### Cleanup

```bash
./docker-run.sh cleanup
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key environment variables:

- **AWS Credentials**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- **GCP Credentials**: `GOOGLE_APPLICATION_CREDENTIALS`
- **Azure Credentials**: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
- **Monitoring**: `PROMETHEUS_URL`, `GRAFANA_URL`
- **Notifications**: `SLACK_WEBHOOK_URL`, `EMAIL_*`

### Cloud Provider Setup

#### AWS
```bash
# Mount AWS credentials
# ~/.aws will be mounted read-only to the container
aws configure
```

#### Google Cloud
```bash
# Authenticate with gcloud
gcloud auth application-default login
```

#### Azure
```bash
# Login to Azure
az login
```

## Persistent Storage

The following directories are mounted for persistent storage:

- `./logs` - Application logs
- `./data` - Learning data and state
- `./temp` - Temporary files
- Docker volumes for databases

## Monitoring and Observability

### Grafana Dashboards

Access Grafana at http://localhost:3000 (admin/admin123) to view:

- System metrics
- Application performance
- Infrastructure costs
- Decision effectiveness

### Prometheus Metrics

Access Prometheus at http://localhost:9090 to query:

- CPU, memory, disk usage
- Response times and error rates
- Custom application metrics

## Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   # Start Docker Desktop or Docker daemon
   sudo systemctl start docker  # Linux
   ```

2. **Permission denied on docker.sock**
   ```bash
   # Add user to docker group (Linux)
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

3. **Port conflicts**
   ```bash
   # Check what's using the ports
   lsof -i :8080
   lsof -i :3000
   
   # Modify docker-compose.yml to use different ports
   ```

4. **Out of disk space**
   ```bash
   # Clean up Docker resources
   ./docker-run.sh cleanup
   docker system prune -a
   ```

### Viewing Logs

```bash
# Real-time logs for main agent
docker-compose logs -f devops-agent

# All services logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f redis
```

### Debugging

To run with debug logging:

```bash
# Set LOG_LEVEL=DEBUG in .env file
echo "LOG_LEVEL=DEBUG" >> .env

# Restart the stack
./docker-run.sh stop
./docker-run.sh stack
```

## Security Considerations

- Never commit `.env` file with real credentials
- Use read-only mounts for credential directories
- Run containers as non-root user (already configured)
- Regularly update base images for security patches
- Use Docker secrets in production environments

## Production Deployment

For production deployment:

1. Use environment-specific `.env` files
2. Set up proper SSL/TLS certificates
3. Configure external databases (not containers)
4. Set up proper monitoring and alerting
5. Use container orchestration (Kubernetes)
6. Implement proper backup strategies

### Kubernetes Deployment

```bash
# Example Kubernetes deployment (create k8s/ directory)
kubectl apply -f k8s/
```

## Performance Tuning

### Resource Limits

Modify `docker-compose.yml` to set resource limits:

```yaml
services:
  devops-agent:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Scaling Services

```bash
# Scale specific services
docker-compose up -d --scale devops-agent=3
```

## Development

### Development Mode

```bash
# Mount source code for development
docker run -it --rm \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/logs:/app/logs \
  devops-agent:latest bash
```

### Custom Builds

```bash
# Build with specific tag
docker build -t devops-agent:dev .

# Use custom image in docker-compose
export DEVOPS_AGENT_IMAGE=devops-agent:dev
docker-compose up -d
```

## Support

For issues and questions:

1. Check the logs: `./docker-run.sh logs`
2. Run status check: `./docker-run.sh status`
3. Review this documentation
4. Check Docker and system resources

## License

This project is licensed under the MIT License.
