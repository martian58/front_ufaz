from openai import OpenAI

class Bot:

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def chat(self,prompt):
        client = OpenAI(api_key=self.api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="gpt-3.5-turbo",  
        )
        return chat_completion.choices[0].message.content.strip()

    def response(self,user_input: str):
        response = self.chat(user_input)
        return(response)

