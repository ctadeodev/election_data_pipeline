from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json
import os

app = Flask(__name__)

producer = KafkaProducer(
    bootstrap_servers=os.environ['KAFKA_BROKER'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    producer.send('registration', value=data)
    return jsonify({"status": "success", "message": "Registration event produced"}), 200

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    producer.send('vote', value=data)
    return jsonify({"status": "success", "message": "Vote event produced"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
