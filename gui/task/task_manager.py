import logging
import threading

from gui.task.task_executor import TaskExecutor


class TaskManager:
    """任务管理器，负责管理多个任务"""

    def __init__(self):
        self.executors = {}  # 任务执行器字典
        self.lock = threading.Lock()  # 用于线程安全

    def register_task(self, task):
        """注册任务"""
        with self.lock:
            if task.name in self.executors:
                logging.warning(f"任务 {task.name} 已存在")
                return False

            self.executors[task.name] = TaskExecutor(task)
            logging.info(f"已注册任务: {task.name}")
            return True

    def unregister_task(self, task_name):
        """注销任务"""
        with self.lock:
            if task_name not in self.executors:
                logging.warning(f"任务 {task_name} 不存在")
                return False

            executor = self.executors.pop(task_name)
            executor.stop()
            logging.info(f"已注销任务: {task_name}")
            return True

    def start_task(self, task_name):
        """启动指定任务"""
        with self.lock:
            if task_name not in self.executors:
                logging.warning(f"任务 {task_name} 不存在")
                return False

            return self.executors[task_name].start()

    def stop_task(self, task_name, timeout=5.0):
        """停止指定任务"""
        with self.lock:
            if task_name not in self.executors:
                logging.warning(f"任务 {task_name} 不存在")
                return False

            return self.executors[task_name].stop(timeout)

    def start_all(self):
        """启动所有任务"""
        success = True
        with self.lock:
            for name in self.executors:
                if not self.executors[name].start():
                    success = False
        return success

    def stop_all(self, timeout=5.0):
        """停止所有任务"""
        success = True
        with self.lock:
            for name in self.executors:
                if not self.executors[name].stop(timeout):
                    success = False
        return success

    def get_task_status(self, task_name):
        """获取任务状态"""
        with self.lock:
            if task_name not in self.executors:
                return "NOT_EXIST"

            executor = self.executors[task_name]
            if executor.thread and executor.thread.is_alive():
                return "RUNNING"
            return "STOPPED"

    def get_all_status(self):
        """获取所有任务状态"""
        status = {}
        with self.lock:
            for name in self.executors:
                status[name] = self.get_task_status(name)
        return status