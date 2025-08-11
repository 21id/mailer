# MJML builder
FROM node:22-alpine AS mjml

WORKDIR /templates
COPY templates/package*.json ./templates/
RUN cd templates && npm install

COPY templates/src ./templates/src
RUN cd templates && npm run all

# Python runner
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY --from=mjml /templates/templates/dist /app/templates/files

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]