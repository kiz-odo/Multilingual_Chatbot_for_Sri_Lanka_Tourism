# Dockerfile for Rasa Actions Server

FROM rasa/rasa-sdk:3.6.2

# Set working directory
WORKDIR /app

# Switch to root to install dependencies
USER root

# Install additional dependencies
RUN pip install --no-cache-dir \
    httpx \
    asyncio \
    motor \
    pymongo \
    beanie

# Copy actions code
COPY backend/rasa/actions/ ./rasa/actions/

# Set permissions
RUN chown -R 1001:0 /app && chmod -R 775 /app

# Switch back to rasa user
USER 1001

# Expose port
EXPOSE 5055

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5055/health || exit 1

# Default command
CMD ["start", "--actions", "rasa.actions", "--port", "5055", "--debug"]
