FROM python:3.10-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock
COPY solution ./solution
COPY artifacts/classifier.joblib ./artifacts/classifier.joblib
COPY docs ./docs
COPY process-log/README.md ./process-log/README.md
RUN useradd --create-home caseuser && mkdir -p /app/artifacts/runtime && chown -R caseuser:caseuser /app
USER caseuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app:app", "--app-dir", "solution", "--host", "0.0.0.0", "--port", "8000"]
