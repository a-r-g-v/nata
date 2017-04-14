from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/v1')
def index():
    return jsonify({'success': 'poe'})

app.run(host='0.0.0.0', port=80)
