from flask import Flask, render_template
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
import uuid
import os

## Config API
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

# Config model

BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BROKER_URL")  #'kafka:9092'
TOPIC_NAME = os.environ.get("TRANSACTIONS_TOPIC")
MODEL_TOPIC = os.environ.get("MODEL_TOPIC")

# Local config :
# BOOTSTRAP_SERVERS = "localhost:9092"
# TOPIC_NAME = "test"
# MODEL_TOPIC = "model"


@app.route("/")
@cross_origin()
def home():
    return render_template("index.html")


""" Kafka endpoints """


@socketio.on("connect", namespace="/kafka")
def test_connect():
    print('Connected via Websocket ')


def kafkaconsumer():
    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP_SERVERS, auto_offset_reset="latest"
    )
    tp = TopicPartition(TOPIC_NAME, 0)
    # register to the topic
    consumer.assign([tp])

    # obtain the last offset value
    consumer.seek_to_end(tp)
    lastOffset = consumer.position(tp)
    consumer.seek_to_beginning(tp)
    for message in consumer:
        if message.offset == lastOffset -1:
            msg = message.value.decode("utf-8")
            response = chatbot(msg)
            emit("kafkaconsumer", response)
            break
    consumer.close()


@socketio.on("kafkaproducer", namespace="/kafka")
def kafkaproducer(message):
    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
    producer.send(
        TOPIC_NAME,
        value=bytes(str(message), encoding="utf-8"),
        key=bytes(str(uuid.uuid4()), encoding="utf-8"),
    )
    producer.close()
    kafkaconsumer()


if __name__ == "__main__":
    from model import chatbot  
    socketio.run(app, host="0.0.0.0", port=80)

