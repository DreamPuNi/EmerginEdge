class FormatAssistantReply():
    def __init__(self, response):
        self.response = response

    def clean_response(self, response):
        text = self.response.choices[0].text['content']

        cleaned_response = {
            "id": response.id,
            "timestamp": response.created,
            "message": [],
            "usage": response.usage
        }

        if text:
            cleaned_response["message"].append({
                "type": "text",
                "content": text
            })

        return cleaned_response