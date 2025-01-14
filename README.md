# ims
An assessment from waje solutions


To run your "IMS" app using Docker, follow these instructions:

Prerequisites:
Make sure you have the following installed:

Docker: Install Docker
Docker Compose: Docker Compose comes bundled with Docker Desktop, so if you've installed Docker Desktop, you should already have Docker Compose.
Steps to Run the IMS App:
Clone or Navigate to the Project Directory: Ensure you are in the root directory of your project, which should contain the following files:

Dockerfile
docker-compose.yml
requirements.txt
Your project files (like manage.py and the app folder)
Build the Docker Containers: In your terminal (Command Prompt, PowerShell, or a terminal in the project directory), run:


Copy code
docker-compose up --build


This command will:
Build the Docker images using the Dockerfile.
Set up and start the containers defined in docker-compose.yml (including the ims-web, ims-celery, ims-postgres, and ims-redis services).

Wait for Containers to Start: Once the docker-compose up --build command finishes, Docker will pull any necessary images (like redis, postgres, etc.), build your images, and start the services.

Access the IMS Web App:

Open your browser and go to http://localhost:8001/swagger/. This should display the web application running on the Docker container.
The api will be running on port 8001 on your local machine.
