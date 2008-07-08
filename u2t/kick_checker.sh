#!/bin/bash

echo "<pre>"
ssh so@sanctuary 'nohup /runchecker.sh "cd ~/ && ./checker.sh" &>/dev/null < /dev/null &' 
echo "</pre>"