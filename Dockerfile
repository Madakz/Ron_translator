# Use official Python base image
FROM python:3.12.3

# Set working directory inside container
WORKDIR /app

# Install system dependencies (optional but useful for some libs)
RUN apt-get update && apt-get install -y build-essential

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

