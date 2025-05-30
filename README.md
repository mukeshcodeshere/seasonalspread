# 🛢️ Dash Spread Calculator – Installation & Deployment Guide

This guide walks you through everything — from local setup to containerizing your Dash app and deploying it on Azure Container Instances (ACI).

---

## 📥 Step 1: Install Git

1. Download Git:
   👉 [https://git-scm.com/downloads](https://git-scm.com/downloads)
2. Follow the installation instructions for your OS.

---

## 📥 Step 2: Install Anaconda

1. Download Anaconda:
   👉 [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution)
2. Follow the installation instructions for your OS.

---

## 📁 Step 3: Navigate to Your Documents Folder

Open Anaconda Prompt (Windows) or terminal (macOS/Linux), then run:

**Windows:**

```bash
cd %USERPROFILE%\Documents
```

**macOS/Linux:**

```bash
cd ~/Documents
```

---

## 📂 Step 4: Clone the Project Repository

```bash
git clone https://github.com/mukeshcodeshere/seasonalspread.git
cd seasonalspread
```

---

## 🐍 Step 5: Create & Activate Python Environment

```bash
conda create --name work python=3.13.2
conda activate work
```

---

## 📦 Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Step 7: Set Up Environment Variables

Create a file `credential.env` in the project root with your sensitive credentials:

```env
DB_SERVER=...
DB_NAME=...
DB_USERNAME=...
DB_PASSWORD=...
USERNAME_LOGIN=...
PASSWORD_LOGIN=...
GvWSUSERNAME=...
GvWSPASSWORD=...
reference_schemaName=...
future_expiry_table_Name=...
tradepricetable=...
contract_margin_table=...
query=...
```

> **Do not commit or share this file publicly!**

The app uses `python-dotenv` to load these automatically.

---

## ▶️ Step 8: Run the App Locally

```bash
python dash_launcher.py
```

Access the app at [http://localhost:8050](http://localhost:8050).

---

# 🐳 Dockerizing Your Dash App

---

## 🔧 Step 9.1: Dockerfile

Use this Dockerfile (in your project root) — includes Microsoft ODBC driver setup:

```dockerfile
FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    locales \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8  
ENV LC_ALL en_US.UTF-8

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

CMD ["python", "dash_launcher.py"]
```

---

## 🐳 Step 9.2: Build Docker Image

```bash
docker build -t seasonalinput-github-dashapp:latest .
```

---

## ▶️ Step 9.3: Run Docker Container Locally

```bash
docker run -p 8050:8050 seasonalinput-github-dashapp:latest
```

Test the app at [http://localhost:8050](http://localhost:8050).

---

## 🐙 Step 9.4: Push Docker Image to Docker Hub

### Login to Docker Hub

```bash
docker login
```

### Tag your image

```bash
docker tag seasonalinput-github-dashapp:latest yourdockerhubusername/seasonalinput-github-dashapp:latest
```

Example:

```bash
docker tag seasonalinput-github-dashapp:latest dreamspartan/seasonalinput-github-dashapp:latest
```

### Push the image

```bash
docker push dreamspartan/seasonalinput-github-dashapp:latest
```

---

## 🧱 Step 9.5: Docker Compose (Optional)

Create `docker-compose.yml` for easier multi-container setups or config:

```yaml
version: '3.8'
services:
  dashapp:
    build: .
    ports:
      - "8050:8050"
    environment:
      - ENV_VAR=value
```

Run with:

```bash
docker-compose up --build
```

---

# ☁️ Deploying to Azure Container Instances (ACI)

---

## 🔹 Step 10.1: Deploy via Azure Portal

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search **Container Instances** → **Create**.
3. Fill Basics: Subscription, Resource Group, Container name, Region.
4. Under **Image Source** select **Public Docker Hub**.
5. Enter image name: `dreamspartan/seasonalinput-github-dashapp:latest`
6. Configure CPU, memory.
7. Open port `8050`.
8. Add environment variables if needed.
9. Create and wait for deployment.
10. Access the app at the assigned IP/DNS on port 8050.

---

## 🔹 Step 10.2: Deploy Using Azure CLI

Make sure you have [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed and logged in:

```bash
az login
```

### Create a resource group (if needed):

```bash
az group create --name myResourceGroup --location eastus
```

### Deploy Container Instance:

```bash
az container create \
  --resource-group myResourceGroup \
  --name dashspreadapp \
  --image dreamspartan/seasonalinput-github-dashapp:latest \
  --cpu 1 --memory 1.5 \
  --ports 8050 \
  --dns-name-label dashspreadapp-unique-label \
  --environment-variables DB_SERVER=... DB_NAME=... DB_USERNAME=... DB_PASSWORD=...
```

* Replace environment variables with your actual values.
* The `--dns-name-label` must be unique across Azure region.

### Check container status:

```bash
az container show --resource-group myResourceGroup --name dashspreadapp --query "{Status:instanceView.state, IP:ipAddress.ip}" --output table
```

### Delete container instance:

```bash
az container delete --resource-group myResourceGroup --name dashspreadapp --yes
```

---

## 🔄 Updating your ACI container

1. Build and push a new Docker image (tag `latest` or use version tags).
2. Use Azure Portal or CLI to update container image and restart container:

```bash
az container restart --resource-group myResourceGroup --name dashspreadapp
```

---

# Summary of Key Commands

| Command                                      | Description                                |
| -------------------------------------------- | ------------------------------------------ |
| `docker build -t imagename .`                | Build Docker image                         |
| `docker run -p 8050:8050 imagename`          | Run container locally                      |
| `docker login`                               | Log in to Docker Hub                       |
| `docker tag imagename username/repo:tag`     | Tag image for Docker Hub                   |
| `docker push username/repo:tag`              | Push image to Docker Hub                   |
| `docker-compose up --build`                  | Run multi-container app via Docker Compose |
| `az login`                                   | Login to Azure CLI                         |
| `az group create --name myResourceGroup ...` | Create Azure resource group                |
| `az container create --name ...`             | Create Azure Container Instance            |
| `az container show --name ...`               | Check container status                     |
| `az container delete --name ...`             | Delete container instance                  |
| `az container restart --name ...`            | Restart container instance                 |
