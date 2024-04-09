

# running the app local
** create a db:
docker run -d -p 6969:5432 --name postgres-db -e POSTGRES_PASSWORD=mysecretpassword postgres:latest


export DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:6969/postgres"
export MIDDLEWARE="pickarandomsecretkey"


** run the web app
uvicorn main:app  --port 8000 --reload



docker build --build-arg DATABASE_URL=$DATABASE_URL -t fastapi-app .
docker run -p j000:8000 -p 443:443 fastapi-app

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


echo 'export DATABASE_URL="postgresql://postgres:{put the password here}@database-1.{blahlblahblah}.us-west-2.rds.amazonaws.com/postgres"' >> ~/.bashrc
echo 'export MIDDLEWARE="{add a big password here}"' >> ~/.bashrc
source ~/.bashrc


clone the repo: 
git clone https://github.com/mmc102/gimmie_feedback.git


install psql in ubuntu
sudo apt install postgresql postgresql-contrib




sudo apt update
sudo apt install nginx
sudo vim /etc/nginx/sites-available/fastapi.conf


server {
listen 80;
server_name {blah};  # Replace with public IP address of server

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


MAKE SURE YOU UPDATE RULES ON EC2 FOR INBOUND, COPY WORKING GROUP

run deploy script
chmox +x deploy.sh
sudo deploy.sh


# hook up to domain

@    A   N/A   {ip of server public}
www CNAME N/A  reallygreatfeedback.com



sudo apt install certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx

in theory this updates the nginx config, confirm with:

sudo vim /etc/nginx/sites-available/fastapi.conf

I actually had to manually remove the default things and instead copy over the server config from an existing server:

server {
server_name reallygreatfeedback.com www.reallygreatfeedback.com; 

    location / { 
        proxy_pass http://0.0.0.0:8000;  
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }   
    
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/reallygreatfeedback.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/reallygreatfeedback.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot




}


server {
listen 80; 
server_name reallygreatfeedback.com www.reallygreatfeedback.com;

    location / { 
        return 301 https://$host$request_uri;
    }   
    }


sudo systemctl reload nginx









