# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY ./llm_manager/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy local packages
COPY ./setup.py .
COPY ./providers ./providers
COPY ./llm_manager ./llm_manager

# Install local package
RUN pip install .

# Expose the port the app runs on
EXPOSE 8001

# Run uvicorn server
CMD ["uvicorn", "llm_manager.main:app", "--host", "0.0.0.0", "--port", "8001"] 