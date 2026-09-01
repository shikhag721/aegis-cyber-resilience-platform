FROM python:3.12-slim

# Cybersecurity note: run as a non-root user inside the container to limit
# blast radius if the application process is ever compromised.
RUN useradd --create-home --shell /bin/bash aegis

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN chown -R aegis:aegis /app
USER aegis

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
