#!/bin/sh
git add *
git commit -a -m "$1"
git pull
git commit -a -m "$1"
git push origin master
echo $1
