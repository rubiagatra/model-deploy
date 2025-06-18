# FastAPI on Kubernetes (Minikube) Deployment

This project demonstrates how to containerize a simple Python FastAPI application using Docker and deploy it to a local Kubernetes cluster managed by Minikube.
The guide provides a full, step-by-step walkthrough from setting up the project files to accessing the live API endpoints on your local machine.

## Prerequisites

Before you begin, ensure you have the following tools installed on your system:

-   **Docker**: To build the container image. [Install Docker](https://docs.docker.com/get-docker/)
-   **Minikube**: To run a local Kubernetes cluster. [Install Minikube](https://minikube.sigs.k8s.io/docs/start/)
-   **kubectl**: The Kubernetes command-line tool. [Install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

## Project Structure

Your project directory should contain the following files:

```
.
├── Dockerfile          # Defines the steps to build our application's container image.
├── main.py             # The Python source code for the FastAPI application.
├── pyproject.toml      # Defines project metadata and Python dependencies.
├── deployment.yaml     # Kubernetes manifest to create a Deployment.
└── service.yaml        # Kubernetes manifest to expose the Deployment via a Service.
```
## Step-by-Step Deployment Guide

Follow these steps to build the Docker image and deploy the application to your Minikube cluster.

### 1. Start Your Minikube Cluster

Open your terminal and start the Minikube cluster.

```bash
minikube start
```
### 2. Set Minikube's Docker Environment
To build the Docker image directly inside Minikube's environment (avoiding the need for a separate registry), point your terminal's Docker daemon to the one inside Minikube.

```
eval $(minikube -p minikube docker-env)
```
Note: You will need to do this for every new terminal session. To disconnect, run eval $(minikube -p minikube docker-env -u).

### 3. Build the Docker ImageWith your terminal in the root of the project directory, build the Docker image. We will tag it as fastapi-app:1.0.

```
docker build -t fastapi-app:1.0 .
```

### 4. Create the Kubernetes Deployment and ServiceApply the Kubernetes manifest files to create the Deployment and Service resources. The Deployment will manage our application's pods, and the Service will make them accessible.

```
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### 5. Verify the DeploymentCheck the status of your pods to ensure they are running correctly. You should see two fastapi-deployment pods in the Running state.

```
kubectl get pods
Expected output:NAME                                  READY   STATUS    RESTARTS   AGE
fastapi-deployment-65c69476cd-abcde   1/1     Running   0          60s
fastapi-deployment-65c69476cd-fghij   1/1     Running   0          60s
```

## How to Access the API
You can access your running FastAPI service in two primary ways with Minikube.

### Quick Access (Using minikube service)

This is the easiest way to get a temporary URL to your service. Run the command and it will open a tunnel in your terminal.

```
minikube service fastapi-service
```
This command provides a URL (e.g., http://127.0.0.1:54321) and will stay active until you press Ctrl+C. You will need to open a new terminal to use this URL.

### Test the root endpoint
```
export API_URL={URL_FROM_MINIKUBE_SERVICE}
curl $API_URL/
# Expected Output: {"Hello":"World"}

# Test the GET item endpoint
curl $API_URL/items/42?q=testquery
# Expected Output: {"item_id":42,"q":"testquery"}

# Test the PUT item endpoint
curl -X PUT "$API_URL/items/42" \
-H "Content-Type: application/json" \
-d '{"name": "My New Item", "price": 19.99}'
# Expected Output: {"item_name":"My New Item","item_id":42}
```

## Cleanup
When you are finished, you can remove the created resources from your cluster and stop Minikube.

1. Delete Kubernetes ResourcesDelete the service and deployment you created.

```
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
```
2. Stop MinikubeStop the local Kubernetes cluster.

```
minikube stop
```

