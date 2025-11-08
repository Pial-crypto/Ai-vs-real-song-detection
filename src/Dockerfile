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

# 5️⃣ Copy only requirements file (so Docker can cache installs)
COPY requirements.txt /app/

# 6️⃣ Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ⚡ Docker will cache everything above this line
#    So unless `requirements.txt` changes, it won’t re-download torch etc.

# 7️⃣ Copy the rest of your project files
COPY . /app/

# 8️⃣ Expose the FastAPI port
EXPOSE 8000

# 9️⃣ Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
