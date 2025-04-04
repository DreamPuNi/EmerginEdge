# 简介
用户发送任何和AI的对话消息都会交由这里进行处理，这是AI向外的专属数据交流口。仅用于用户与AI互动

# 管道消息

### 入格式

```json
{
  "sender_id": "user_id",
  "sender_type": "user",
  "receiver_id": "other_user_id",
  "room_id": "room_id",
  "task_type": "first_impression",
  "message": [
    {
      "type": "image",
      "content": "https://example.com/image.png"
    },
    {
      "type": "text",
      "content": "这是什么？"
    }
  ],
  "is_group": false,
  "timestamp": 1743495837
}
```

### 出格式
```json
{
  "sender_id": "user_id",
  "sender_type": "user",
  "receiver_id": "other_user_id",
  "room_id": "room_id",
  "task_type": "first_impression",
  "message": [
    {
      "type": "image",
      "content": "https://example.com/image.png"
    },
    {
      "type": "text",
      "content": "这是什么？"
    }
  ],
  "is_group": false,
  "timestamp": 1743495837
}
```

> 出的时候如果是AI的消息，那么user_id为什么呢？或者说怎么在数据库区分是人发的还是AI发的

### 管道格式：交由AI路由进行处理，拿到的返回组装为出格式

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
            "content": "https://example.com/image.png"
        },
        {
            "role": "user",
            "content": "这是什么？"
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

# 调用方法

# 调用过程

1. 消息首先进入 **dialog_flow** 进行初次处理，这里会根据 **target_id** 和 **task type** 进行任务识别
2. 识别时间戳，缓存进入 **user_analytics** 里面，并进行时间监控，存在超过20分钟就检查对话长度，然后进行用户分析
3. 进入 **prompt_engine** 进行系统提示词的获取，同时使用 **context_manager** 和 **memory_management** 进行上下文和记忆的处理
4. 在 **dialog_flow** 进行对话的处理，最后将消息发送到 **ai_services** 进行AI的调用