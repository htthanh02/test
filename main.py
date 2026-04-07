import http.server
import subprocess
import urllib.parse
import urllib.request
import re
import os

PORT = 9999
# Define the path where your local scripts are stored
LOCAL_SCRIPT_PATH = "./scripts"
WHITELISTED_USER = "Digibrary"
WHITELISTED_REPO = "maintenance-scripts"

class ScriptExecHandler(http.server.BaseHTTPRequestHandler):
    
    def validate_github_url(self, url):
        # Regex to capture: username (1), repo (2)
        pattern = r"https://raw\.githubusercontent\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+)/.*"
        match = re.match(pattern, url)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)
        
        output = ""
        status = 200

        try:
            if parsed_path.path == "/local":
                # Implementation of Switch-Case for local scripts
                script_name = params.get("name", [None])[0]
                
                match script_name:
                    case "update":
                        cmd = [f"{LOCAL_SCRIPT_PATH}/sys_update.sh"]
                    case "cleanup":
                        cmd = [f"{LOCAL_SCRIPT_PATH}/cleanup.sh"]
                    case "health":
                        cmd = [f"{LOCAL_SCRIPT_PATH}/service_health.sh"]
                    case _:
                        status = 404
                        output = "Error: Local script not found in switch-case."
                        cmd = None

                if cmd:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    output = result.stdout + result.stderr

            elif parsed_path.path == "/remote":
                github_url = params.get("url", [None])[0]
                user, repo = self.validate_github_url(github_url)

                if user and repo and user == WHITELISTED_USER and repo == WHITELISTED_REPO:
                    print(f"Executing remote script from User: {user}, Repo: {repo}")
                    
                    # Fetch and execute
                    with urllib.request.urlopen(github_url) as response:
                        script_content = response.read().decode('utf-8')
                        # Execute the fetched script via bash stdin
                        result = subprocess.run(["bash"], input=script_content, capture_output=True, text=True)
                        output = f"Executed {repo} by {user}:\n\n" + result.stdout + result.stderr
                else:
                    status = 400
                    output = "Invalid GitHub Raw URL. Must be https://raw.githubusercontent.com/Digibrary/maintenance-scripts"

            else:
                status = 404
                output = "Endpoint not found. Use /local?name=... or /remote?url=..."

        except Exception as e:
            status = 500
            output = f"Internal Server Error: {str(e)}"

        self.send_response(status)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(output.encode())

if __name__ == "__main__":
    if not os.path.exists(LOCAL_SCRIPT_PATH):
        os.makedirs(LOCAL_SCRIPT_PATH)
    
    server = http.server.HTTPServer(("0.0.0.0", PORT), ScriptExecHandler)
    print(f"Server running on port {PORT}...")
    server.serve_forever()