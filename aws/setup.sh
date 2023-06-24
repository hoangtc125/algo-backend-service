sudo apt update
sudo apt install docker.io -y
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker --version
docker-compose --version

sudo chown -R $USER:$USER /home/hoang/dist
sudo chmod -R 755 /home/hoang

scp -i "aws/algo.pem" -r aws/algo 
docker-compose up -d

sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
sudo ufw allow 'Nginx Full'
sudo nano /etc/nginx/conf.d/algo.conf
server {
    listen 80;
    server_name 74.235.240.39;

    root /home/hoang/dist;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets {
        try_files $uri $uri/ =404;
    }

    location ~ \.css {
        add_header Content-Type text/css;
    }

    location ~ \.js {
        add_header Content-Type application/x-javascript;
    }
}
sudo nginx -t
sudo systemctl restart nginx

wget https://github.com/hoangtc125/algo-backend-service/archive/refs/heads/master.zip
sudo apt install unzip -y
unzip master.zip
