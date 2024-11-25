
FROM FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script into the container
COPY my_script.py .
COPY run.py .

# Set the default command to execute the Python script
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]

