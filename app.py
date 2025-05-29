#gemini

from flask import Flask,request,render_template
import google.generativeai as genai
import os
import sqlite3
import datetime
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv() # <-- this loads .env file variables

# For connecting to Gemini API
gemini_api_key = os.getenv("gemini_api_key")
genai.configure(api_key=gemini_api_key)

# Initialize the Google Gemini client
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# For Telegram bot
gemini_telegram_token = os.getenv("gemini_telegram_token")


app = Flask(__name__)

first_time = 1


@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))


@app.route("/main",methods=["GET","POST"])
def main():
    global first_time
    if first_time==1:
        q = request.form.get("q")
        print(q)
        t = datetime.datetime.now()
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("insert into users(name,timestamp) values(?,?)",(q,t))
        conn.commit()
        c.close()
        conn.close()
        first_time=0
    return(render_template("main.html"))


@app.route("/gemini",methods=["GET","POST"])
def gemini():
    return(render_template("gemini.html"))


@app.route("/gemini_reply",methods=["GET","POST"])
def gemini_reply():
    try:
       
        # Set system prompt for financial question
        system_prompt = """
        You are a financial expert.  Answer ONLY questions related to finance, economics, investing, 
        and financial markets. If the question is not related to finance, 
        state that you cannot answer it. Answers should be summarised to max 50 words"""

        q = request.form.get("q")

        # Construct the prompt with system prompt and user query
        prompt = f"{system_prompt}\n\nUser Query: {q}"

        print("Received question:", q)
        response = gemini_model.generate_content(prompt)
        print("Gemini Response:", response.text)
        return render_template("gemini_reply.html", r=response.text)
    except Exception as e:
        print("❌ Error occurred:", e)
        return f"An error occurred: {e}", 500
    
    
@app.route("/paynow",methods=["GET","POST"])
def paynow():
    return(render_template("paynow.html"))


@app.route("/prediction",methods=["GET","POST"])
def prediction():
    return(render_template("prediction.html"))


@app.route("/prediction_reply",methods=["GET","POST"])
def prediction_reply():
    q = float(request.form.get("q"))
    result = 90.23 + (-50.6 * q)
    rounded_result = round(result, 2)  # Round to 2 decimal places
    return(render_template("prediction_reply.html",r=rounded_result))


@app.route("/start_telegram", methods=['GET', 'POST'])
def start_telegram():

    domain_url = os.getenv('WEBHOOK_URL')

    # The following line is used to delete the existing webhook URL for the Telegram bot.
    delete_webhook_url = f'https://api.telegram.org/bot{gemini_telegram_token}/deleteWebhook'
    requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})

    # Set the webhook URL for the Telegram bot
    set_webhook_url = f'https://api.telegram.org/bot{gemini_telegram_token}/setWebhook?url={domain_url}/telegram'
    webhook_response = requests.post(set_webhook_url, json={"url": domain_url, "drop_pending_updates": True})
    print('webhook:', webhook_response)
    if webhook_response.status_code == 200:
        # set status message
        status = 'The telegram bot is running. Please check with the telegram bot t.me/DSAI_Ilua_Gemini_bot'
    else:
        status = "Failed to start the telegram bot. Please check the logs."

    return(render_template("telegram.html", status=status))


@app.route("/telegram", methods=['GET', 'POST'])
def telegram():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        # Extract the chat ID and message text from the update
        chat_id = update['message']['chat']['id']
        text = update['message']['text']

        if text == '/start':
            r_text = "Welcome to FinGPT. I'm here to assist you with finance-related questions, feel free to ask."
        else:
            # Process the message and generate a response
            system_prompt = "You are a financial expert. Answer ONLY questions related to finance,economics, investing, and financial markets. If the question is not related to finance, state that you cannot answer it."
            prompt = f"{system_prompt}\n\nUser Query: {text}"
            r = gemini_model.generate_content(prompt)
            r_text = r.text

        # Send the response back to the user
        send_message_url = f"https://api.telegram.org/bot{gemini_telegram_token}/sendMessage"
        requests.post(send_message_url, data={"chat_id": chat_id, "text": r_text})
    # Return a 200 OK response to Telegram
    # This is important to acknowledge the receipt of the message
    # and prevent Telegram from resending the message
    # if the server doesn't respond in time
    return('ok', 200)



INFURA_URL = os.getenv("INFURA_URL")
print(INFURA_URL)
MetaMask_Private = os.getenv("MetaMask_Private")
print(MetaMask_Private)
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.from_key(MetaMask_Private)

@app.route("/")
def show_balance():
    try:
        print("🔁 Triggered / route")
        balance_wei = w3.eth.get_balance(account.address)
        balance_eth = w3.fromWei(balance_wei, 'ether')
        print(f"✅ Wallet Address: {account.address}")
        print(f"💰 Balance: {balance_eth} SepoliaETH")
        return (
            f"✅ Wallet Address: {account.address}<br>"
            f"💰 Balance: {balance_eth} SepoliaETH"
        )
    except Exception as e:
        print("❌ Error while checking balance:", e)
        return f"❌ Error: {str(e)}"
    

@app.route('/user_log', methods=['GET', 'POST'])
def user_log():
    # read all users
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row  # so we can use column names
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users order by timestamp')
    rows = cursor.fetchall()
    conn.close()
    return render_template('user_log.html', users=rows)


@app.route("/delete_log",methods=["GET","POST"])
def delete_log():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("delete from users")
    conn.commit()
    c.close()
    conn.close()
    return(render_template("delete_log.html"))

@app.route("/logout",methods=["GET","POST"])
def logout():
    global first_time
    first_time = 1
    return(render_template("index.html"))

if __name__ == "__main__":
    app.run(debug=True)