# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (Heroku uses $PORT)
EXPOSE 5000

# Run the main script
CMD ["python", "src/main.py"]
