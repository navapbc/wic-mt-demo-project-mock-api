# WIC Mock API

This is a Mock API wrapper around the SPIRIT MIS for the Special Supplemental Nutrition Program for Women, Infants, and Children (WIC). It was developed for the State of Montana.

## Getting started

This application is dockerized. Take a look at [Dockerfile](./app/Dockerfile) to see how it works.

A very simple [docker-compose.yml](./docker-compose.yml) has been included to support local development and deployment. Take a look at [docker-compose.yml](./docker-compose.yml) for more information.

**How to run:**

1. In your terminal, `cd` to this repo.
2. Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed & running.
3. Run `make init start` to build the image and start the container.
4. Navigate to `localhost:8080/v1/docs` to access the Swagger UI.
5. Run `make run-logs` to see the logs of the running API container
6. Run `docker-compose down` when you are done to delete the container.

See: [app/README.md](/app/README.md) for further details on the API implementation.