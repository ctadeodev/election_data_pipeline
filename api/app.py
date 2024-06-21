import os
import json
import logging

from kafka import KafkaProducer
from flask import Flask, request, jsonify

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)


producer = KafkaProducer(
    bootstrap_servers=os.environ['KAFKA_BROKER'],
    api_version=(2, 5, 0),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    producer.send('registration', value=data)
    app.logger.debug('Produced registration event: %s', str(data))
    return jsonify({"status": "success", "message": "Registration event produced"}), 200

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    producer.send('vote', value=data)
    app.logger.debug('Produced vote event: %s', str(data))
    return jsonify({"status": "success", "message": "Vote event produced"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
