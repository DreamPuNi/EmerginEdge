from queue import Full, Queue
from time import monotonic as time

class Dequeue(Queue):
    def _putleft(self, item):
        self.queue.appendleft(item)

    def putleft(self, item, block=True, timeout=None):
        with self.not_full:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._putleft(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def putleft_nowait(self, item):
        return self.putleft(item, block=False)

def get_msg_queue(maxsize=20):
    """
    这里是ai_services里面的queue，主要是存储了与AI通信的实例

    内部序列(user_id, task_id, adapter)：
        user_id: 当前处理的消息的来源用户
        task_id: 当前消息的任务id
        adapter: 当前消息的适配器实例
    """
    if not hasattr(get_msg_queue, "_instance"):
        get_msg_queue._instance = Dequeue(maxsize)
    return get_msg_queue._instance

def get_dispatch_queue(maxsize=20):
    """
    这里是对话系统的分发queue，主要是存储所有用户的新消息序列，不管是发送给ai还是另外的user

    内部消息:
        直接就是DispatchMessage实例，定义于src.conversation_system.message_instance中
    """
    if not hasattr(get_dispatch_queue, "_instance"):
        get_dispatch_queue._instance = Dequeue(maxsize)
    return get_dispatch_queue._instance

def get_event_queue(maxsize=20):
    if not hasattr(get_event_queue, "_instance"):
        get_event_queue._instance = Dequeue(maxsize)
    return get_event_queue._instance