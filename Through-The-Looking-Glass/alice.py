import os
import requests
from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
# Deprecated
# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

BACKEND_URL = "http://localhost:5001/process"  # Backend service URL

# Set up Tracer
APP_NAME = os.path.splitext(os.path.basename(__file__))[0]

# Set up Tracer
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({"service.name": APP_NAME})
    )
)
tracer = trace.get_tracer(APP_NAME)

# Configure Jaeger Exporter
# Deprecated
# jaeger_exporter = JaegerExporter(
#     agent_host_name="localhost",
#     agent_port=6831,
# )
jaeger_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces"
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Initialize Flask App
app = Flask(APP_NAME)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()  # Instrument outgoing HTTP requests

@app.route("/")
def index():
    with tracer.start_as_current_span(APP_NAME):
        response = requests.get(BACKEND_URL)  # Call backend
        return f"Frontend received: {response.text}"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
