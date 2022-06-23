# WIC Mock API

This is a Mock API wrapper around the SPIRIT MIS for the Special Supplemental Nutrition Program for Women, Infants, and Children (WIC). It was developed for the State of Montana.

## How to Run

This application is dockerized. Take a look at `./app/Dockerfile` to see how it works.

A very simple `docker-compose.yml` has been included to support local development and deployment. Take a look at `./docker-compose.yml` for more information.

How to run:

1. In your terminal, `cd` to this repo.
2. Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed & running.
3. Run `docker-compose up -d --build` to build the image and start the container.
4. Navigate to `localhost:8080/v1/docs` to access the Swagger UI.
5. Run `docker-compose down` when you are done to delete the container.
