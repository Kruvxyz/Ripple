# 〰️ Ripple 
Ripple is a powerful yet intuitive, super-lean orchestrator designed for seamless personal data collection workflows — all at zero cost. Ripple streamlines data scraping, processing, and ML flows with ease and efficiency, running everything through Docker containers for a modular, flexible setup.

## Features
- **Simple & Lean**: Minimal setup and resource-efficient design, making orchestration straightforward and accessible.
- **Comprehensive Data Workflows**: Manage scraping, data processing, and machine learning pipelines with ease.
- **Cost-Free**: Ripple was built to run on a server with minimum resources. Run it on AWS free-tier or on your old PC.

## Components
- **UI**: A user-friendly interface for managing and monitoring workflows.
- **Backend (BE)**:
Flask: Acts as the API layer, serving requests and managing data interactions.
Routine Manager: Coordinates data collection, processing, and ML tasks with a focus on simplicity and efficiency.

## Commands
- **start**: start a task (task will calculate new waiting)
- **cancle**: kill task
- [P1] **execute**: stop task and run immiate
- [P1] **restart**: cancle and start task
- [P1] **pause**: freaze task when computation was completed 
- [P1] **resume**: return to freezed task

## Getting Started
Ripple is built to operate fully within Docker, ensuring easy deployment, isolation, and scalability for every component. Just spin up the containers, and you're ready to start orchestrating.

To go to the directory and run Docker Compose, you can follow these steps:

1. Open your terminal or command prompt.
2. Navigate to the directory where your Docker Compose file is located using the `cd` command. For example, if your file is in the `/RIPPLE DIRECTORY` directory, you would run:
```
cd /RIPPLE DIRECTORY
```
3. Once you are in the correct directory, you can run the Docker Compose command to start the containers. Use the following command:
```
docker compose up --build
```
This will build and start the containers specified in your Docker Compose file.

That's it! You are now ready to start orchestrating with Ripple using Docker Compose.
