import logging
from log_aggregator import LogAggregator
from narrative_engine import NarrativeEngine

def main():
    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create and configure the aggregator
    aggregator = LogAggregator()
    aggregator.setLevel(logging.INFO)
    aggregator.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(aggregator)

    # Create narrative engine
    engine = NarrativeEngine(model="mistral")

    # Simulate a simple combat sequence
    print("Simulating combat...")
    logging.info("Bob the Fighter draws his sword.")
    logging.info("The goblin snarls and readies its club.")
    logging.info("Bob strikes swiftly, dealing 5 damage!")
    logging.info("The goblin staggers but remains standing.")

    # Get the combat log
    combat_log = aggregator.get_logs()
    print("\nCombat Log:")
    print(combat_log)

    # Generate a narrative summary using the new method
    print("\nGenerating narrative summary...")
    summary = engine.summarize_combat(combat_log)
    print("\nNarrative Summary:")
    print(summary)

if __name__ == "__main__":
    main()