# Customer 360 Enterprise Data Platform

An enterprise-grade **Customer 360 Data Platform** designed to demonstrate scalable, real-time data processing using event-streaming architecture and containerized orchestration.

The platform aggregates, streams, and analyzes multi-source customer event data, providing unified customer insights through an interactive analytical dashboard.

## Tech Stack

| Component | Technologies |
|---|---|
| Backend & Event Streaming | Apache Kafka, Apache Zookeeper |
| Database | PostgreSQL |
| Caching | Redis |
| User Interface | Streamlit |
| Containerization | Docker |
| Orchestration | Docker Compose |

## Project Purpose

The objective of this project is to build a centralized customer data platform that integrates customer events from multiple sources and processes them using an event-driven architecture.

### Key Features

- **Unified Customer View:** Aggregate customer information and activities from multiple data sources.
- **Real-Time Data Streaming:** Utilize Apache Kafka to handle customer events through an event-driven architecture.
- **Scalable Data Storage:** Use PostgreSQL for persistent storage of structured customer information and event data.
- **High-Speed Caching:** Integrate Redis for efficient data access and caching.
- **Containerized Infrastructure:** Deploy and manage infrastructure services using Docker and Docker Compose.
- **Analytical Dashboard:** Provide customer insights and data visualizations through an interactive Streamlit interface.

## Architecture Overview

The platform follows an event-driven architecture in which Apache Kafka manages customer event streaming, PostgreSQL handles persistent data storage, and Redis provides caching capabilities.

Docker Compose coordinates the infrastructure services, while Streamlit provides an interactive interface for exploring customer data and analytical insights.

## Project Setup Guide

Follow the steps below to clone, configure, and run the project locally.

### 1. Clone the Repository

Clone the GitHub repository and navigate to the project directory:

```bash
git clone https://github.com/rahul-gupta-2004/ecom-customer-360.git

cd ecom-customer-360
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory of the project.

Add the following database configuration:

```env
POSTGRES_DB=customer360
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
```

Replace `your_secure_password` with a secure password of your choice.

### 3. Start the Infrastructure

Launch the infrastructure services using Docker Compose:

```bash
docker compose up -d
```

This starts the services configured in the Docker Compose file, including PostgreSQL, Apache Kafka, and Zookeeper.

### 4. Verify Running Containers

Check whether the containers are running successfully:

```bash
docker ps
```

To inspect service logs:

```bash
docker compose logs -f
```

### 5. Install Python Dependencies

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

It is recommended to use a Python virtual environment for dependency management.

### 6. Launch the Streamlit Dashboard

Start the application:

```bash
streamlit run main.py
```

Once the application starts, open the local URL displayed in your terminal (usually `http://localhost:8501`) to access the dashboard.

## Docker Hub Deployment

The project Docker image is published to Docker Hub for container distribution and deployment.

**Docker Hub Repository:**  
https://hub.docker.com/r/rahulguptatech/customer-360-app

### 1. Login to Docker Hub

Authenticate with your Docker Hub account:

```bash
docker login
```

### 2. Build the Docker Image

Build the application image from the project root directory:

```bash
docker build -t rahulguptatech/customer-360-app:latest .
```

### 3. Push the Image to Docker Hub

Push the tagged image to Docker Hub:

```bash
docker push rahulguptatech/customer-360-app:latest
```

### 4. Pull the Docker Image

To download the published image from Docker Hub:

```bash
docker pull rahulguptatech/customer-360-app:latest
```

## Infrastructure Management

The following Docker Compose commands can be used to manage the infrastructure:

| Command | Description |
|---|---|
| `docker compose up -d` | Start all services in the background |
| `docker compose down` | Stop and remove containers |
| `docker compose ps` | Display the status of services |
| `docker compose logs -f` | View live service logs |
| `docker compose restart` | Restart services |
| `docker ps` | List running containers |
| `docker images` | List locally available Docker images |

## Repository

**GitHub:**  
https://github.com/rahul-gupta-2004/ecom-customer-360

**Docker Hub:**  
https://hub.docker.com/r/rahulguptatech/customer-360-app
