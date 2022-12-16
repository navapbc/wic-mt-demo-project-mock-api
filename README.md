# WIC Mock API

This is a Mock API wrapper around the SPIRIT MIS for the Special Supplemental Nutrition Program for Women, Infants, and Children (WIC). It was developed for the State of Montana.

It currently includes:
- a `POST` endpoint for accepting data from an eligibility screener

## Features

- Python/Flask-based API that writes to a database using API key authentication
- PostgreSQL database + Alembic migrations configured for updating the database when the SQLAlchemy database models are updated
- Thorough formatting & linting tools
- Logging, with formatting in both human-readable and JSON formats
- Backend script that generates a CSV locally or on S3 with proper credentials
- Ability to run the various utility scripts inside or outside of Docker
- Restructured and improved API request and response error handling which gives more details than the out-of-the-box approach for both Connexion and Pydantic
- Easy environment variable configuration for local development using a `local.env` file

See [docs/README.md](/docs/README.md) for details on the API implementation.

## Getting started

This application is dockerized. Take a look at [Dockerfile](./app/Dockerfile) to see how it works.

A very simple [docker-compose.yml](./docker-compose.yml) has been included to support local development and deployment. Take a look at [docker-compose.yml](./docker-compose.yml) for more information.

**How to run:**

1. In your terminal, `cd` to the app directory of this repo.
2. Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed & running.
3. Run `make init start` to build the image and start the container.
4. Navigate to `localhost:8080/v1/docs` to access the Swagger UI.
5. Run `make run-logs` to see the logs of the running API container
6. Run `make stop` when you are done to delete the container.

## Disclaimer
This public repository exists purely for the purposes of hosting a snapshot of code to serve as a reference for similar efforts and is therefore not actively maintained. Entities wishing to use this code should do standard security due diligence and make sure to use up-to-date dependencies.
