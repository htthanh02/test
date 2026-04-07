import http.server
import subprocess
import urllib.parse
import urllib.request
import re
import os

url = "https://raw.githubusercontent.com/Digibrary/maintenance-scripts/main/../../../../../../../htthanh02/htthanh02.github.io/refs/heads/main/index.html"
with urllib.request.urlopen(url) as response:
    content = response.read().decode('utf-8')
    print(content)