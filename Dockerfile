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
COPY ./paas/start.sh /app

RUN chmod +x start.sh

EXPOSE 80

CMD ["/app/start.sh"]