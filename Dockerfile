# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Dependencies for postgres, added for debugging
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/
RUN chmod u+x /app/docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["sh","/app/docker-entrypoint.sh"]

CMD ["python", "carebot/manage.py", "runserver", "0.0.0.0:8000"]
