#!/usr/bin/env bash

# This script makes an AWS Lambda deployment package
# for a provided project.

set -e

# The environment of the python project. Usually it is either dev or prod.
ENVIRONMENT=$1; shift;
# Path to the project to build (e.g. /path/to/my/project).
PROJECT_PATH=$1; shift;
# Dynamically generated root working path (e.g. /tmp/dir/path).
ROOT_PATH=$1; shift;
# A path to a build file (e.g. /tmp/build.zip).
BUILD_PATH=$1; shift;

INSTALL_PATH=${ROOT_PATH}"/install"
VENV_PATH=${ROOT_PATH}"/venv"

# Save the path in which this current script is.
THIS_SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

# Import installation optimization functions.
. "$THIS_SCRIPT_PATH/lambda_optimize.sh"

# Assert that provided project.
if ! [[ -n ${PROJECT_PATH} ]]
then
    echo "Path to the project is not provided!"
    exit 1
fi

set +e

# Clean any failed builds.
rm $BUILD_PATH
rm -rf $VENV_PATH
rm -rf $INSTALL_PATH

set -e

# Create new virtual env.
virtualenv $VENV_PATH --python=python3.6

# Source virtual env.
. $VENV_PATH/bin/activate

# Ensure that the python executable points to a virtual environment.
echo $( which python )

# Ensure pip version 18.1.
python -m pip install pip==18.1

# Install all dependencies
$THIS_SCRIPT_PATH/lambda_install.sh python $ENVIRONMENT $PROJECT_PATH

mkdir $INSTALL_PATH

# Copy all material into a separate install folder.
cp -R $PROJECT_PATH/. $INSTALL_PATH
cp -R $VENV_PATH/lib/python3.6/site-packages/. $INSTALL_PATH

# Optimize according to flags.
while true; do
  case "$1" in
    --omit_boto ) omit_boto "$INSTALL_PATH"; shift ;;
    --omit_wheels ) omit_wheel "$INSTALL_PATH"; shift ;;
    --omit_pip ) omit_pip "$INSTALL_PATH"; shift ;;
    --omit_setup ) omit_setup "$INSTALL_PATH"; shift ;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done

# Create a zip.
current_dir=$( pwd )
cd $INSTALL_PATH
shopt -s dotglob && zip -9 -r $BUILD_PATH *
cd $current_dir

# Delete leftovers.
rm -rf $VENV_PATH
rm -rf $INSTALL_PATH
