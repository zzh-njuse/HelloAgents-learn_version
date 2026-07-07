import asyncio

from hello_agents import CalculatorTool, SimpleAgent, ToolRegistry
from hello_agents.tools.async_executor import run_batch_tool
from hello_agents.tools.base import Tool, ToolParameter, tool_action


class EchoTool(Tool):
    def __init__(self):
        super().__init__("echo", "Echo input text")

    def run(self, parameters):
        return parameters["input"]

    def get_parameters(self):
        return [
            ToolParameter(
                name="input",
                type="string",
                description="Text to echo",
                required=True,
            )
        ]


class ScriptedLLM:
    provider = "fake"

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def invoke(self, messages, **kwargs):
        self.calls.append(messages)
        return self.responses.pop(0)

    def stream_invoke(self, messages, **kwargs):
        for chunk in self.invoke(messages, **kwargs):
            yield chunk


def test_package_import_does_not_require_openai_client_initialization():
    import hello_agents

    assert hasattr(hello_agents, "ToolRegistry")
    assert hasattr(hello_agents, "HelloAgentsLLM")


def test_tool_execute_and_schema_compatibility():
    tool = CalculatorTool()

    assert tool.run({"input": "2+3*4"}) == "14"
    assert tool.execute(input="sqrt(16)") == "4.0"

    schema = tool.get_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "python_calculator"
    assert "input" in schema["function"]["parameters"]["properties"]


def test_registry_executes_tools_and_functions_with_compatible_api():
    registry = ToolRegistry()
    registry.register_tool(EchoTool())
    registry.register_function("upper", "Uppercase text", lambda text: text.upper())
    registry.register_function("join", "Join words", lambda left, right: f"{left}-{right}")
    registry.register_function("ping", "No-arg function", lambda: "pong")

    assert registry.execute_tool("echo", "hello") == "hello"
    assert registry.execute_tool("upper", input="hello") == "HELLO"
    assert registry.execute_tool("join", left="a", right="b") == "a-b"
    assert registry.execute_tool("ping") == "pong"
    assert registry.get_tool_descriptions() == registry.get_tools_description()

    assert registry.unregister_tool("upper") is True
    assert registry.unregister_tool("missing") is False


def test_expandable_tool_actions_are_registered_as_subtools():
    class NotesTool(Tool):
        def __init__(self):
            super().__init__("notes", "Notes", expandable=True)

        def run(self, parameters):
            return "unused"

        def get_parameters(self):
            return []

        @tool_action(description="Create a note")
        def create(self, title: str, priority: int = 1):
            return f"{title}:{priority}"

    registry = ToolRegistry()
    registry.register_tool(NotesTool())

    assert registry.list_tools() == ["notes_create"]
    assert registry.execute_tool("notes_create", title="todo", priority=2) == "todo:2"


def test_simple_agent_remove_tool_and_text_tool_call_flow():
    registry = ToolRegistry()
    registry.register_tool(EchoTool())
    llm = ScriptedLLM(["[TOOL_CALL:echo:input=hello]", "final answer"])

    agent = SimpleAgent("tester", llm, tool_registry=registry)

    assert agent.run("say hello") == "final answer"
    assert agent.remove_tool("echo") is True
    assert agent.remove_tool("echo") is False


def test_async_executor_batch_helper_runs_tools():
    registry = ToolRegistry()
    registry.register_tool(CalculatorTool())

    results = asyncio.run(
        run_batch_tool(
            registry,
            "python_calculator",
            ["2+2", "3*5"],
            max_workers=2,
        )
    )

    assert [item["status"] for item in results] == ["success", "success"]
    assert [item["result"] for item in results] == ["4", "15"]
