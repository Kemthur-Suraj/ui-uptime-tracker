# Push ui_render_success_rate and ui_response_time_seconds to OTEL Collector
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
import os

# Initialize Meter
collector = os.getenv("OTEL_COLLECTOR_ENDPOINT")
exporter = OTLPMetricExporter(endpoint=collector, insecure=True)
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter("ghh-ui-synthetic-prober", version="1.0.0")

# Instruments
success_gauge = meter.create_observable_gauge(
    "ui_render_success_rate",
    description="1 for success, 0 for failure",
)
response_time_gauge = meter.create_observable_gauge(
    "ui_response_time_seconds",
    description="Render time in seconds",
)

# Data storage for last values
_last_values = {}

def record(endpoint_name: str, success: int, response_time: float, tags: dict):
    # Store values for the callback
    _last_values[endpoint_name] = (success, response_time, tags)

def _observe_callback(options):
    for name, (succ, rt, tags) in _last_values.items():
        labels = {
            "endpoint": name,
            **tags
        }
        success_gauge.callback(lambda obs, name=name, succ=succ, labels=labels: obs.observe(succ, labels))
        response_time_gauge.callback(lambda obs, name=name, rt=rt, labels=labels: obs.observe(rt, labels))

# Register callback once
meter.register_observable_callback(_observe_callback, [success_gauge, response_time_gauge])
