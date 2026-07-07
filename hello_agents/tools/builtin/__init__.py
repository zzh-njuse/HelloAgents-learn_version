"""内置工具模块。

基础内置工具直接导入；可选扩展工具按需延迟导入。
"""

from importlib import import_module

from .calculator import CalculatorTool, calculate
from .search_tool import SearchTool, search, search_hybrid, search_serpapi, search_tavily

_LAZY_EXPORTS = {
    "MemoryTool": ".memory_tool",
    "RAGTool": ".rag_tool",
    "NoteTool": ".note_tool",
    "TerminalTool": ".terminal_tool",
    "MCPTool": ".protocol_tools",
    "A2ATool": ".protocol_tools",
    "ANPTool": ".protocol_tools",
    "BFCLEvaluationTool": ".bfcl_evaluation_tool",
    "GAIAEvaluationTool": ".gaia_evaluation_tool",
    "LLMJudgeTool": ".llm_judge_tool",
    "WinRateTool": ".win_rate_tool",
    "RLTrainingTool": ".rl_training_tool",
}

__all__ = [
    "SearchTool",
    "search",
    "search_tavily",
    "search_serpapi",
    "search_hybrid",
    "CalculatorTool",
    "calculate",
    *_LAZY_EXPORTS.keys(),
]


def __getattr__(name: str):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(_LAZY_EXPORTS[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
