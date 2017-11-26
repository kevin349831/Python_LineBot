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

line_bot_api = LineBotApi('H/ONc3LzBop7jIt636/HtjoffNMr5PTwxLQ29kvsskpqv5+m8teC8lhQRzW9Iv+y4T7EdvvW+vulR9P509BYnvknPT6365cfCOjdbzcDv855Mg9aIzRBJ0ZOsfh5zeoWOA3wyjtc/26fBsyn0/EUjgdB04t89/1O/w1cDnyilFU=
')
handler = WebhookHandler('0357645035d0851034efe3e252196894')


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
