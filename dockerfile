# build python environment
FROM python:3.12-slim

# Install required packages
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    rm -rf /var/lib/apt/lists/*

# Adding trusting keys to apt for repositories,
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# get Google Chrome
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# update apt-get
RUN apt-get -y update

# install google-chrome-stable
RUN apt-get install -y google-chrome-stable


# Set up a working directory
WORKDIR /app

# Copy your application files
COPY src/fb_scraping_project /app

# copy requiremnts/packages needed, and get installed
COPY requirements.txt requirements.txt
RUN pip install -r ./requirements.txt

# copy all files
COPY . .

# run the application
CMD [ "python", "main.py" ]




# # Install Python dependencies
# RUN pip install --no-cache-dir poetry \
#     && poetry config virtualenvs.create false \
#     && poetry install --no-dev

# # Add a non-root user
# RUN useradd -m appuser
# USER appuser

# # Set up Chrome options for headless mode
# ENV CHROME_OPTIONS "--headless", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"

# # Command to run your application with Poetry
# CMD ["poetry", "run", "python", "src/fb_scraping_project/main.py"]
