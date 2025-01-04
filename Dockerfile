# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for MySQL and Python build tools
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev gcc pkg-config \
    && apt-get clean

# Install required packages
RUN apt-get update && apt-get install -y default-mysql-client

# Copy Pipfile and Pipfile.lock into the container
COPY ./Pipfile ./Pipfile.lock ./

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Install Python dependencies using pipenv
RUN pipenv install --system --deploy

# Copy the rest of the application code
COPY . ./

# Expose the port Django runs on
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]