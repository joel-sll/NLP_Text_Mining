# Use the official Python base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file from the subfolder
COPY interface/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app

# Set the default working directory to the Streamlit app folder
WORKDIR /app/interface

# Expose Streamlit's default port
EXPOSE 8501

# Set the Streamlit entry point
CMD ["streamlit", "run", "app.py","--server.port=8501", "--server.address=0.0.0.0"]
