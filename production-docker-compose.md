root@srv1098486:~/opt/wealth-coach-ai# cat docker-compose.backend.yml
# =============================================================================
# BACKEND-ONLY DOCKER COMPOSE CONFIGURATION
# Wealth Coach AI - Backend API Deployment
# =============================================================================

services:
  # ===========================================================================
  # Backend API Service
  # ===========================================================================
  backend:
    build:
      context: .
      dockerfile: Dockerfile.prod
      args:
        - BUILD_ENV=production
    container_name: wealth_coach_backend
    user: "1000:1000" #added this line
    restart: always
    ports:
      - "8000:8000"
    command: >
        gunicorn backend.main:app
        --workers 1
        --worker-class uvicorn.workers.UvicornWorker
        --bind 0.0.0.0:8000
        --timeout 120
        --access-logfile -
        --error-logfile -
        --log-level info
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=WARNING
      - HOME=/home/appuser #added this line
      - REDIS_URL=${REDIS_URL}
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    env_file:
      - .env
    volumes:
     # - ./logs:/app/logs
      - ./data/knowledge_base:/app/data/knowledge_base:ro
      - huggingface_cache:/home/appuser/.cache  # ADDed THIS LINE
    networks:
      - backend_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

# =============================================================================
# Networks
# =============================================================================
networks:
  backend_network:
    driver: bridge
    enable_ipv6: true
    ipam:
       driver: default
       config:
         - subnet: 172.28.0.0/16
         - subnet: fd00:dead:beef::/48

# =============================================================================
# Volumes
# =============================================================================
volumes:
  logs:
    driver: local
  huggingface_cache:
    driver: local
root@srv1098486:~/opt/wealth-coach-ai#