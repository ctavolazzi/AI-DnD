import logging
from log_aggregator import LogAggregator

def main():
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create and configure the aggregator
    aggregator = LogAggregator()
    aggregator.setLevel(logging.INFO)
    aggregator.setFormatter(logging.Formatter("%(message)s"))  # Simple format for testing
    logger.addHandler(aggregator)

    # Log some test messages
    print("Logging test messages...")
    logging.info("First message")
    logging.info("Second message")
    logging.info("Third message")

    # Get and display the aggregated logs
    print("\nAggregated logs:")
    print(aggregator.get_logs())

    # Clear and verify
    print("\nClearing logs...")
    aggregator.clear()
    print("Logs after clearing:")
    print(aggregator.get_logs())

if __name__ == "__main__":
    main()