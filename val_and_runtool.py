from typing import Any, Dict, Tuple

from schemas import tool_schemas
from tools import (
    terminal,
    write_memory,
    read_memory,
    read_skill,
    get_skills,
    write_skill
   
)


tools = {
    "terminal": terminal,
    "write_memory": write_memory,
    "read_memory": read_memory,
    "read_skill": read_skill,
    "get_skills": get_skills,
    "write_skill": write_skill,

 
}


def validate_arguments(tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, str | None]:
    schema = tool_schemas.get(tool_name)
    if schema is None:
        return False, f"Unknown tool: {tool_name}"

    if not isinstance(arguments, dict):
        return False, "Arguments must be an object"

    allowed = set(schema["properties"].keys())
    required = set(schema["required"])
    provided = set(arguments.keys())

    missing = required - provided
    if missing:
        return False, f"Missing required argument: {sorted(missing)[0]}"

    if schema.get("additionalProperties") is False:
        extra = provided - allowed
        if extra:
            return False, f"Unexpected argument: {sorted(extra)[0]}"

    for name, value in arguments.items():
        prop = schema["properties"].get(name)
        if prop is None:
            return False, f"Unexpected argument: {name}"

        expected_type = prop.get("type")

        if expected_type == "string" and not isinstance(value, str):
            return False, f"Argument {name} must be a string"

        if expected_type == "integer" and not isinstance(value, int):
            return False, f"Argument {name} must be an integer"

        if "enum" in prop and value not in prop["enum"]:
            return False, f"Argument {name} must be one of: {prop['enum']}"

    return True, None


def validate_tool_call(output: Dict[str, Any]) -> Tuple[bool, str | None]:
    if not isinstance(output, dict):
        return False, "Output must be an object"

    if output.get("type") != "tool_call":
        return False, "Output is not a tool call"

    tool_name = output.get("tool")
    if not isinstance(tool_name, str):
        return False, "Tool name must be a string"

    if tool_name not in tools:
        return False, f"Tool is not runnable: {tool_name}"

    return validate_arguments(tool_name, output.get("arguments"))


def run_tool_call(output: Dict[str, Any]) -> Dict[str, Any]:
    valid, error = validate_tool_call(output)
    if not valid:
        return {
            "ok": False,
            "error": error,
            "tool": output.get("tool") if isinstance(output, dict) else None,
            "result": None,
        }

    tool_name = output["tool"]
    arguments = output["arguments"]

    try:
        result = tools[tool_name](**arguments)
    except Exception as error:
        return {
            "ok": False,
            "error": str(error),
            "tool": tool_name,
            "result": None,
        }

    return {
        "ok": True,
        "error": None,
        "tool": tool_name,
        "result": result,
    }