import pytest
from pathlib import Path
from jsonschema import validate
from hypothesis import given, settings, strategies as st
from rgs_types.parser import parse_schema_file
from rgs_types.generators.json_data import JsonDataGenerator

# Get all schema.json files from test_cases
TEST_CASE_DIR = Path(__file__).parent.parent / "test_cases"
schema_files = list(TEST_CASE_DIR.glob("*/schema.json"))

@pytest.mark.parametrize("schema_path", schema_files, ids=lambda p: p.parent.name)
@given(data=st.data())
@settings(deadline=None, max_examples=10) # Reduced examples for speed, use specific fuzzing profile for more
@pytest.mark.slow
def test_generate_data_for_all_test_cases(schema_path, data):
    """
    Ensure that the JsonDataGenerator produces data that validates 
    against the original schema for all test cases.
    
    We use @given(data=st.data()) to draw from the dynamically created strategy,
    which enables Hypothesis shrinking on failure.
    """
    if "7_refs" in str(schema_path):
        pytest.xfail("hypothesis-jsonschema does not support recursive references")

    # 1. Parse the schema into our model
    schema_model = parse_schema_file(schema_path)
    
    # 2. Initialize generator (now cached internally)
    generator = JsonDataGenerator(schema_model)
    
    # 3. Get the strategy
    strategy = generator.get_strategy()
    
    # 4. Draw data from the strategy
    generated_data = data.draw(strategy)
        
    # 5. Validate data against the generator's cached schema dictionary
    validate(instance=generated_data, schema=generator.schema_dict)

@given(data=st.data())
@settings(max_examples=10)
@pytest.mark.slow
def test_generate_data_with_constraints(data):
    """Test that constraints like minimum/maximum are respected."""
    from rgs_types.parser import parse_schema_string
    
    json_str = """
    {
        "type": "object",
        "properties": {
            "val": {
                "type": "integer",
                "minimum": 10,
                "maximum": 20
            }
        },
        "required": ["val"]
    }
    """
    schema_model = parse_schema_string(json_str)
    generator = JsonDataGenerator(schema_model)
    
    strategy = generator.get_strategy()
    generated_data = data.draw(strategy)
    
    assert 10 <= generated_data["val"] <= 20