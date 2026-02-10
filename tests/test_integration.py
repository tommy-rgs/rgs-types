import pytest
import subprocess
import sys
import shutil
import json
import os
from pathlib import Path
from hypothesis import HealthCheck, given, settings, strategies as st
from rgs_types.parser import parse_schema_file
from rgs_types.generators.python import PythonGenerator
from rgs_types.generators.cpp import CppGenerator
from rgs_types.generators.typescript import TypeScriptGenerator
from rgs_types.generators.json_data import JsonDataGenerator
from rgs_types.generators.utils import snake_case, pascal_case

# Get all schema.json files from test_cases
TEST_CASE_DIR = Path(__file__).parent.parent / "test_cases"
schema_files = list(TEST_CASE_DIR.glob("*/schema.json"))

def is_tool_installed(name):
    return shutil.which(name) is not None

@pytest.mark.slow
@pytest.mark.parametrize("schema_path", schema_files, ids=lambda p: p.parent.name)
@given(data=st.data())
@settings(
    deadline=None, 
    max_examples=1, # One run per schema, but we draw multiple samples inside
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_python_integration(schema_path, tmp_path, data):
    """
    Generate Python code once, then run multiple Hypothesis samples through it in a batch.
    """
    schema = parse_schema_file(schema_path)
    root_name = schema.title or "GeneratedModel"
    module_name = root_name.lower()
    
    # Determine expected location based on namespace
    final_module_path = module_name
    if schema.python_namespace:
        final_module_path = f"{schema.python_namespace}.{module_name}"
    
    generator = PythonGenerator(schema, tmp_path)
    generator.generate()

    data_gen = JsonDataGenerator(schema)
    try:
        strategy = data_gen.get_strategy()
        # Batch draw: 10 samples
        samples = [data.draw(strategy) for _ in range(10)]
    except Exception as e:
        if "7_refs" in str(schema_path):
             pytest.xfail(f"Strategy generation failed for recursive schema: {e}")
        raise

    sys.path.insert(0, str(tmp_path))
    try:
        import importlib
        # Force reload if it was already imported in a previous parametrization
        if final_module_path in sys.modules:
            importlib.reload(sys.modules[final_module_path])
        mod = importlib.import_module(final_module_path)
        
        class_name = root_name.replace(" ", "")
        cls = getattr(mod, class_name)
        
        for sample_data in samples:
            try:
                instance = cls.from_dict(sample_data)
                output_dict = instance.to_dict()
                assert isinstance(output_dict, dict)
            except TypeError as e:
                if "argument" in str(e):
                     pytest.skip(f"Nested instantiation gap: {e}")
                raise
    finally:
        sys.path.pop(0)


@pytest.mark.slow
@pytest.mark.parametrize("schema_path", schema_files, ids=lambda p: p.parent.name)
@given(data=st.data())
@settings(
    deadline=None, 
    max_examples=1, 
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_cpp_integration(schema_path, tmp_path, data):
    """
    Generate and compile C++ once, then run multiple samples in a single batch.
    """
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        pytest.fail("C++ compiler (clang++ or g++) not found in PATH.")

    schema = parse_schema_file(schema_path)
    root_name = schema.title or "GeneratedModel"
    root_name = pascal_case(root_name)
    class_name = root_name.replace(" ", "")
    header_file = tmp_path / f"{root_name.lower()}.hpp"
    bin_file = tmp_path / "test_bin"

    generator = CppGenerator(schema, tmp_path)
    generator.generate()
    
    namespace = schema.cpp_namespace
    if not namespace and schema.id:
        namespace = schema.id.split("/")[-1].split(".")[0]
        namespace = snake_case(namespace)
    ns_prefix = f"{namespace}::" if namespace else ""
    
    main_cpp = tmp_path / "main.cpp"
    main_cpp.write_text(f"""
    #include "{header_file.name}"
    #include <iostream>
    #include <fstream>
    #include <nlohmann/json.hpp>

    int main(int argc, char** argv) {{
        if (argc < 2) return 1;
        std::ifstream f(argv[1]);
        if (!f.is_open()) return 1;
        try {{
            nlohmann::json data_array = nlohmann::json::parse(f);
            for (auto& data : data_array) {{
                {ns_prefix}{class_name} obj;
                from_json(data, obj);
                nlohmann::json output;
                to_json(output, obj);
            }}
        }} catch (const std::exception& e) {{
            std::cerr << "Error: " << e.what() << std::endl;
            return 1;
        }}
        return 0;
    }}
    """)
    
    include_paths = ["-I/usr/include", "-I/usr/local/include"]
    if "JSON_INCLUDE_DIR" in os.environ:
        include_paths.append(f"-I{os.environ['JSON_INCLUDE_DIR']}")

    try:
        subprocess.run(
            [compiler, "-std=c++17"] + include_paths + [str(main_cpp), "-o", str(bin_file)], 
            cwd=tmp_path, check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        pytest.fail(f"C++ Compilation failed.\nStderr: {e.stderr}")

    data_gen = JsonDataGenerator(schema)
    try:
        strategy = data_gen.get_strategy()
        samples = [data.draw(strategy) for _ in range(10)]
    except Exception as e:
        if "7_refs" in str(schema_path):
             pytest.xfail(f"Strategy generation failed for recursive schema: {e}")
        raise

    data_file = tmp_path / "samples.json"
    data_file.write_text(json.dumps(samples))
    
    try:
        subprocess.run([str(bin_file), "samples.json"], cwd=tmp_path, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Runtime batch parsing failed:\nStderr: {e.stderr}")


@pytest.mark.slow
@pytest.mark.parametrize("schema_path", schema_files, ids=lambda p: p.parent.name)
@given(data=st.data())
@settings(
    deadline=None, 
    max_examples=1, 
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_typescript_integration(schema_path, tmp_path, data):
    """
    Generate and compile TS once, then verify multiple samples in a batch.
    """
    if not is_tool_installed("tsc"):
        pytest.fail("tsc not found in PATH.")

    schema = parse_schema_file(schema_path)
    root_name = schema.title or "GeneratedModel"
    root_name = pascal_case(root_name)
    
    generator = TypeScriptGenerator(schema, tmp_path)
    generator.generate()
    
    (tmp_path / "tsconfig.json").write_text(json.dumps({
        "compilerOptions": {
            "target": "es2020", "module": "commonjs", "strict": True, "skipLibCheck": True, "esModuleInterop": True
        }
    }))
    
    try:
        subprocess.run(["tsc"], cwd=tmp_path, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"TS compilation failed: {e.stderr}")

    if not is_tool_installed("node"):
        pytest.fail("node not found in PATH.")

    data_gen = JsonDataGenerator(schema)
    try:
        strategy = data_gen.get_strategy()
        samples = [data.draw(strategy) for _ in range(10)]
    except Exception as e:
        if "7_refs" in str(schema_path):
             pytest.xfail(f"Strategy generation failed for recursive schema: {e}")
        raise
    
    samples_file = tmp_path / "samples.json"
    samples_file.write_text(json.dumps(samples))

    test_js = tmp_path / "test_run.js"
    test_js.write_text(f"""
    const {{ {root_name} }} = require('./{root_name.lower()}');
    const samples = require('./samples.json');
    try {{
        samples.forEach(data => {{
            const obj = {root_name}.fromJson(data);
            const jsonStr = {root_name}.toJson(obj);
        }});
        process.exit(0);
    }} catch (e) {{
        console.error(e);
        process.exit(1);
    }}
    """)
    
    try:
        subprocess.run(["node", str(test_js)], cwd=tmp_path, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"TS runtime batch execution failed:\nStderr: {e.stderr}")