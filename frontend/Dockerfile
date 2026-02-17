# Frontend Dockerfile for React/Vite application

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build-time argument for API URL
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application (VITE_ vars are embedded at build time)
RUN echo "Building with VITE_API_BASE_URL=$VITE_API_BASE_URL" && npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (Railway maps PORT to this)
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
