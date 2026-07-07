"""工具注册表 - HelloAgents原生工具系统"""

import inspect
import logging
from typing import Optional, Any, Callable
from .base import Tool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    HelloAgents工具注册表

    提供工具的注册、管理和执行功能。
    支持两种工具注册方式：
    1. Tool对象注册（推荐）
    2. 函数直接注册（简便）
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool: Tool, auto_expand: bool = True):
        """
        注册Tool对象

        Args:
            tool: Tool实例
            auto_expand: 是否自动展开可展开的工具（默认True）
        """
        # 检查工具是否可展开
        if auto_expand and hasattr(tool, 'expandable') and tool.expandable:
            expanded_tools = tool.get_expanded_tools()
            if expanded_tools:
                # 注册所有展开的子工具
                for sub_tool in expanded_tools:
                    if sub_tool.name in self._tools:
                        logger.warning("工具 '%s' 已存在，将被覆盖。", sub_tool.name)
                    self._tools[sub_tool.name] = sub_tool
                logger.info("工具 '%s' 已展开为 %d 个独立工具", tool.name, len(expanded_tools))
                return

        # 普通工具或不展开的工具
        if tool.name in self._tools:
            logger.warning("工具 '%s' 已存在，将被覆盖。", tool.name)

        self._tools[tool.name] = tool
        logger.info("工具 '%s' 已注册。", tool.name)

    def register_function(self, name: str, description: str, func: Callable[..., str]):
        """
        直接注册函数作为工具（简便方式）

        Args:
            name: 工具名称
            description: 工具描述
            func: 工具函数，接受字符串参数，返回字符串结果
        """
        if name in self._functions:
            logger.warning("工具 '%s' 已存在，将被覆盖。", name)

        self._functions[name] = {
            "description": description,
            "func": func
        }
        logger.info("工具 '%s' 已注册。", name)

    def unregister(self, name: str) -> bool:
        """注销工具。

        Returns:
            bool: 工具存在并被移除时返回 True，否则返回 False。
        """
        if name in self._tools:
            del self._tools[name]
            logger.info("工具 '%s' 已注销。", name)
            return True
        elif name in self._functions:
            del self._functions[name]
            logger.info("工具 '%s' 已注销。", name)
            return True
        else:
            logger.warning("工具 '%s' 不存在。", name)
            return False

    def unregister_tool(self, name: str) -> bool:
        """兼容入口：注销指定名称的工具或函数工具。"""
        return self.unregister(name)

    def get_tool(self, name: str) -> Optional[Tool]:
        """获取Tool对象"""
        return self._tools.get(name)

    def get_function(self, name: str) -> Optional[Callable]:
        """获取工具函数"""
        func_info = self._functions.get(name)
        return func_info["func"] if func_info else None

    def execute_tool(self, name: str, input_text: Optional[str] = None, **parameters: Any) -> str:
        """
        执行工具

        Args:
            name: 工具名称
            input_text: 简单文本输入，通常会映射为 {"input": input_text}
            **parameters: 结构化参数，直接传递给 Tool.run

        Returns:
            工具执行结果
        """
        # 优先查找Tool对象
        if name in self._tools:
            tool = self._tools[name]
            try:
                payload = dict(parameters)
                if input_text is not None and "input" not in payload:
                    payload["input"] = input_text
                return tool.run(payload)
            except Exception as e:
                logger.exception("执行工具 '%s' 时发生异常", name)
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"

        # 查找函数工具
        elif name in self._functions:
            func = self._functions[name]["func"]
            try:
                return self._execute_function(func, input_text, parameters)
            except Exception as e:
                logger.exception("执行工具函数 '%s' 时发生异常", name)
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"

        else:
            return f"错误：未找到名为 '{name}' 的工具。"

    def _execute_function(
        self,
        func: Callable[..., str],
        input_text: Optional[str],
        parameters: dict[str, Any],
    ) -> str:
        """执行 register_function 注册的函数工具。"""
        if parameters:
            try:
                return func(**parameters)
            except TypeError:
                if set(parameters.keys()) == {"input"}:
                    return func(parameters["input"])
                raise

        if input_text is not None:
            return func(input_text)

        signature = inspect.signature(func)
        if not signature.parameters:
            return func()

        return func("")

    def get_tools_description(self) -> str:
        """
        获取所有可用工具的格式化描述字符串

        Returns:
            工具描述字符串，用于构建提示词
        """
        descriptions = []

        # Tool对象描述
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")

        # 函数工具描述
        for name, info in self._functions.items():
            descriptions.append(f"- {name}: {info['description']}")

        return "\n".join(descriptions) if descriptions else "暂无可用工具"

    def get_tool_descriptions(self) -> str:
        """兼容入口：获取工具描述。"""
        return self.get_tools_description()

    def list_tools(self) -> list[str]:
        """列出所有工具名称"""
        return list(self._tools.keys()) + list(self._functions.keys())

    def get_all_tools(self) -> list[Tool]:
        """获取所有Tool对象"""
        return list(self._tools.values())

    def clear(self):
        """清空所有工具"""
        self._tools.clear()
        self._functions.clear()
        logger.info("所有工具已清空。")

# 全局工具注册表
global_registry = ToolRegistry()
