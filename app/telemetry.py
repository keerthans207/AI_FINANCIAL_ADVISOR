# app/telemetry.py
import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from structlog import configure, get_logger, processors, stdlib
from structlog.stdlib import LoggerFactory

def init_tracing():
    resource = Resource.create({"service.name": "ai-financial-advisor"})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

def init_structlog():
    configure(
        processors=[processors.JSONRenderer()],
        logger_factory=LoggerFactory(),
    )
