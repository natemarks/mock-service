#!/usr/bin/env bash
set -Eeuoxv pipefail
yum install -y unzip nc
curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip
unzip awscliv2.zip
sudo ./aws/install

sudo amazon-linux-extras install postgresql10
