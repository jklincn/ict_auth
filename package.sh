#!/usr/bin/env bash
set -e

# install pip and makeself
sudo apt-get install python3-pip makeself

# install selenium
python3 -m pip install selenium

# get binary file
version="125.0.6422.141"
selenium_manager="$(python3 -c "import sys; print([p for p in sys.path if 'site-packages' in p][0] + '/selenium/webdriver/common/linux/selenium-manager')")"
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
for version in 3.8 3.9 3.10 3.11 3.12; do
    python3 -m pip download -d src/wheel \
        --platform manylinux2014_x86_64 \
        --python-version $version \
        --only-binary=:all: \
        selenium
done

# make run file
if [[ -f src/version.txt ]]; then
    VERSION=$(cat src/version.txt)
else
    VERSION="self-build"
    echo "$VERSION" > src/version.txt
fi
makeself --nox11 --xz src ict_auth.run "ICT Auth - ${VERSION}" ./setup.sh