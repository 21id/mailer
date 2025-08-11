#!/bin/bash

set -e

export $(grep -v '^#' .env | xargs)
export SMTP_FROM="21ID <no-reply@21id.uz>"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000