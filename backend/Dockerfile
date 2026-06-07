FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Seed database and start server
CMD ["sh", "-c", "python seed_database.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
