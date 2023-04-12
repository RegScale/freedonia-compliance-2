from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return jsonify({'status': 'OK'})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'})

@app.route('/makeoscal', methods=['GET'])
def make_oscal():
    result = subprocess.run(["python", "make_oscal.py"], capture_output=True, text=True)
    return jsonify({'status': 'OK', 'content': result.stdout})

@app.route('/upload', methods=['GET'])
def upload():
    cmd = 'find /Users/gregelinadmin/Documents/workspace/complianceintegration/output/oscal -type f -name "*.json" -exec python regscale.py oscal component {} \\;'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return jsonify({'status': 'OK', 'content': result.stdout})

if __name__ == '__main__':
    app.run(port=5050)