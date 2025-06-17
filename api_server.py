from flask import Flask, jsonify
from services.main_logic import scan_items

app = Flask(__name__)

@app.route('/scan')
def scan():
    items = scan_items()
    return jsonify(items)

if __name__ == "__main__":
    app.run(port=5000)
