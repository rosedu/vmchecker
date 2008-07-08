#!/bin/bash

echo "<pre>"
find ~/teme/checker -name file.zip | cut -f7- -d/
ssh so@sanctuary 'cat job_errors | cut -c 1-80' 
echo "</pre>"