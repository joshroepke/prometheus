# Flask App with Prometheus

### How to build and run the Docker container locally

There is a Docker Compose file that provides instructions to build and run the Flask App and Prometheus instances locally. 

This will require that you have Docker installed locally. Follow these [Get Docker](https://docs.docker.com/get-docker/) instructions if not already installed. 

Once Docker is installed run the following command from the `flask-app` directory 

```bash
docker-compose up --build -d 
```

Once the containers have been build and are running the Flask app can be accessed on following endpoints

- [api/message](http://localhost:8080/api/message)

- [custom-metrics](http://localhost:8080/custom-metrics)

### How to setup and access the Prometheus instance 

Prometheus will be built following running Docker Compose and can be accessed at `http://localhost:9090`

- [Prometheus](http://localhost:9090/targets?search=)

### Assumptions made during implementation

- Kubernetes manifests are for reference of how to deploy to Kubernetes. I have tested the manifest files against a local minikube cluster and verified functionality using an image pushed to public repository. This was performed by the following; 

```bash
kubectl apply -f k8s/
minikube service flask-app-service
minikube service prometheus
```

- Logging can be sent to Console only and not to File. 

### Important improvements 

If given more time, I would include a `/health` endpoint and use this endpoint to implement `liveness` and `readiness` probes within the Deployment object. 

### CI/CD 

Given that this project is just currently setup for local development with local k8s cluster at this time I would create a `Makefile` to automate the following workflows
- build image and push to registry 
- setup k8s cluster and deploy k8s manifest files
- teardown k8s cluster
