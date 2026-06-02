"""Prompt regression tests against golden responses."""
import json

GOLDEN_PATH = "tests/prompts/golden_responses/sample_cases.json"

def load_golden():
    with open(GOLDEN_PATH) as f:
        return json.load(f)

# TODO: Implement regression test loop against agent
