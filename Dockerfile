# Use an official Python runtime as a base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure the entrypoint script is executable
RUN chmod +x entrypoint.sh

# Set the entrypoint script to run when the container starts
ENTRYPOINT ["./entrypoint.sh"]

# The CMD can specify default arguments to the ENTRYPOINT or run as the main process if ENTRYPOINT isn't set
# It's good practice to keep CMD, as it allows you to override it easily at runtime if needed
CMD ["python", "run.py"]
