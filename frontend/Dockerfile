FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the HTML files
COPY *.html /app/

# Expose port
EXPOSE 3000

# Create a simple startup script
RUN echo '#!/bin/bash\ncd /app\npython -m http.server 3000' > /app/start.sh && \
    chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000')" || exit 1

# Start the server
CMD ["/app/start.sh"]