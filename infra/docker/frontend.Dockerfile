# Frontend Dockerfile
FROM node:20-alpine

# Set work directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy project
COPY frontend/ .

# Expose port
EXPOSE 5173

# Default command (development)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
