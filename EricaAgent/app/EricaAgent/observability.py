from opentelemetry import metrics


ENVIRONMENT = "classroom"
APP_VERSION = "v2"

COMMON_ATTRIBUTES = {
    "environment": ENVIRONMENT,
    "app_version": APP_VERSION,
}

meter = metrics.get_meter("erica-agent")


messages_loaded_metric = meter.create_histogram(
    name="erica.memory.messages_loaded",
    unit="messages",
    description="Messages loaded from Redis for each request",
)


response_length_metric = meter.create_histogram(
    name="erica.response.length",
    unit="characters",
    description="Number of characters returned by the agent",
)


def get_history_size_bucket(message_count):
    if message_count == 0:
        return "0"
    if message_count <= 4:
        return "1-4"
    if message_count <= 8:
        return "5-8"
    return "9+"


def observe_input(message_count):
    # CloudWatch: record how much history was loaded.
    messages_loaded_metric.record(
        message_count,
        COMMON_ATTRIBUTES,
    )

    # LangSmith: explain the request using metadata.
    return {
        "run_name": "erica.chat",
        "metadata": {
            "history_size": message_count,
            "history_size_bucket": get_history_size_bucket(message_count),
            **COMMON_ATTRIBUTES,
        },
        "tags": ["erica", "agentcore"],
    }


def observe_output(response_text):
    response_length_metric.record(
        len(str(response_text)),
        COMMON_ATTRIBUTES,
    )

    provider = metrics.get_meter_provider()
    if hasattr(provider, "force_flush"):
        provider.force_flush()

