class FormatAssistantReply():
    def __init__(self):
        pass

    def clean_response(self, user_id, task_id, response):
        generated_message = response.choices[0].message.content

        cleaned_response = {
            "success": True,
            "user_id": user_id,
            "task_id": task_id,
            "timestamp": response.created,
            "message": [],
            "usage": response.usage
        }

        if generated_message:
            cleaned_response["message"].append({
                "type": "text",
                "content": generated_message
            })

        return cleaned_response