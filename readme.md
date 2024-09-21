# FastAPI Project

## Overview

This project is a FastAPI application that provides a set of APIs for managing users and customers. It includes features such as user registration, authentication, rate limiting, and more. The application is designed to be efficient and scalable.

## Features

- User registration and login
- Customer management 
- Rate limiting per user
- Integration with Redis for rate limiting
- Sqlite for data persistence

## Prerequisites

Make sure you have the following installed:

- Python 3.9 or higher
- Docker (if using Docker)
- Docker Compose (if using Docker Compose)

## Installation
pip install -r requirements.txt

## Running
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

## Build the Docker Image:
docker build -t my-fastapi-app .

## Run the Docker Container
docker run -d -p 8000:8000 my-fastapi-app

