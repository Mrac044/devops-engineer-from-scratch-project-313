FROM node:20-alpine AS frontend-loader
WORKDIR /app
RUN npm install @hexlet/project-devops-deploy-crud-frontend



FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

COPY --from=frontend-loader /app/node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /app/public/

ENV FLASK_APP=paas/scripts/app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY paas/ ./paas/
COPY ./services/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

RUN echo '#!/bin/sh\nflask run --port=5000 & \nnginx -g "daemon off;"\n' > /app/start.sh && chmod +x /app/start.sh
CMD ["/app/start.sh"]