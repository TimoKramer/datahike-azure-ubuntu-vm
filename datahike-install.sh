# Install Java
# Install Java
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get install -y $1
sudo apt-get -y update --fix-missing
sudo apt-get install -y $1

# Install datahike-server
sudo wget https://raw.githubusercontent.com/technomancy/leiningen/stable/bin/lein --output-document=/usr/local/bin/lein
sudo chmod a+x /usr/local/bin/lein
sudo mkdir -p /var/www/datahike-server
cd /var/www/datahike-server
sudo chown ${2}. .
git clone https://github.com/replikativ/datahike-server.git .
/usr/local/bin/lein uberjar
java -jar ./target/datahike-server-0.1.0-SNAPSHOT-standalone.jar &

sleep 10

if netstat -tulpen | grep 3000
then
  exit 0
fi
