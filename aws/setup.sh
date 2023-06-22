sudo apt update
sudo apt install docker.io -y
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

docker --version
docker-compose --version
scp -i "aws/algo.pem" -r aws/algo 
docker-compose up -d