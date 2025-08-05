# Frontend Dockerfile - Simple Python HTTP Server (No Nginx)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all frontend files
COPY index.html /app/
COPY styles.css /app/
COPY app.js /app/

# Expose port 80
EXPOSE 80

# Create a simple startup script
RUN echo '#!/bin/bash\ncd /app\npython -m http.server 80' > /app/start.sh && \
    chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:80')" || exit 1

# Start the simple HTTP server
CMD ["/app/start.sh"]