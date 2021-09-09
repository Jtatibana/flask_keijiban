from datetime import datetime, date
from os import name
from flask import Flask, render_template, request, redirect, url_for, Response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

#***********別ファイルに移植予定****************

ACCEPTED_IP = ["127.0.0.1","192.168.11.2"]

def ip_check(func):
    def wrapper(*args, **kwargs):
        if request.remote_addr in ACCEPTED_IP:
            print('IP Check : OK')
            return func(*args, **kwargs)
        else:
            print("403")
            return abort(403)
    return wrapper

#***********別ファイルに移植予定****************


class Post(db.Model):
    __tablename__="post"
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=True)

class UserResist(db.Model):
    __tablename__="user_manage"
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50))
    auth_flag = db.Column(db.Integer, nullable=True)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secret"

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# ログイン用ユーザー作成
users = {
    1: User(1, "user01", "password"),
    2: User(2, "user02", "password")
}


###ゴミみたいな処理いずれ改変予定
###つまりuser_checkにusers.valuesのパスワードとidを入れちょるだけ
# ユーザーチェックに使用する辞書作成
nested_dict = lambda: defaultdict(nested_dict)
user_check = nested_dict()
for i in users.values():
    user_check[i.name]["password"] = i.password
    user_check[i.name]["id"] = i.id

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route('/')
#@ip_check
def home():
    # return Response("home: <a href='/login/'>Login</a> <a href='/login_top/'>index画面</a> <a href='/logout/'>Logout</a>")
     return render_template("access_top.html")

# ログインしないと表示されないパス
@app.route('/protected/')
@login_required
def protected():
    return Response('''
    protected<br />
    <a href="/logout/">logout</a>
    ''')

# アカウントクリエイト
@app.route('/account_create/', methods=["GET", "POST"])
def ac_create():
    if(request.method == "POST"):

        print("返事は返されているか？")
        print(request.form["resist_username"])
        print(request.form["resist_username"] in user_check)
        print()
        # ユーザーチェック
        if(request.form["resist_username"] in user_check and request.form["resist_password"] == user_check[request.form["resist_username"]]["password"]):
                    return abort(401) 
        else:
                    create_account_id = len(users)+1
                    users[create_account_id] = User(len(users)+1, request.form["resist_username"], request.form["resist_password"])
                    print("ああああ"+users[3].name)

                    # user_name = request.form.get('resist_username')
                    # user_password = request.form.get('resist_password')
                    # new_account = UserResist(name=user_name, password=user_password)

                    #db.session.add(new_account)
                    #db.session.commit()


                    user_check[request.form["resist_username"]]["password"] = request.form["resist_password"]
                    user_check[request.form["resist_username"]]["id"] = create_account_id

                     # ユーザーが存在した場合はログイン
                    login_user(users[create_account_id])
                    return redirect('/login_top/')
    else:
        return render_template("account_create.html")

# ログインパス
@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        print(request.form["username"] in user_check)
        # ユーザーチェック
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            print(user_check[request.form["username"]]["id"])
            login_user(users.get(user_check[request.form["username"]]["id"]))
            return redirect('/login_top/')
        else:
            return abort(401)
    else:
        return render_template("login.html")

# ログアウトパス
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return Response('''
    logout success!<br />
    <a href="/login/">login</a>
    ''')


@app.route('/login_top/', methods={'POST', 'GET'})
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.due).all()
        return render_template('index.html', posts=posts, today=date.today())
    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')

        due = datetime.strptime(due, '%Y-%m-%d')
        new_post = Post(title=title, detail=detail, due=due)

        db.session.add(new_post)
        db.session.commit()
        return redirect('/login_top/')

@app.route('/login_top/create')
@login_required
def create():
    return render_template('create.html')

@app.route('/login_top/detail/<int:id>')
@login_required
def read(id):
    post = Post.query.get(id)
    return render_template('detail.html', post=post)

@app.route('/login_top/update/<int:id>', methods={'GET', 'POST'})
@login_required
def update(id):




    post = Post.query.get(id)
    print(post.detail)
 


    if request.method == 'GET':
        #updateのページ

        fi = open(post.title+".txt", 'r', encoding='UTF-8')
        aaa = fi.read()
        print(aaa)
        fi.close

        return render_template('update.html', post=post, aaa=aaa)
    else:
        # post.title = request.form.get('title')
        # post.detail = request.form.get('detail')
        # post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')

        if request.form.get('detail') != "":
            print(request.form.get('detail'))
            f = open(request.form.get('title')+'.txt', 'a', encoding='UTF-8')

            for key, value in request.form.items():
                print("===============")
                print(key, value)

            f.write("##################################")
            f.write("\n")
            f.write("発言者："+request.form.get('username'))
            f.write("\n")
            f.write("========コメント内容========")
            f.write("\n")
            f.write(request.form.get('detail'))
            f.write("\n")
            f.write("\n")
            f.write(str(datetime.now()))
            f.write("\n")
            f.write("##################################")
            f.write("\n\n")
            
            f.close

    
        # db.session.commit()
        return redirect('/login_top/')

@app.route('/login_top/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/login_top/')


if __name__ == "__main__":
    app.run()