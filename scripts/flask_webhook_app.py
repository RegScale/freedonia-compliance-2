from flask import Flask, jsonify
import subprocess
import settings

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return jsonify({'status': 'OK'})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'})

@app.route('/makeoscal', methods=['GET'])
def make_oscal():
    result = subprocess.run(["python3", "scripts/make_oscal.py"], capture_output=True, text=True)
    return jsonify({'content': result.stdout, 'status': 'OK'})

@app.route('/upload', methods=['GET'])
def upload():
    cmd = f'find {settings.OUTPUTDIR} -type f -name "*.json" -exec python3 regscale.py oscal component {{}} \\;'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        return jsonify({'content': result.stdout, 'status': 'OK'})
    else:
        return jsonify({'content': "No stdout", 'status': 'Error'})

if __name__ == '__main__':
    app.run(host=settings.FLASK_HOST, port=settings.FLASK_PORT)