from mcp.tools.sense_handler import TOOL_SCHEMA


def test_sense_declares_its_read_only_mcp_contract():
    assert TOOL_SCHEMA["name"] == "sense"
    assert TOOL_SCHEMA["annotations"] == {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }


def test_sense_contract_only_selects_the_citizen_workspace():
    assert set(TOOL_SCHEMA["inputSchema"]["properties"]) == {"handle"}
    assert "Global Workspace" in TOOL_SCHEMA["description"]
    assert "Spaces" in TOOL_SCHEMA["description"]
