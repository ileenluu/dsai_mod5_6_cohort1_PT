#gemini

from flask import Flask,request,render_template
import google.generativeai as genai
import os
import sqlite3
import datetime
from web3 import Web3
from dotenv import load_dotenv
from sklearn import linear_model
from sklearn.metrics import mean_squared_error

load_dotenv() # <-- this loads .env file variables

gemini_api_key = os.getenv("gemini_api_key")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

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


@app.route("/gemini", methods=['GET', 'POST'])
def gemini():
    return(render_template('gemini.html')) 


@app.route("/gemini_reply",methods=["GET","POST"])
def gemini_reply():
    try:
        q = request.form.get("q")
        print(q)
        r = model.generate_content(q)
        reply_text = r.candidates[0].content.parts[0].text
        return render_template("gemini_reply.html", r=reply_text)
    except Exception as e:
        print("Error:", e)
        return f"Error occurred: {e}", 500
    
    
@app.route("/paynow",methods=["GET","POST"])
def paynow():
    return(render_template("paynow.html"))


@app.route("/prediction", methods=['GET', 'POST'])
def prediction():
    return(render_template('prediction.html'))


@app.route("/prediction_reply",methods=["GET","POST"])
def prediction_reply():
    q = float(request.form.get("q"))
    print(q)
    return(render_template("prediction_reply.html",r=90.2 + (-50.6*q)))


INFURA_URL = os.getenv("INFURA_URL")
print(INFURA_URL)
MetaMask_Private = os.getenv("MetaMask_Private")
print(MetaMask_Private)
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.from_key(MetaMask_Private)

@app.route("/")
def show_balance():
    balance_wei = w3.eth.get_balance(account.address)
    balance_eth = w3.fromWei(balance_wei, 'ether')
    return (
        f"✅ Wallet Address: {account.address}<br>"
        f"💰 Balance: {balance_eth} SepoliaETH"
        )

@app.route('/users', methods=['GET', 'POST'])
def users():
    # read all users
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row  # so we can use column names
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users order by timestamp')
    rows = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=rows)


@app.route("/user_log",methods=["GET","POST"])
def user_log():
    #read
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("select * from users")
    r=""
    for row in c:
        print(row)
        r= r+str(row)
    c.close()
    conn.close()
    return(render_template("user_log.html",r=r))


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
    app.run()