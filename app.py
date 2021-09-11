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

ACCEPTED_IP = ["127.0.0.1","14.3.59.247","126.51.248.65"]

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
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=True)

class Board_status(db.Model):
    b_id = db.Column(db.Integer, primary_key=True) 
    b_title = db.Column(db.String(100), nullable=False)
    create_user = db.Column(db.String(50))
    create_day = db.Column(db.DateTime)
    last_comment_day = db.Column(db.DateTime)
    num_comment = db.Column(db.Integer) 

class User_manage(db.Model):
    u_id = db.Column(db.Integer, primary_key=True) 
    u_name = db.Column(db.String(50), unique = True, nullable=False)
    u_password = db.Column(db.String(50), nullable=False)
    auth_flag = db.Column(db.Integer, nullable=True)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secret"

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password


user_manages = User_manage.query.all()
###ゴミみたいな処理いずれ改変予定
###つまりuser_checkにusers.valuesのパスワードとidを入れちょるだけ
# ユーザーチェックに使用する辞書作成
nested_dict = lambda: defaultdict(nested_dict)
user_check_for_db = nested_dict()
for i in user_manages:
    user_check_for_db[i.u_name]["password"] = i.u_password
    user_check_for_db[i.u_name]["id"] = i.u_id

@login_manager.user_loader
def load_user(user_id):
    #return users.get(int(user_id))

    user_collum = User_manage.query.get(int(user_id))
    iikagennnisiro_user = User(user_id, user_collum.u_name, user_collum.u_password)
    return iikagennnisiro_user

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
@ip_check
def ac_create():
    if(request.method == "POST"):

        print("返事は返されているか？")
        print(request.form["resist_username"])
        #print(request.form["resist_username"] in user_check)
        print()
        # ユーザーチェック
        if(request.form["resist_username"] in user_check_for_db):
                print("アカウントクリエイトのアボート")
                return render_template("account_create.html", fail_flag = True)
        else:
                #create_account_id = len(users)+1
                #users[create_account_id] = User(len(users)+1, request.form["resist_username"], request.form["resist_password"])
                #print("ああああ"+users[3].name)

                user_name = request.form.get('resist_username')
                user_password = request.form.get('resist_password')
                new_account = User_manage(u_name=user_name, u_password=user_password)

                db.session.add(new_account)
                db.session.commit()


                print("↓user_manageのデータベースから持ってきた対象カラムは（名前で指定）↓")
                print(user_name)
                #要修正点-ほんとはallで取得したくない
                ttt = User_manage.query.filter_by(u_name = user_name).all()[0].u_id
                #ttt[0].u_id
                print(ttt)


                user_check_for_db[request.form["resist_username"]]["password"] = request.form["resist_password"]
                #user_check_for_db[request.form["resist_username"]]["id"] = create_account_id
                user_check_for_db[request.form["resist_username"]]["id"] = User_manage.query.filter_by(u_name = user_name).all()[0].u_id


                user = User(ttt, user_name, user_password)

                # ユーザーが存在した場合はログイン
                login_user(user)
                #return redirect('/login_top/')
                return redirect('/login_top/')
    else:
        return render_template("account_create.html", fail_flag = False)

# ログインパス
@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        #user_manage = User_manage(request.form["username"],request.form["password"])


        #print(request.form["username"] in user_check)
        # ユーザーチェック
        if(request.form["username"] in user_check_for_db and request.form["password"] == user_check_for_db[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            #print(user_check_for_db[request.form["username"]]["id"])

            ttt_id = User_manage.query.filter_by(u_name = request.form["username"]).all()[0].u_id

            login_form_user_status = User(ttt_id, request.form["username"], request.form["password"])

            login_user(login_form_user_status)
            return redirect('/login_top/')
        else:
            print("ログイン画面のアボート")
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
    <a href="/login/">login</a><br />
    <a href="/">トップ画面へ</a>
    ''')


@app.route('/login_top/', methods={'POST', 'GET'})
@login_required
def index():
    if request.method == 'GET':
        #posts = Post.query.all()
        #return render_template('index.html', posts=posts)
        boards = Board_status.query.order_by(Board_status.last_comment_day.desc()).all()
        return render_template('index.html', boards=boards)
    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        #due = request.form.get('due')

        #due = datetime.strptime(due, '%Y-%m-%d')
        #new_post = Post(title=title, detail=detail)
        get_now_time = datetime.now()
        new_board = Board_status(b_title=title, create_user=request.form['username'], create_day=get_now_time, last_comment_day=get_now_time, num_comment=1)

        db.session.add(new_board)
        db.session.commit()
        #return redirect('/login_top/')
        return redirect('/login_top/')

@app.route('/login_top/create')
@login_required
def create():
    return render_template('create.html')

@app.route('/login_top/detail/<int:id>')
@login_required
def read(id):
    #post = Post.query.get(id)
    board = Board_status.query.get(id)
    #return render_template('detail.html', post=post)
    return render_template('detail.html', post=board)

@app.route('/login_top/update/<int:b_id>', methods={'GET', 'POST'})
@login_required
def update(b_id):

    print(b_id)

    #post = Post.query.get(id)
    board = Board_status.query.get(b_id)

    if request.method == 'GET':
        #updateのページ

        #テキストファイルがなかったら作成する↓要修正
        fi0 = open(board.b_title+".txt", 'a', encoding='UTF-8')
        fi0.close
        fi = open(board.b_title+".txt", 'r', encoding='UTF-8')
        all_comments = fi.read()
        print(all_comments)
        fi.close

        return render_template('update.html', board=board, all_comments=all_comments)
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

            
            f.write("\n")
            f.write("発言者："+request.form.get('username'))
            f.write("\n")
            f.write(str(datetime.now()))
            f.write("\n")
            f.write("========コメント内容========")
            f.write("\n")
            f.write(request.form.get('detail'))
            f.write("\n")
            f.write("========コメント内容========")
            f.write("\n")
            f.write("\n")
            f.write("##################################")
            f.write("\n\n")
            
            f.close

            board.last_comment_day = datetime.now()

            db.session.commit()

    
        # db.session.commit()
        return redirect('/login_top/')

@app.route('/login_top/delete/<int:b_id>')
@login_required
def delete(b_id):
    board = Board_status.query.get(b_id)
    db.session.delete(board)
    db.session.commit()
    return redirect('/login_top/')


if __name__ == "__main__":
    app.run()