==============================
Setting up and hacking the GUI
==============================

sudo apt-get install apache2
sudo apt-get install libapache2-mod-python
sudo apt-get install git
sudo apt-get install python-paramiko
sudo apt-get install python-ldap
git clone https://github.com/vmchecker/vmchecker.git (after the merge | https://github.com/valenting/vmchecker.git is needed)
cd vmchecker
sudo python setup.py install
cd ~
mkdir storer-course1
cd storer-course1
vmchecker-init-course storer
cd tests
wget http://swarm.cs.pub.ro/~vgosu/vmchecker/1-minishell-linux.zip
wget http://swarm.cs.pub.ro/~vgosu/vmchecker/1-minishell-windows.zip
cd ..
echo '{"auth": {"user1":"password1"}}' > auth_file.json
sudo sh -c 'echo C1:`pwd`/config > /etc/vmchecker/config.list'
cd /var/www
sudo wget http://swarm.cs.pub.ro/~vgosu/vmchecker/ui.tar.gz
sudo tar -zxvf ui.tar.gz
sudo sed -i 's&<Directory /var/www/>&<Directory /var/www/>\nAddHandler mod_python .py\nPythonHandler mod_python.publisher\nPythonDebug On\n&g' /etc/apache2/sites-available/default

