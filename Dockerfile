# # Use official Ubuntu base image
# FROM ubuntu:22.04

# # Set noninteractive frontend for apt
# ENV DEBIAN_FRONTEND=noninteractive

# # Install prerequisites and dependencies for ODBC and Python
# RUN apt-get update && apt-get install -y \
#     curl \
#     gnupg \
#     apt-transport-https \
#     ca-certificates \
#     unixodbc \
#     unixodbc-dev \
#     libodbc1 \
#     libssl3 \
#     libgssapi-krb5-2 \
#     locales \
#     python3 \
#     python3-pip \
#     && rm -rf /var/lib/apt/lists/*

# # Configure locale
# RUN locale-gen en_US.UTF-8
# ENV LANG=en_US.UTF-8  
# ENV LC_ALL=en_US.UTF-8

# # Add Microsoft ODBC Driver 18 repo and key
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
#     curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# # Install msodbcsql18
# RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# # Install optional tools (sqlcmd, bcp) - remove if not needed
# RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18 && \
#     echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc

# # Install Python dependencies
# COPY requirements.txt /tmp/
# RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# # Copy your Dash app code into the container
# WORKDIR /app
# COPY . /app

# # Expose the port your Dash app runs on (default 8050)
# EXPOSE 8050

# # Command to run the Dash app
# CMD ["python3", "dash_launcher.py"]


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
