import requests
def test_new_endpoint():
    WEBHOOK_URL = "https://chatbot-492327799816.asia-south1.run.app"
    url = f"{WEBHOOK_URL}/chat.telegram"
    response = requests.get(url)
    assert response.status_code == 404