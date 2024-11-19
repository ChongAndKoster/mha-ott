# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/venv/bin:$PATH"

# Run the command to start the server

# CMD ["python", "manage.py", "runserver", "0.0.0.0:80" ] 
# CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:80"]
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:80"]

