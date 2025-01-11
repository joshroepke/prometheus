from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter
import logging
import os

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter


# Setup Flask 
app = Flask(__name__)

# Setup Prometheus Metrics with a custom endpoint
metrics = PrometheusMetrics(app, path='/custom-metrics')

# Setup logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up OpenTelemetry tracing
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "flask-app"}))
)
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# # Set up OpenTelemetry metrics
meter_provider = MeterProvider()
metrics_exporter = OTLPMetricExporter()
# meter_provider.start_pipeline(metrics_exporter)

# Register the provider
# metrics.set_meter_provider(meter_provider)

# # Setup counter for requests
REQUEST_COUNT = Counter('request_count_total', 'Total number of requests')

# Set message environment variable
MESSAGE = os.getenv('MESSAGE', "Hello World!")

@app.before_request
def log_request_info():
    # Create a new span 
    with tracer.start_as_current_span("request_processing") as span:
        # Increment the request count
        REQUEST_COUNT.inc()
    
        # Log request details
        logger.info({
            "event": "request",
            "method": request.method,
            "url": request.url
        })

@app.after_request
def log_request_info(response):
    with tracer.start_span("after_request") as span:
        # Log response details
        logger.info({
            "event": "response",
            "status_code":response.status_code,
        })
        return response

@app.route('/api/message', methods=['GET'])
def get_message():
    with tracer.start_as_current_span("api_message_endpoint") as span:
        logger.info("Handling /api/message request")
        return jsonify({"message": MESSAGE})


# run app

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=8080)

# Improvements to be made 
# 1. Add Error Handling
#   Add a global error handler to catch unhandled exceptions and log them
# 2. Enhance Logging with more context 
#   Include request and response headers in the logs for better traceability
#   Log the request payload if applicable 
# 3. Environment specific Configurations 
#   Implement configuration that change based on the environment
#   (development/production). For instance, toggle debugging, log levels, or 
#   metric paths based on an environment variable
# 4. Optimize Prometheus Integration 
#   Add more Prometheus metrics, like a `Histogram` or `Summary` to track request duractions 
# 5. Graceful Shutdown 
#   Implement a handler to catch termination signals and gracefully shutdown the server,
#   ensuring logs are flushed and Prometheus metrics are updated
# 6. Validation and Security 
#   Add input validation to the `/api/message` endpoint if planning to handle requests with parameters
#   Consider using Flask's built-in security features, like CSRF protection, if app has forms or handles sensitive data
# 7. Improve JSON logging
#   Ensure that all logs are output as proper JSON objects for easier integration
#   with log aggregation systems
# 8. Health check endpoint 
#   Consider adding a `/health` endpoint that can be used by load balancers or monitoring systems 
# to check if your app is running properly
