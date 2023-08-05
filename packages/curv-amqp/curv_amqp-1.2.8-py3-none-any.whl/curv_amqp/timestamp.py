import arrow


def get_timestamp() -> int:
    return arrow.utcnow().timestamp


def get_timestamp_difference_in_seconds(timestamp: int) -> float:
    """returns the difference between a timestamp and now in seconds."""
    return arrow.utcnow().timestamp - timestamp
