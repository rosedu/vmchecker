vmchecker-ng
============

Install nodejs and npm:
https://gist.github.com/isaacs/579814
```
echo 'export PATH=$HOME/local/bin:$PATH' >> ~/.bashrc
. ~/.bashrc
mkdir ~/local
mkdir ~/node-latest-install
cd ~/node-latest-install
curl http://nodejs.org/dist/node-latest.tar.gz | tar xz --strip-components=1
./configure --prefix=~/local
make install # ok, fine, this step probably takes more than 30 seconds...
curl https://npmjs.org/install.sh | sh
```


Install meteor:
```
curl https://install.meteor.com | /bin/sh
```

Install meteorite:

```
npm install -g meteorite
```
or
```
sudo -H npm install -g meteorite
```

Go to vmchecker-ng/vmchecker and run
```
mrt
```
