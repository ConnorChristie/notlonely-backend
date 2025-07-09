# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install first, to leverage Docker layer caching
COPY ./gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files, generate code, and fix the imports
COPY ./proto ./proto
RUN mkdir -p generated
RUN python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/chat.proto
RUN touch generated/__init__.py
RUN sed -i 's/^import chat_pb2 as chat__pb2/from . import chat_pb2 as chat__pb2/' generated/chat_pb2_grpc.py

# Copy the application source code
COPY ./gateway .

# Expose the ports the app runs on
EXPOSE 8000
EXPOSE 50051

# Run uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 