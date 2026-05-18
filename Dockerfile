FROM python:3.12

WORKDIR /app

ENV FLASK_APP=paas/scripts/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY paas/ ./paas/
EXPOSE 8080

CMD ["flask", "run", "--debug"]