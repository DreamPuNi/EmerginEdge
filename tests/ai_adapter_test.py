from config.config import load_config
from src.ai_services.routers.model_router import ai_services_router

test_request = {
    "user_id": "yingdaomayi",
    "task_id":"conversation_with_user_test_01010101",
    "adapter": "openai",
    "model_name": "gpt-3.5-turbo",
    "system_prompt": "你要扮演樱岛麻衣和用户对话",
    "messages": [
        {
            "role": "user",
            "content": "学姐在吗？"
        },
        {
            "role": "assistant",
            "content": "今天可真是稀奇，竟然主动来找我了呢。不过提前说好，奇怪的要求我可不会答应"
        },
        {
            "role": "user",
            "content": "什么是奇怪的要求？"
        }
    ],
    "parameters": {
        "temperature": 0.5,
        "max_tokens": 100,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
}

def run():
    future = ai_services_router.route(test_request)
    try:
        reply = future.result()
        print(f"收到 AI 回复: {reply}")
    except Exception as e:
        print(f"AI 任务失败: {e}")

"""
future = ai_services_router.route({"adapter": "gpt4", "task_id": "123"})

def process_result(fut):
    try:
        reply = fut.result()
        print("AI 回复:", reply)
    except Exception as e:
        print("发生错误:", e)

future.add_done_callback(process_result)  # 当 Future 结果出来后，自动调用 process_result

print("程序不会被阻塞，会继续执行其他逻辑...")
"""

if __name__ == "__main__":
    load_config()
    run()