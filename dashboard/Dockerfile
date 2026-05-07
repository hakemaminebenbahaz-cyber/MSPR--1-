FROM node:20-alpine AS builder

WORKDIR /app

# npm ci = installation reproductible (plus fiable que npm install)
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Image de production — nginx léger
FROM nginx:alpine

# Configuration SPA (gère le routing React)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copier le build
COPY --from=builder /app/dist /usr/share/nginx/html

# Utilisateur non-root
RUN chown -R nginx:nginx /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1
