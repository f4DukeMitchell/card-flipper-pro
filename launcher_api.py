from flask import Flask
import subprocess
import threading

app = Flask(__name__)

def run_python_server():
    subprocess.run(["python", "api_server.py"])

def run_node_server():
    subprocess.run(["npm", "run", "dev"], cwd="./cardflipper-ui")

@app.route("/start-python", methods=["GET"])
def start_python():
    threading.Thread(target=run_python_server).start()
    return {"status": "Python API server starting..."}

@app.route("/start-node", methods=["GET"])
def start_node():
    threading.Thread(target=run_node_server).start()
    return {"status": "Svelte UI server starting..."}

if __name__ == "__main__":
    app.run(port=5001)
