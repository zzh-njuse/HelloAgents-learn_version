# 工具系统 API 文档

## 概述

HelloAgents 的工具系统由 `Tool`、`ToolParameter` 和 `ToolRegistry` 组成。

核心约定：

- 标准工具入口是 `Tool.run(parameters: dict) -> str`
- 参数定义入口是 `Tool.get_parameters() -> list[ToolParameter]`
- 兼容入口 `Tool.execute(**kwargs)` 会自动转为 `run(kwargs)`
- OpenAI function calling schema 可通过 `Tool.get_schema()` 或 `Tool.to_openai_schema()` 获取
- `ToolRegistry.execute_tool()` 同时支持简单文本输入和结构化参数

基础工具会随包轻量导入；Memory、RAG、协议、评估、RL 等可选重依赖工具会按需延迟加载，避免 `import hello_agents` 时强制安装全部扩展依赖。

## Tool 基类

```python
from hello_agents.tools.base import Tool, ToolParameter


class Tool(ABC):
    def __init__(self, name: str, description: str, expandable: bool = False)

    def run(self, parameters: dict) -> str
    def get_parameters(self) -> list[ToolParameter]

    # 兼容和辅助方法
    def execute(self, **kwargs) -> str
    def validate_parameters(self, parameters: dict) -> bool
    def to_dict(self) -> dict
    def to_openai_schema(self) -> dict
    def get_schema(self) -> dict
```

### 自定义工具

```python
from hello_agents.tools.base import Tool, ToolParameter


class WeatherTool(Tool):
    def __init__(self):
        super().__init__(
            name="weather",
            description="获取指定城市的天气信息",
        )

    def run(self, parameters: dict) -> str:
        city = parameters["city"]
        return f"{city}的天气：晴，25°C"

    def get_parameters(self):
        return [
            ToolParameter(
                name="city",
                type="string",
                description="城市名称",
                required=True,
            )
        ]
```

调用方式：

```python
tool = WeatherTool()
tool.run({"city": "杭州"})
tool.execute(city="杭州")
```

## 可展开工具

复杂工具可以使用 `@tool_action` 展开为多个子工具，适合 Memory、RAG、MCP 这类多动作工具。

```python
from hello_agents.tools.base import Tool, ToolParameter, tool_action


class NoteTool(Tool):
    def __init__(self):
        super().__init__("note", "笔记工具", expandable=True)

    def run(self, parameters: dict) -> str:
        return "请使用展开后的子工具"

    def get_parameters(self):
        return []

    @tool_action("note_create", "创建笔记")
    def create(self, title: str, content: str) -> str:
        return f"已创建：{title}"
```

注册时默认会自动展开：

```python
registry = ToolRegistry()
registry.register_tool(NoteTool())
print(registry.list_tools())  # ["note_create"]
```

## ToolRegistry

```python
from hello_agents import ToolRegistry

registry = ToolRegistry()
```

主要方法：

```python
registry.register_tool(tool, auto_expand=True)
registry.register_function(name, description, func)
registry.unregister(name) -> bool
registry.unregister_tool(name) -> bool

registry.get_tool(name)
registry.get_function(name)
registry.list_tools()
registry.get_all_tools()

registry.execute_tool(name, input_text=None, **parameters) -> str
registry.get_tools_description() -> str
registry.get_tool_descriptions() -> str
registry.clear()
```

### 注册 Tool 对象

```python
from hello_agents import ToolRegistry, CalculatorTool

registry = ToolRegistry()
registry.register_tool(CalculatorTool())

result = registry.execute_tool("python_calculator", "2 + 3 * 4")
print(result)  # 14
```

### 注册函数工具

`register_function` 适合快速把普通函数包装成工具。函数可以接收一个文本参数，也可以接收关键字参数。

```python
registry.register_function("upper", "转大写", lambda text: text.upper())
registry.register_function("join", "拼接文本", lambda left, right: f"{left}-{right}")

registry.execute_tool("upper", "hello")             # HELLO
registry.execute_tool("upper", input="hello")       # HELLO
registry.execute_tool("join", left="a", right="b")  # a-b
```

## 内置基础工具

### CalculatorTool

```python
from hello_agents import CalculatorTool, calculate

tool = CalculatorTool()
tool.run({"input": "sqrt(16)"})     # "4.0"
tool.execute(input="2+3*4")         # "14"

calculate("2 + 2")                  # "4"
```

工具名：`python_calculator`

支持基础运算和部分 `math` 函数，例如 `sqrt(16)`、`sin(pi/2)`、`log(e)`。

### SearchTool

```python
from hello_agents import SearchTool, search

tool = SearchTool(backend="hybrid")
result = tool.run({"input": "Python agent framework"})
```

支持后端：

- `hybrid` / `advanced`
- `tavily`
- `serpapi`
- `duckduckgo`
- `searxng`
- `perplexity`

Tavily、SerpApi、Perplexity 等后端需要对应 API key 和可选依赖；缺失时会降级或报出明确错误。

## 异步执行

```python
import asyncio
from hello_agents import ToolRegistry, CalculatorTool
from hello_agents.tools.async_executor import run_batch_tool


async def main():
    registry = ToolRegistry()
    registry.register_tool(CalculatorTool())

    results = await run_batch_tool(
        registry,
        "python_calculator",
        ["2+2", "3*5"],
        max_workers=2,
    )
    return results


print(asyncio.run(main()))
```

`AsyncToolExecutor` 同时支持同步和异步上下文管理：

```python
async with AsyncToolExecutor(registry) as executor:
    results = await executor.execute_tools_parallel(tasks)
```

## 在 Agent 中使用工具

```python
from hello_agents import HelloAgentsLLM, SimpleAgent, ToolRegistry, CalculatorTool

llm = HelloAgentsLLM()
registry = ToolRegistry()
registry.register_tool(CalculatorTool())

agent = SimpleAgent(
    name="工具助手",
    llm=llm,
    tool_registry=registry,
)

response = agent.run("请计算 123 * 456")
```

`SimpleAgent` 支持文本标记格式：

```text
[TOOL_CALL:python_calculator:input=123*456]
```

如果需要 OpenAI 原生 function calling，可使用 `FunctionCallAgent`。

## 测试

核心工具系统的单元测试位于：

```bash
tests/test_tools_core.py
```

运行：

```bash
python -m pytest tests/test_tools_core.py -q
```
