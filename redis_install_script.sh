wget http://download.redis.io/releases/redis-6.0.3.tar.gz
tar xzf redis-6.0.3.tar.gz
cd redis-6.0.3
make &> /dev/null
mv src/redis-server ..
mv src/redis-cli ..
