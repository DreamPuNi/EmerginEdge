import threading
from concurrent.futures import Future, ThreadPoolExecutor
from src.core.utilities.log import logger
from src.core.middleware.queue_manage import get_msg_queue
from src.ai_services.adapters.adapters_list import ADAPTERS_LIST
from src.ai_services.interfaces.adapter_return import FormatAssistantReply

class ModelRouter:
    def __init__(self, adapters, max_workers=5):
        self.adapters = adapters
        self.message_queue = get_msg_queue()
        self.future_dict = {}
        self.clean_response = FormatAssistantReply().clean_response
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._start_handler_thread()

    def route(self, request_data):
        """
        解析request_data并将解析后的AI实例放入消息列表

        Args:
            request_data: 请求数据
        """
        adapter_name = request_data["adapter"]
        user_id = request_data["user_id"]
        task_id = request_data["task_id"]
        if adapter_name not in self.adapters:
            logger.error(f"Unsupported adapter: {adapter_name}")
            raise ValueError(f"Unsupported adapter: {adapter_name}")
        adapter = self.adapters[adapter_name](request_data)

        future = Future()
        self.future_dict[task_id] = future

        self.message_queue.put((user_id, task_id, adapter))

        return future

    def _handle(self):
        """
        不断取出任务并交给线程池执行
        """
        while True:
            user_id, task_id, adapter = self.message_queue.get()
            self.executor.submit(self._process_task, user_id, task_id, adapter)
            self.message_queue.task_done()

    def _process_task(self, user_id, task_id, adapter):
        """
        此函数在多个线程中并行执行，获取handle给到的任务信息，在线程池中执行

        Args:
            task_id: 任务ID
            adapter: 指定的适配器
        """
        try:
            response = adapter.handle()
            reply = self.clean_response(user_id, task_id, response)
            logger.info(f"User {user_id}`s task {task_id} processed successfully.")
            success = True
        except Exception as e:
            logger.error(f"Error occurred while processing task [{task_id}]:[{e}]")
            reply = {
                "success": False,
                "user_id": user_id,
                "task_id": task_id,
                "message": [f"{e}"]
            }
            success = False
        finally:
            if task_id in self.future_dict:
                future = self.future_dict.pop(task_id)
                if success:
                    future.set_result(reply)
                else:
                    future.set_exception(reply)

    def _start_handler_thread(self):
        handler_thread = threading.Thread(target=self._handle, daemon=True)
        handler_thread.start()

ai_services_router = ModelRouter(ADAPTERS_LIST)

