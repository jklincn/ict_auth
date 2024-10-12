#!/usr/bin/env bash
set -e

# install pip and makeself
sudo apt-get install python3-pip makeself

# install selenium
python3 -m pip install selenium

# get binary file
version="125.0.6422.141"
selenium_manager="$(python -c "import sys; print([p for p in sys.path if 'site-packages' in p][0] + '/selenium/webdriver/common/linux/selenium-manager')")"
$selenium_manager \
    --browser chrome \
    --browser-version "${version}" \
    --driver chromedriver \
    --driver-version "${version}" \
    --cache-path $(pwd)/src \
    --force-browser-download \
    --avoid-stats \
    --debug

# get wheel file, compatible with python3.8
mkdir -p src/wheel
python3 -m pip download -d src/wheel \
    --platform manylinux1_x86_64 \
    --python-version 38 \
    --implementation cp \
    --abi cp38 \
    --only-binary=:all: \
    selenium

# make run file
makeself --nox11 --xz src ict_auth.run "ICT Internet Authentication without GUI support" ./setup.sh