from flask import Flask, request
from flask_cors import CORS, cross_origin
import os

from services.home_activities import *
from services.notifications_activities import *
from services.user_activities import *
from services.create_activity import *
from services.create_reply import *
from services.search_activities import *
from services.message_groups import *
from services.messages import *
from services.create_message import *
from services.show_activity import *

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Initialize Flask app
app = Flask(__name__)

# Get the frontend URL from environment variables
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Configure CORS to allow requests from the frontend
CORS(app, resources={r"/api/*": {"origins": frontend_url}})

# Set up OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure OTLP exporter for Honeycomb
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://otel-collector:4317'),
    headers={
        "x-honeycomb-team": os.getenv('HONEYCOMB_API_KEY')
    }
)

# Add the exporters to the tracer
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask app with OpenTelemetry
FlaskInstrumentor().instrument_app(app)

@app.route("/api/message_groups", methods=['GET'])
def data_message_groups():
    user_handle = 'greyalora'
    model = MessageGroups.run(user_handle=user_handle)
    if model['errors'] is not None:
        return model['errors'], 422
    else:
        return model['data'], 200

@app.route("/api/messages/@<string:handle>", methods=['GET'])
def data_messages(handle):
    user_sender_handle = 'greyalora'
    user_receiver_handle = request.args.get('user_reciever_handle')

    model = Messages.run(user_sender_handle=user_sender_handle, user_receiver_handle=user_receiver_handle)
    if model['errors'] is not None:
        return model['errors'], 422
    else:
        return model['data'], 200

@app.route("/api/messages", methods=['POST', 'OPTIONS'])
@cross_origin()
def data_create_message():
    user_sender_handle = 'greyalora'
    user_receiver_handle = request.json['user_receiver_handle']
    message = request.json['message']

    model = CreateMessage.run(message=message, user_sender_handle=user_sender_handle, user_receiver_handle=user_receiver_handle)
    if model['errors'] is not None:
        return model['errors'], 422
    else:
        return model['data'], 200

@app.route("/api/activities/home", methods=['GET'])
def data_home():
    data = HomeActivities.run()
    return data, 200

@app.route("/api/activities/notifications", methods=['GET'])
def data_notifications():
    data = NotificationsActivities.run()
    return data, 200

@app.route("/api/activities/@<string:handle>", methods=['GET'])
def data_handle(handle):
    model = UserActivities.run(handle)
    if model['errors'] is not None:
        return model['errors'], 422
    else:
        return model['data'], 200

@app.route("/api/activities/search", methods=['GET'])
def data_search():
    term = request.args.get('term')
    model = SearchActivities.run(term)
    if model['errors'] is not None:
        return model['errors'], 422
    else:
        return model['data'], 200

@app.route("/api/activities", methods=['POST', 'OPTIONS'])
@cross_origin()
def data_activities():
    user_handle = 'greyalora'
    message = request.json['message']
    ttl = request.json['ttl']
    model = CreateActivity.run(message, user_handle, ttl)
    if model['errors'] is not None:
        return model['errors'], 422
    else:
        return model['data'], 200

@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
def data_show_activity(activity_uuid):
    data = ShowActivity.run(activity_uuid=activity_uuid)
    return data, 200

@app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST', 'OPTIONS'])
@cross_origin()
def data_activities_reply(activity_uuid):
    user_handle = 'greyalora'
    message = request.json['message']
    model = CreateReply.run(message, user_handle, activity_uuid)
    if model['errors'] is not None:
        return model['errors'], 422
    else:
        return model['data'], 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)