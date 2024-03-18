# running the app local
** create a db:
docker run -d -p 6969:5432 --name postgres-db -e POSTGRES_PASSWORD=mysecretpassword postgres:latest


export DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:6969/postgres"


** run the web app
uvicorn main:app  --port 8000 --reload



docker build --build-arg DATABASE_URL=$DATABASE_URL -t fastapi-app .
docker run -p 8000:8000 -p 443:443 fastapi-app

# install docker on ubuntu ec2 instance
sudo apt update
sudo apt install -y \
apt-transport-https \
ca-certificates \
curl \
gnupg \
lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo docker --version
sudo usermod -aG docker $USER


# set an env varaible for the db url
echo 'export DATABASE_URL="postgresql://postgres:{put the password here}@database-1.cxmow2wac1p0.us-west-2.rds.amazonaws.com/postgres"' >> ~/.bashrc


# then run the build and run commands from above


# set up nginx as a reverse proxy

sudo apt update
sudo apt install nginx
sudo nano /etc/nginx/sites-available/fastapi.conf


server {
listen 80;
server_name 54.185.59.109;  # Replace with public IP address of server

    location / {
        proxy_pass http://0.0.0.0:8000;  
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    }
    sudo ln -s /etc/nginx/sites-available/fastapi.conf /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx


# go to the website and it should work


# hook up to domain


buy a domain

set the following records:

@    A   N/A   54.185.59.109

www CNAME N/A  reallygreatfeedback.com


save and now go back to nginx on server


update the server: 


server {
listen 80;
server_name reallygreatfeedback.com www.reallygreatfeedback.com; 

    location / {
        proxy_pass http://0.0.0.0:8000;  
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    }



sudo systemctl reload nginx



# enable https (first need to attach this to a domain)

sudo apt install certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx

in theory this updates the nginx config, confirm with:

sudo vim /etc/nginx/sites-available/fastapi.conf


sudo systemctl reload nginx

!!IMPORTANT

make sure you go to aws and add an inbound rule for https trafffic on port 443


# setup a deploy process in the ec2 instance

deploy.sh

```
#!/bin/bash
cd
cd gimmie_feedback
git pull origin main

docker build --build-arg DATABASE_URL=$DATABASE_URL -t fastapi-app .


docker stop fastapi-container
docker rm fastapi-container

docker run -d -p 8000:8000 --name fastapi-container fastapi-apdocker run -d -p 8000:8000 --name fastapi-container fastapi-app
p
```


after i deployed the ip of the container was no longer the same, so the nginx config was busted

a valid way to test the app is running in the container:

curl http://localhost:8000



`
