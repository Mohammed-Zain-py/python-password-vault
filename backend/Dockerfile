FROM python:3.10-slim
WORKDIR /app

# We pull the requirements from the root folder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set the working directory to the backend folder and start Uvicorn
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]