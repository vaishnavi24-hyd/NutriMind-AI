import ollama

class ChatService:
    @staticmethod
    def generate_response(user_message: str, history: list) -> str:
        """
        Generates an AI response using the local Ollama llama3.2-vision model.
        """
        messages = []
        for msg in history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
            
        try:
            response = ollama.chat(
                model='llama3.2-vision',
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            return f"I'm sorry, I couldn't connect to my brain. Please make sure Ollama is running with the 'llama3.2-vision' model. Error: {str(e)}"
