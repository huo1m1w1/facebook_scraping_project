# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Copy only the files needed for installing dependencies
COPY pyproject.toml poetry.lock /app/

# Install poetry and project dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy the rest of the application code
COPY . /app

# Run main.py when the container launches
CMD ["python", "-u", "src/fb_scraping_project/main.py"]
