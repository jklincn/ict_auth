#!/usr/bin/env bash
set -e

# install pip and makeself
sudo apt-get install python3-pip makeself pigz

# install selenium
python3 -m pip install -U selenium

# get binary file
version="125.0.6422.141"
echo "$version" > src/browser_version.txt
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

# Make run file
if [[ -f "src/release.txt" ]]; then
    VERSION=$(cat src/release.txt)
else
    VERSION="self-build ($(date +"%Y-%m-%d %H:%M:%S"))"
    echo "$VERSION" > src/self-build.txt
fi

if [[ "$VERSION" == self-build* ]]; then
    # local develop, --pigz will be faster 
    makeself --nox11 --pigz src ict_auth.run "ICT Auth - ${VERSION}" ./install.sh
else
    # github release, --xz will reduce size
    makeself --nox11 --xz src ict_auth.run "ICT Auth - ${VERSION}" ./install.sh
fi