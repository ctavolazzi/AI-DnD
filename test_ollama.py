from narrative_engine import NarrativeEngine

def main():
    print("Testing Ollama Integration")
    print("=========================")

    engine = NarrativeEngine(model="mistral")

    # Test ONE simple scene description
    result = engine.describe_scene("tavern", ["Bob the Fighter"])
    print("\nScene Description:")
    print(result)

if __name__ == "__main__":
    main()