"""工具系统。

基础工具系统保持轻量导入；Memory/RAG/协议/评估/RL 等可选重依赖工具
通过 ``__getattr__`` 延迟加载，避免 ``import hello_agents`` 时强制安装全部扩展。
"""

from importlib import import_module

from .base import Tool, ToolParameter, tool_action
from .registry import ToolRegistry, global_registry
from .builtin.search_tool import SearchTool
from .builtin.calculator import CalculatorTool
from .chain import ToolChain, ToolChainManager, create_research_chain, create_simple_chain
from .async_executor import (
    AsyncToolExecutor,
    run_batch_tool,
    run_batch_tool_sync,
    run_parallel_tools,
    run_parallel_tools_sync,
)

_LAZY_EXPORTS = {
    "MemoryTool": ".builtin.memory_tool",
    "RAGTool": ".builtin.rag_tool",
    "NoteTool": ".builtin.note_tool",
    "TerminalTool": ".builtin.terminal_tool",
    "MCPTool": ".builtin.protocol_tools",
    "A2ATool": ".builtin.protocol_tools",
    "ANPTool": ".builtin.protocol_tools",
    "BFCLEvaluationTool": ".builtin.bfcl_evaluation_tool",
    "GAIAEvaluationTool": ".builtin.gaia_evaluation_tool",
    "LLMJudgeTool": ".builtin.llm_judge_tool",
    "WinRateTool": ".builtin.win_rate_tool",
    "RLTrainingTool": ".builtin.rl_training_tool",
}

__all__ = [
    "Tool",
    "ToolParameter",
    "tool_action",
    "ToolRegistry",
    "global_registry",
    "SearchTool",
    "CalculatorTool",
    "ToolChain",
    "ToolChainManager",
    "create_research_chain",
    "create_simple_chain",
    "AsyncToolExecutor",
    "run_parallel_tools",
    "run_batch_tool",
    "run_parallel_tools_sync",
    "run_batch_tool_sync",
    *_LAZY_EXPORTS.keys(),
]


def __getattr__(name: str):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(_LAZY_EXPORTS[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
