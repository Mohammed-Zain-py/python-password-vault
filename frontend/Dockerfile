FROM python:3.10-slim
WORKDIR /app

# We pull the requirements from the root folder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set the working directory to the frontend folder and start Streamlit
WORKDIR /app/frontend
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]