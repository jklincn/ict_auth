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

# Make run file
if [[ -f "src/release.txt" ]]; then
    version=$(cat src/release.txt)
else
    version="self-build $(date +"%Y-%m-%d %H:%M:%S")"
    echo "$version" > src/self-build.txt
fi

if [[ "$version" == self-build* ]]; then
    # local develop, --pigz will be faster 
    makeself --nox11 --pigz src ict_auth.run "ICT Auth (version: $version)" ./install.sh
else
    # github release, --xz will reduce size
    makeself --nox11 --xz src ict_auth.run "ICT Auth (version: $version)" ./install.sh
fi

chmod +x ict_auth.run