# Improved Dockerfile for Rasa Chatbot with SpaCy

FROM rasa/rasa:3.6.13

# Set working directory
WORKDIR /app

# Switch to root to install dependencies
USER root

# Install system dependencies and SpaCy with English model
RUN pip install --no-cache-dir \
    httpx \
    asyncio \
    motor \
    pymongo \
    spacy==3.7.2 \
    && python -m spacy download en_core_web_md

# Copy Rasa configuration and training data
COPY backend/rasa/ ./rasa/

# Create models directory with proper permissions
RUN mkdir -p /app/models && \
    mkdir -p /app/rasa/models && \
    chown -R 1001:0 /app && \
    chmod -R 775 /app

# Switch back to rasa user
USER 1001

# Expose port
EXPOSE 5005

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5005/status || exit 1

# Default command
CMD ["run", "--enable-api", "--cors", "*", "--port", "5005", "--model", "/app/rasa/models"]
