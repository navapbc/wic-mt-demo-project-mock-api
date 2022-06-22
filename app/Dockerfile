# Use the official python3 image based on Debian 11 "Bullseye".
# https://hub.docker.com/_/python
FROM python:3-slim
# Keep container packages up-to-date.
RUN apt update \
    && apt install --yes --no-install-recommends \
        cron \
    && apt upgrade --yes
# Install poetry, the package manager.
# https://python-poetry.org
RUN pip install poetry
# Copy application files.
COPY . /srv
# Set the application working directory.
WORKDIR /srv
# Install application dependencies.
# https://python-poetry.org/docs/basic-usage/#installing-dependencies
RUN poetry install
# Run the application.
CMD ["cron", "-f"]