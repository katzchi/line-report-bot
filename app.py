import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# LINE Bot 設定
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# Google Apps Script URL
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyWRJ5zuSq66LxfS0AL80M7e7D5lBenbSKVNEGld8WffRa31KlOP_fQiyPaAo-nWDXA/exec"

@app.route("/")
def home():
    return "LINE Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    
    if text == '/報表':
        try:
            # 回覆確認訊息
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="收到報表請求，處理中...")
            )
            
            # 呼叫 Google Apps Script
            response = requests.post(APPS_SCRIPT_URL)
            
            if response.status_code == 200:
                print("成功呼叫 Google Apps Script")
            else:
                print(f"呼叫失敗: {response.status_code}")
                
        except Exception as e:
            print(f"發生錯誤: {str(e)}")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"發生錯誤: {str(e)}")
            )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
