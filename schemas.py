tool_schemas = {
    "terminal": {
        "type": "object",
        "properties": {
            "line": {
                "type": "string",
                "description": "The shell command to execute.",
            },
            "timeout": {
                "type": "integer",
                "minimum": 1,
                "description": "Maximum execution time in seconds. Defaults to 30.",
            },
        },
        "required": ["line"],
        "additionalProperties": False,
    },

    "write_memory": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to append to the agent's memory file.",
            },
        },
        "required": ["text"],
        "additionalProperties": False,
    },

    "read_memory": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },

    "write_skill": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "minLength": 1,
                "description": (
                    "The skill filename without the .md extension. "
                    "The skill must not already exist."
                ),
            },
            "content": {
                "type": "string",
                "description": "The complete Markdown content of the new skill.",
            },
        },
        "required": ["name", "content"],
        "additionalProperties": False,
    },

    "get_skills": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },

    "read_skill": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "minLength": 1,
                "description": (
                    "The name of the skill to read, without the .md extension."
                ),
            },
        },
        "required": ["name"],
        "additionalProperties": False,
    },
}

tool_call_schema = {
    "type": "object",
    "properties": {
        "type": {"const": "tool_call"},
        "tool": {
            "type": "string",
            "enum": list(tool_schemas.keys()),
        },
        "arguments": {"type": "object"},
    },
    "required": ["type", "tool", "arguments"],
    "additionalProperties": False,
}


final_response_schema = {
    "type": "object",
    "properties": {
        "type": {"const": "final"},
        "message": {"type": "string"},
    },
    "required": ["type", "message"],
    "additionalProperties": False,
}


response_schemas = {
    "tool_call": tool_call_schema,
    "final": final_response_schema,
}