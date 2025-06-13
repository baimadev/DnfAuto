import threading


class TaskExecutor:
    """任务执行器，负责在单独的线程中运行任务"""

    def __init__(self, task):
        self.task = task
        self.thread = None

    def start(self):
        """启动任务"""
        if self.thread and self.thread.is_alive():
            self.task.logger.warning("任务已在运行")
            return False

        self.thread = threading.Thread(
            target=self.task.run,
            daemon=True,
            name=f"Executor-{self.task.name}"
        )
        self.thread.start()
        self.task.logger.info("任务已启动")
        return True

    def stop(self, timeout=1.0):
        """停止任务并等待完成"""
        if not self.thread or not self.thread.is_alive():
            self.task.logger.warning("任务未在运行")
            return True

        self.task.stop()
        self.thread.join(timeout)

        if self.thread.is_alive():
            self.task.logger.warning(f"任务在 {timeout}s 内未能完成")
            return False
        else:
            self.task.logger.info("任务已停止")
            return True