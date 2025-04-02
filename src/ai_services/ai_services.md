# 文件架构
```txt
ai_services/
├── adapters/                   # AI渠道的分别实现及统一封装
│   ├── adapters_list           # 管理所有的AI渠道
│   └── openai_adapter          # 支持openai库的模型的适配器
├── interfaces/                 # 统一格式化AI渠道的输出
│   └── adapter_return          # 格式化输出
├── routers/                    # AI路由，根据不同的管道消息拉起不同的AI
│   ├── model_router            # 路由模块
│   └── model_to_url            # 这里存着各个AI和他们对应的url地址,需要添加新的AI支持就在这里添加设置，然后是config
└── ai_services.md              # 本模块说明文档
```

# 管道消息
### 入格式
```json
{
    "user_id": "user_id",
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
```

### 出格式
```json
{
  "success": true, 
  "user_id": "user_id",
  "task_id": "conversation_with_user_test_01010101", 
  "timestamp": 1743495837, 
  "message": [
    {
      "type": "text", 
      "content": "比如让我帮你写作业、做项目，或者帮你追男生之类的。我可是学姐，要给你树立好榜样哦。"
    }
  ], 
  "usage": CompletionUsage(completion_tokens=50, prompt_tokens=101, total_tokens=151, completion_tokens_details=None, prompt_tokens_details=None)
}
```

# 调用方法
首先导入 `from src.ai_services.routers.model_router import ai_services_router` 然后直接使用 `future = ai_services_router.route(test_request)` 即可获取消息
```python
# 导入AI路由模块
from src.ai_services.routers.model_router import ai_services_router

# 构造消息
test_request = "构造的入格式管道消息"

# 构建AI事件序列并获取输出
future = ai_services_router.route(test_request)

# 阻塞获取回复
reply = future.result()

# 回调处理获取回复
def process_result(fut):
    try:
        reply = fut.result()
        print("AI回复：",reply)
    except Exception as e:
        print("发生错误：",e)
future.add_done_callback(process_result) # 当 Future 结果出来后，自动调用 process_result
```

# 调用架构
包装好的管道消息 -> model_router读取adapter参数启动相应的adapter -> adapter根据模型名及参数组装发送的API消息体 -> 将消息体放入msg_queue队列 -> model_router会不断调用_handler方法处理消息列表 -> 将处理完成收到回复的消息返回到future