#!/usr/bin/env bash
set -Eeuoxv pipefail
# the prefix forces install in the current directory
# if npm doesn't find node_modules in the current directory, it looks in the home directory
# this is a problem on pipeline agents because the package ends up getting installed in
# $HOME/node_modules


if [[ $# -ne 1 ]]; then
  # if the version isn't provided, install latest and check installed version
  npm install --prefix ./ aws-cdk
  CDK_VERSION=$(npm list --json  | jq -r '.dependencies."aws-cdk".version')
else
  # otherwise install provided version
  CDK_VERSION="${1}"
  npm install --prefix ./ "aws-cdk@${CDK_VERSION}"
fi

# remove and update aws cdk entries in requirements.txt
sed -i '/aws-cdk-lib==/d' requirements.txt
echo "aws-cdk-lib==${CDK_VERSION}" >> requirements.txt