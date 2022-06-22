# Use the official python3 image based on Debian 11 "Bullseye".
# https://hub.docker.com/_/python
FROM python:3-slim
# Install poetry, the package manager.
# https://python-poetry.org
RUN pip install poetry
# Keep container packages up-to-date.
RUN apt update \
    && apt install --yes --no-install-recommends \
        cron \
    && apt upgrade --yes
CMD ["cron", "-f"]
