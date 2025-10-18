Method A: If using Docker Compose (recommended)

  # Stop only backend service
  docker compose stop backend

  # Rebuild only backend
  docker compose build backend --no-cache

  # Start backend
  docker compose up -d backend

  # Check logs
  docker compose logs -f backend

