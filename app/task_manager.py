from typing import Dict, Callable
import asyncio

# 这个字典将作为我们简单的内存任务状态管理器
# 状态可以是: idle, running, success, failed
task_statuses: Dict[str, str] = {}

async def run_task_in_background(task_name: str, task_func: Callable, *args, **kwargs):
    """
    一个通用的后台任务执行器，并负责更新任务状态。
    """
    task_statuses[task_name] = "running"
    print(f"Task '{task_name}' started.")
    try:
        # 使用 asyncio.to_thread 来运行可能包含同步代码的异步函数，避免阻塞事件循环
        # 在我们的案例中，爬虫主要是异步的，但这是一个更稳健的做法
        await task_func(*args, **kwargs)
        task_statuses[task_name] = "success"
        print(f"Task '{task_name}' finished successfully.")
    except Exception as e:
        task_statuses[task_name] = "failed"
        print(f"Task '{task_name}' failed: {e}")

def get_task_status(task_name: str) -> str:
    """
    获取指定任务的当前状态。
    """
    return task_statuses.get(task_name, "idle")
