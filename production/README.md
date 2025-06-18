# Deploying a FastAPI ML Model to a Public Cloud Kubernetes Cluster

This guide provides step-by-step instructions for deploying the containerized FastAPI application to a public cloud Kubernetes provider (like GKE, EKS, or AKS) using an NGINX Ingress Controller to expose the service to the internet.

## High-Level Steps

1.  **Build and Push** the Docker image to an online container registry (Docker Hub).
2.  **Install an Ingress Controller** into your cluster to manage external traffic.
3.  **Deploy the Application** using the updated Kubernetes manifests (`deployment.yaml`, `service.yaml`, `ingress.yaml`).
4.  **Test the Application** by sending requests to the Ingress Controller's public IP address.

---

## Step 1: Build and Push the Docker Image

Your cloud cluster needs to fetch your application's image from an online registry. We'll use Docker Hub.

1.  **Log in to Docker Hub**
    If you haven't already, create an account on [hub.docker.com](https://hub.docker.com). Then, log in from your terminal:
    ```bash
    docker login
    ```

2.  **Tag Your Image**
    Re-tag the image you built previously with your Docker Hub username. This formats the image name for the registry.
    ```bash
    # IMPORTANT: Replace 'your_dockerhub_username' with your actual username
    docker tag fastapi-app:1.0 your_dockerhub_username/fastapi-app:1.0
    ```

3.  **Push the Image to Docker Hub**
    Upload the tagged image to the registry.
    ```bash
    # IMPORTANT: Replace 'your_dockerhub_username' with your actual username
    docker push your_dockerhub_username/fastapi-app:1.0
    ```
    The image is now publicly available for your cluster to pull.

---

## Step 2: Install an NGINX Ingress Controller

An Ingress Controller is the component that fulfills Ingress rules, typically by running a load balancer. This is a one-time setup for your cluster.

Apply the recommended manifest from the official NGINX Ingress project. This command sets up everything needed.

```bash
kubectl apply -f [https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml](https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml)
```

Wait a minute or two for your cloud provider to provision a public IP address for the load balancer. You can check its status by running:

```bash
kubectl get svc -n ingress-nginx
```

Look for the `ingress-nginx-controller` service and wait until an `EXTERNAL-IP` is assigned.

## Step 3: Deploy the FastAPI Application

Now, apply your updated application manifests to the cluster.
Important: Make sure you have updated `deployment.yaml` to use the image you pushed to Docker Hub `(your_dockerhub_username/fastapi-app:1.0)`.

```bash
# Apply the deployment, service, and new ingress rule
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```

---

## Step 4: Test the Live Application

1.  **Find Your Ingress IP Address**
    Get the public IP address of the Ingress load balancer you created in Step 2.
    ```bash
    export INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    echo "Your application IP is: $INGRESS_IP"
    ```

2.  **Test the Prediction Endpoint**
    We will use `curl` to send a request to the Ingress IP. Because our `ingress.yaml` specifies a host (`fastapi.example.com`), we must include a `Host` header in our request so the Ingress knows where to route the traffic.

    ```bash
    curl -X POST "http://$INGRESS_IP/predict" \
    -H "Host: fastapi.example.com" \
    -H "Content-Type: application/json" \
    -d '{
      "sepal_length": 6.7,
      "sepal_width": 3.1,
      "petal_length": 4.7,
      "petal_width": 1.5
    }'
    ```

    **Expected Output (for the data above, which is a versicolor):**
    ```json
    {"predicted_species":"versicolor","predicted_class_id":1}
    ```

### (Optional) Using DNS

For a production setup, you would create a DNS 'A' record for `fastapi.example.com` (or your chosen domain) that points to the `$INGRESS_IP`. Once DNS propagates, you could make requests without the `Host` header: `curl -X POST http://fastapi.example.com/predict ...`

---
## Cleanup

When you are finished, you can remove the application resources from your cluster.

```bash
kubectl delete -f ingress.yaml
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
```

To remove the Ingress controller itself, run:

```
kubectl delete -f [https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml](https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml)
```
