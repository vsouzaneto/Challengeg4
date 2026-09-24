FROM node:24-alpine

RUN apk add --no-cache \
    postgresql \
    postgresql-client \
    su-exec

WORKDIR /app

COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci

COPY backend/package*.json ./backend/
RUN cd backend && npm ci

COPY frontend ./frontend
COPY backend ./backend
COPY data ./data
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN (cd backend && npm run build) \
    && (cd frontend && npm run build) \
    && chmod +x /docker-entrypoint.sh

EXPOSE 3000 5173

CMD ["/docker-entrypoint.sh"]
