# Use the puckel/docker-airflow base image
FROM puckel/docker-airflow:1.10.9

# Set environment variables
ENV AIRFLOW_HOME=/usr/local/airflow

# Switch to root user to install dependencies
USER root

# Install necessary system packages for psycopg2 and other dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy entrypoint.sh script to customize entrypoint
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Switch back to airflow user
USER airflow

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command to start Airflow webserver
CMD ["webserver"]
