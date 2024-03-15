import sqlite3
from flask import *
import pandas as pd
import openai
openai.api_key="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"

app = Flask(__name__)
app.secret_key = "addr_system"
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/ind')
def ind():
    return render_template('admin_index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/sign',methods=['POST'])
def sign():

    if request.method=='POST':
        name= request.form["name"]
        password = request.form['password']
        conn=sqlite3.connect("data.db")
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? and password=?", (name, password))
        user=cursor.fetchone()
        if user:
            role = user[3]
            if role == 'admin':
                session['user_id']=name
                session['user_role'] = user[3]
                return render_template('admin_index.html')
            elif role == 'student':
                session['user_id'] = name
                session['user_role'] = user[3]
                return render_template('index.html')

        else:
            return redirect(url_for('login'))
@app.route('/reg')
def reg():
    return render_template('register.html')

@app.route('/users')
def users():
    conn=sqlite3.connect('data.db')
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM users')
    user=cursor.fetchall()
    return render_template('user_details.html',user=user)

@app.route('/delete_user/<id>')
def delete_user(id):
    conn=sqlite3.connect('data.db')
    cursor=conn.cursor()
    cursor.execute('DELETE  FROM users WHERE id=?',(id,))
    conn.commit()
    return redirect(url_for('users'))


@app.route('/mes')
def mes():
    user=session.get("user_id")
    conn = sqlite3.connect('data.db')
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM msg ')
    rows=cursor.fetchall()
    return render_template('group.html',rows=rows, user=user)

@app.route('/stu_mes')
def stu_mes():
    user=session.get("user_id")
    conn = sqlite3.connect('data.db')
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM msg ')
    rows=cursor.fetchall()
    return render_template('stu_group.html',rows=rows, user=user)


@app.route('/delete_msg/<id>')
def delete_msg(id):
    conn=sqlite3.connect('data.db')
    cursor=conn.cursor()
    cursor.execute('DELETE FROM msg WHERE id=?',(id,))
    conn.commit()
    return redirect(url_for("his"))



@app.route('/msg',methods=['POST'])
def msg():
    if request.method == 'POST':
        name = request.form['name']
        msg = request.form['msg']
        conn = sqlite3.connect('data.db')
        conn.execute("INSERT INTO msg(name,m) VALUES(?,?)",(name,msg))
        conn.commit()
        return redirect(url_for('mes'))


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if request.method == 'POST':
        name = request.form.get("name")
        password = request.form.get('password')
        type = request.form.get('type')
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET email=?, password=?, role=? WHERE id=?",
            (name, password, type, id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('users'))
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id=?', (id,))
    data = cursor.fetchone()

    return render_template('edit_user.html', data=data)

@app.route('/sub_reg', methods=['POST'])
def sub_reg():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        type = request.form.get('type')
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password, role) VALUES (?, ?, ?)',
                       (email, password, type))
        conn.commit()

        msg = 'successfully added'
        return render_template('admin_index.html', msg=msg)


@app.route('/get', methods=['POST'])
def get_response():
    user_message = request.form['msg']

    # Split the user's message into a list using spaces as the delimiter
    user_message_list = user_message.split()
    print(user_message_list)

    user_message_lower = [word.lower() for word in user_message_list]

    if "hi" in user_message_lower:
        print("hello")
        bot_response = "Hello! I'm your virtual assistant. How may I assist you? You can choose from the following options: Technical Support, Buy a Product."

    elif "buy" in user_message_lower and "product" in user_message_lower:
        bot_response = "To buy a product, visit our online store at <a href='http://msksolutions.org' target='_blank'>msksolutions.org</a>"

    elif "how are you" in user_message_lower:
        bot_response = "I am good, thanks for asking!"

    else:
        csv_file_path = 'data.csv'  # Update this to your CSV file path

        df = pd.read_csv(csv_file_path, encoding='latin1')

        questions_data = list(df['question'])
        print(questions_data)
        answer_data = df['answer']

        user_question = ' '.join(user_message_list)

        # Check if the question exists in the DataFrame
        if user_question in questions_data:
            exact_answer = df.loc[df['question'] == user_question, 'answer'].iloc[0]
            print(exact_answer)
            bot_response = str(exact_answer)
            print(bot_response)
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "assistant", "content": user_question}]
            )

            bot_responses = response['choices'][0]['message']['content']
            bot_response = bot_responses.split(".")[0]
            bot_response = bot_response.replace("OpenAI", "MSK")

    save_to_database(user_message, bot_response)

    return jsonify({'status': 'success', 'bot_response': bot_response})
def save_to_database(user_message,bot_response):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''
            INSERT INTO chat_history (user_message, bot_response)
            VALUES (?, ?)
        ''', (user_message, bot_response))
    conn.commit()
    conn.close()


@app.route('/chatter')
def chatter():
    return render_template('chatter.html')

@app.route('/stu_chatter')
def stu_chatter():
    return render_template('stu_chatter.html')


@app.route('/his')
def his():
    conn=sqlite3.connect('data.db')
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM msg ')
    data=cursor.fetchall()
    conn.close()

    return render_template('history.html', data=data)

@app.route('/history')
def history():
    conn=sqlite3.connect('data.db')
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM msg ')
    data=cursor.fetchall()
    conn.close()
    return render_template("stu_histroy.html", data=data)

@app.route('/bot_histroy')
def bot_histroy():
    conn=sqlite3.connect('data.db')
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM chat_history ')
    data=cursor.fetchall()
    conn.close()

    return render_template('bot_histroy.html', data=data)

@app.route('/ad_bot_histroy')
def ad_bot_histroy():
    conn=sqlite3.connect('data.db')
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM chat_history ')
    data=cursor.fetchall()
    conn.close()

    return render_template('ad_bot_histroy.html', data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5050')
