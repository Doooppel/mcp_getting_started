import httpx


def web_search(query: str) -> str:
    """
    search on web
    :param query: content to be searched
    :return: summary
    """
    response = httpx.post(
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent',
        headers={
            'x-goog-api-key': os.getenv("OPENAI_KEY")},
        json={
            'contents': [
                {
                    'parts': [
                        {
                            'text': query
                        }
                    ]
                }
            ],
        },
        timeout=500
    )
    text = ""
    for element in response.json()['candidates']:
        for content in element['content']['parts']:
            text = content['text']
    print(text)
    return text


if __name__ == '__main__':
    web_search('ping')
