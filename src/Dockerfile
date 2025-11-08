# 1️⃣ Base image
FROM python:3.11-slim

# 2️⃣ Working directory
WORKDIR /app

# 3️⃣ Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 4️⃣ System dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 5️⃣ Copy requirements & install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6️⃣ Copy project files
COPY . /app

# 7️⃣ Expose port
EXPOSE 8000

# 8️⃣ Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
