from src.core.utilities.log import logger
from src.core.middleware.queue_manage import get_msg_queue
from src.ai_services.adapters.adapters_list import ADAPTERS_LIST

class ModelRouter:
    def __init__(self, adapters):
        self.adapters = adapters
        self.message_queue = get_msg_queue()

    def route(self, request_data):
        """
        解析request_data并将解析后的AI实例放入消息列表

        Args:
            request_data: 请求数据
        """
        adapter_name = request_data.get["adapter"]
        if adapter_name not in self.adapters:
            logger.error(f"Unsupported adapter: {adapter_name}")
            raise ValueError(f"Unsupported adapter: {adapter_name}")
        adapter = self.adapters[adapter_name]
        # 在这里加上消息处理列表
        self.message_queue.put(adapter)

    # 在这里添加取出消息列表处理并进行reply decorate的函数
    def _handle(self):
        while True:
            adapter = self.message_queue.get()
            response = adapter.handle()

            # 在这里加上reply decorate

            self.message_queue.task_done()

ai_services_router = ModelRouter(ADAPTERS_LIST)
