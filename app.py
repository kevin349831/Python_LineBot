from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('8suvXUHjBNey25GGX1kvuip5RM2vNUyIxEgMqZVJYKW7cJuS3qKd9edtw5Y5s3UATnrdfEMjj3r/69SiztrtIcWLdqWpGmsIwmYIhAUGvdDbqOxzMiWmywaQMgSFbCb/ewJA0v2581gHdU/ZfK4OBAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b6b6b707c23e48e6b8f3b588ffdc3146')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = event.message.text)


if __name__ == "__main__":
    app.run()
