# Nginx Dockerfile
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy nginx configuration
COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY infra/nginx/sites-enabled/ /etc/nginx/sites-enabled/

# Create directories for static and media files
RUN mkdir -p /var/www/static /var/www/media

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
