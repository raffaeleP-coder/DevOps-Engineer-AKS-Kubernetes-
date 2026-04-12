FROM python:3.12-slim

WORKDIR /app

RUN groupadd -g 10001 devops && useradd -u 10001 -g 10001 -m -s /usr/sbin/nologin devops

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=devops:devops . .

USER devops

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "app:app"]

