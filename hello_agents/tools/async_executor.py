"""异步工具执行器 - HelloAgents异步工具执行支持"""

import asyncio
import concurrent.futures
import logging
from typing import Dict, Any, List
from .registry import ToolRegistry

logger = logging.getLogger(__name__)


class AsyncToolExecutor:
    """异步工具执行器"""

    def __init__(self, registry: ToolRegistry, max_workers: int = 4):
        self.registry = registry
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    async def execute_tool_async(self, tool_name: str, input_data: str) -> str:
        """异步执行单个工具"""
        loop = asyncio.get_running_loop()
        
        def _execute():
            return self.registry.execute_tool(tool_name, input_data)
        
        try:
            result = await loop.run_in_executor(self.executor, _execute)
            return result
        except Exception as e:
            return f"❌ 工具 '{tool_name}' 异步执行失败: {e}"

    async def execute_tools_parallel(self, tasks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        并行执行多个工具
        
        Args:
            tasks: 任务列表，每个任务包含 tool_name 和 input_data
            
        Returns:
            执行结果列表，包含任务信息和结果
        """
        logger.info("开始并行执行 %d 个工具任务", len(tasks))
        
        # 创建异步任务
        async_tasks = []
        for i, task in enumerate(tasks):
            tool_name = task.get("tool_name")
            input_data = task.get("input_data", "")
            
            if not tool_name:
                continue
                
            logger.debug("创建任务 %d: %s", i + 1, tool_name)
            async_task = asyncio.create_task(self.execute_tool_async(tool_name, input_data))
            async_tasks.append((i, task, async_task))
        
        # 等待所有任务完成
        results = []
        gathered = await asyncio.gather(
            *(async_task for _, _, async_task in async_tasks),
            return_exceptions=True,
        )

        for (i, task, _), result in zip(async_tasks, gathered):
            try:
                if isinstance(result, Exception):
                    raise result
                results.append({
                    "task_id": i,
                    "tool_name": task["tool_name"],
                    "input_data": task["input_data"],
                    "result": result,
                    "status": "success"
                })
                logger.debug("任务 %d 完成: %s", i + 1, task["tool_name"])
            except Exception as e:
                results.append({
                    "task_id": i,
                    "tool_name": task["tool_name"],
                    "input_data": task["input_data"],
                    "result": str(e),
                    "status": "error"
                })
                logger.exception("任务 %d 失败: %s", i + 1, task["tool_name"])
        
        logger.info(
            "并行执行完成，成功: %d/%d",
            sum(1 for r in results if r["status"] == "success"),
            len(results),
        )
        return results

    async def execute_tools_batch(self, tool_name: str, input_list: List[str]) -> List[Dict[str, Any]]:
        """
        批量执行同一个工具
        
        Args:
            tool_name: 工具名称
            input_list: 输入数据列表
            
        Returns:
            执行结果列表
        """
        tasks = [
            {"tool_name": tool_name, "input_data": input_data}
            for input_data in input_list
        ]
        return await self.execute_tools_parallel(tasks)

    def close(self):
        """关闭执行器"""
        self.executor.shutdown(wait=True)
        logger.debug("异步工具执行器已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 便捷函数
async def run_parallel_tools(registry: ToolRegistry, tasks: List[Dict[str, str]], max_workers: int = 4) -> List[Dict[str, Any]]:
    """
    便捷函数：并行执行多个工具
    
    Args:
        registry: 工具注册表
        tasks: 任务列表
        max_workers: 最大工作线程数
        
    Returns:
        执行结果列表
    """
    async with AsyncToolExecutor(registry, max_workers) as executor:
        return await executor.execute_tools_parallel(tasks)


async def run_batch_tool(registry: ToolRegistry, tool_name: str, input_list: List[str], max_workers: int = 4) -> List[Dict[str, Any]]:
    """
    便捷函数：批量执行同一个工具
    
    Args:
        registry: 工具注册表
        tool_name: 工具名称
        input_list: 输入数据列表
        max_workers: 最大工作线程数
        
    Returns:
        执行结果列表
    """
    async with AsyncToolExecutor(registry, max_workers) as executor:
        return await executor.execute_tools_batch(tool_name, input_list)


# 同步包装函数（为了兼容性）
def run_parallel_tools_sync(registry: ToolRegistry, tasks: List[Dict[str, str]], max_workers: int = 4) -> List[Dict[str, Any]]:
    """同步版本的并行工具执行"""
    return asyncio.run(run_parallel_tools(registry, tasks, max_workers))


def run_batch_tool_sync(registry: ToolRegistry, tool_name: str, input_list: List[str], max_workers: int = 4) -> List[Dict[str, Any]]:
    """同步版本的批量工具执行"""
    return asyncio.run(run_batch_tool(registry, tool_name, input_list, max_workers))


# 示例函数
async def demo_parallel_execution():
    """演示并行执行的示例"""
    from .registry import ToolRegistry
    
    # 创建注册表（这里假设已经注册了工具）
    registry = ToolRegistry()
    
    # 定义并行任务
    tasks = [
        {"tool_name": "my_calculator", "input_data": "2 + 2"},
        {"tool_name": "my_calculator", "input_data": "3 * 4"},
        {"tool_name": "my_calculator", "input_data": "sqrt(16)"},
        {"tool_name": "my_calculator", "input_data": "10 / 2"},
    ]
    
    # 并行执行
    results = await run_parallel_tools(registry, tasks)
    
    # 显示结果
    logger.info("并行执行结果:")
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        logger.info("%s %s(%s) = %s", status_icon, result["tool_name"], result["input_data"], result["result"])
    
    return results


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_parallel_execution())
