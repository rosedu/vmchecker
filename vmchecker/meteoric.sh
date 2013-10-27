#!/bin/bash


# ### --- SETUP ----------------------

# # Does NOT need to be root user:

# # create directory
# mkdir -p ~/.nodes && cd ~/.nodes

# # download latest Node.js distribution
# curl -O http://nodejs.org/dist/v0.10.13/node-v0.10.13-linux-x64.tar.gz

# # unpack it
# tar -xzf node-v0.10.13-linux-x64.tar.gz

# # discard it
# rm node-v0.10.13-linux-x64.tar.gz

# # rename unpacked folder
# mv node-v0.10.13-linux-x64 0.10.13

# # create symlink
# ln -s 0.10.13 current

# # add path to PATH
# export PATH="~/.nodes/current/bin:$PATH"

# # check
# node --version
# npm --version

# # Needs to be root user (apply "sudo" if not at root shell)

# apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
# echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/10gen.list
# apt-get update
# apt-get install mongodb-10gen

source "$PWD/meteoric.config.sh"

if [ -z "$GIT_URL" ]; then
	echo "You need to create a conf file named meteoric.config.sh"
	exit 1
fi

###################
# You usually don't need to change anything here –
# You should modify your meteoric.config.sh file instead.
#

APP_DIR=/root/vmchecker-ng/

if [ -z "$ROOT_URL" ]; then
    ROOT_URL=http://$APP_HOST
fi


if [ -z "$MONGO_URL" ]; then
	MONGO_URL=mongodb://localhost:27017/$APP_NAME
fi

if [ -z "$PORT" ]; then
    PORT=80
fi

if $METEORITE; then
	METEOR_CMD=mrt
	METEOR_OPTIONS=''
else
	METEOR_CMD=meteor
	if [ -z "METEOR_RELEASE" ]; then
		echo "When using meteor and not Meteorite, you have to specify $METEOR_RELEASE in the config file"
		exit 1
	fi
	METEOR_OPTIONS="--release $METEOR_RELEASE"
fi

if [ -z "$EC2_PEM_FILE" ]; then
	SSH_HOST="root@$APP_HOST" SSH_OPT=""
else
	SSH_HOST="ubuntu@$APP_HOST" SSH_OPT="-i $EC2_PEM_FILE"
fi


if [ -z "$APP_PATH" ]; then
	APP_PATH="."
fi


if [ -z "$GIT_BRANCH" ]; then
	GIT_BRANCH="master"
fi

DEPLOY="
cd $APP_DIR;
cd $APP_NAME;
echo Updating codebase;
sudo git fetch origin;
sudo git checkout $GIT_BRANCH;
sudo git pull;
cd $APP_PATH;
if [ "$FORCE_CLEAN" == "true" ]; then
    echo Killing node;
    sudo killall node;
    echo Killing services;
    kill -9 `ps ax | grep services.py | head -n1 | awk '{print $1;}'`;
fi;
export MONGO_URL=$MONGO_URL;
export ROOT_URL=$ROOT_URL;
if [ -n "$MAIL_URL" ]; then
    export MAIL_URL=$MAIL_URL;
fi;
export PORT=$PORT;
"

if [ -n "$PRE_METEOR_START" ]; then
    DEPLOY="$DEPLOY $PRE_METEOR_START"
fi;

DEPLOY="$DEPLOY
echo Starting server;
nohup python services.py &;
nohup mrt &;
"

case "$1" in
deploy)
	ssh $SSH_OPT $SSH_HOST $DEPLOY
	;;
*)
	cat <<ENDCAT
meteoric [action]

Available actions:
deploy  - Deploy the app to the server
ENDCAT
	;;
esac

