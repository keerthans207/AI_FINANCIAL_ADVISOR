# app/telemetry.py
import os
from structlog import configure, get_logger, processors, stdlib
from structlog.stdlib import LoggerFactory

# Try to import OpenTelemetry, but make it optional
TRACING_AVAILABLE = False
try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    TRACING_AVAILABLE = True
except ImportError:
    pass

def init_tracing():
    """Initialize OpenTelemetry tracing (optional)"""
    if not TRACING_AVAILABLE:
        # Silently skip if OpenTelemetry is not installed
        return
    
    try:
        resource = Resource.create({"service.name": "ai-financial-advisor"})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
    except Exception:
        # If tracing fails, continue without it
        pass

def init_structlog():
    """Initialize structured logging with proper processors"""
    configure(
        processors=[
            stdlib.filter_by_level,
            stdlib.add_logger_name,
            stdlib.add_log_level,
            stdlib.PositionalArgumentsFormatter(),
            processors.TimeStamper(fmt="iso"),
            processors.StackInfoRenderer(),
            processors.format_exc_info,
            processors.UnicodeDecoder(),
            processors.JSONRenderer()
        ],
        logger_factory=LoggerFactory(),
        wrapper_class=stdlib.BoundLogger,
        context_class=dict,
        cache_logger_on_first_use=True,
    )
