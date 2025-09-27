import httpx

class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", timeout: int = 60):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        self.headers = {"x-goog-api-key": self.api_key}

    def _parse_response(self, response: httpx.Response) -> str:
        data: dict = response.json()
        text: str = ""
        for element in data['candidates']:
            for content in element['content']['parts']:
                text = content['text']
        return text



    def generate(self, query: str) -> str:
        payload = {
            "contents": [
                {"parts": [{"text": query}]}
            ]
        }
        response = httpx.post(self.url, json=payload, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return self._parse_response(response)

    async def generate_async(self, query: str) -> str:
        payload = {
            "contents": [
                {"parts": [{"text": query}]}
            ]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return self._parse_response(response)