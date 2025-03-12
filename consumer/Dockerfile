# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variable so Python output is sent straight to the terminal
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the .env file and requirements first (this helps with caching)
COPY .env requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the consumer application code to the container
COPY . .

# Expose any ports if needed (optional)
# EXPOSE 8000

# Run main.py when the container launches
CMD ["python", "main.py"]
