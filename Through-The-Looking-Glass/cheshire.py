import os
from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
# Deprecated
# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Set APP_NAME reading file name
APP_NAME = os.path.splitext(os.path.basename(__file__))[0]

# Set up Tracer
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource(attributes={"service.name": APP_NAME})
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

# Define the /process path for the application
@app.route("/process")
def process_request():
    with tracer.start_as_current_span(APP_NAME):
        return "Processed data in Backend!"

# Execute Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5001)

