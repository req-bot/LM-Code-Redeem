import flask_login
from flask import Flask, render_template, request, jsonify, redirect, url_for
from threading import Thread
import requests
import re
import os
import pandas as pd
from datetime import timedelta

CLEANR = re.compile('<.*?>')
curr_acc=""
acc_data=dict()

if(os.environ.get('secret')==None):
    raise Exception("Environment Variables are Not Set")
else:
    print("All is well")

def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext

app = Flask(__name__)
app.secret_key = os.environ.get('secret')
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=120)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
users = eval(os.environ.get('accounts'))


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user

login_html=''' <head><link rel="icon" href="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSFPLKMicv1lSDv-jU70q9aMk3NqD4tstNi5Q&usqp=CAU"> <style> .align { display: grid; -webkit-box-align: center; -ms-flex-align: center; align-items: center; justify-items: center; place-items: center; } /* helpers/grid.css */ :root { --gridMaxWidth: 24em; --gridWidth: 90%; } .grid { width: 90%; width: var(--gridWidth); margin-left: auto; margin-right: auto; max-width: 24em; max-width: var(--gridMaxWidth); margin-top:10%; } .home { color: red; } .home:hover { color: lime; } /* helpers/icon.css */ .icon { height: 1.25em; display: inline-block; width: 1.25em; line-height: 1.25em; margin-right: 0.625em; text-align: center; vertical-align: middle; } .icon--info { background-color: #e5e5e5; border-radius: 50%; } /* layout/base.css */ :root { --bodyBackgroundColor: #eaeaea; --bodyFontFamily: 'Helvetica', 'Arial'; --bodyFontFamilyFallback: sans-serif; --bodyFontSize: 0.875rem; --bodyFontWeight: 400; --bodyLineHeight: 1.5; } *, *::before, *::after { -webkit-box-sizing: inherit; box-sizing: inherit; } html { -webkit-box-sizing: border-box; box-sizing: border-box; } body { background-color: #eaeaea; background-color: var(--bodyBackgroundColor); font-family: 'Helvetica', 'Arial', sans-serif; font-family: var(--bodyFontFamily), var(--bodyFontFamilyFallback); font-size: 0.875rem; font-size: var(--bodyFontSize); font-weight: 400; font-weight: var(--bodyFontWeight); line-height: 1.5; line-height: var(--bodyLineHeight); margin: 0; min-height: 100vh; } /* modules/anchor.css */ :root { --anchorColor: inherit; --anchorHoverColor: #1dabb8; } body { background-attachment: fixed; background-image: url('https://ia800206.us.archive.org/2/items/UHDWalpaper13/Nature/UHDWalpaper%20(10).jpg'); background-size: 100% 100%; } a { color: inherit; color: var(--anchorColor); text-decoration: none; -webkit-transition: color 0.3s; -o-transition: color 0.3s; transition: color 0.3s; } .login__footer a:hover { color: #1dabb8; color: var(--anchorHoverColor); } /* modules/form.css */ fieldset { border: none; margin: 0; } input { -webkit-appearance: none; -moz-appearance: none; appearance: none; border: none; font: inherit; margin: 0; outline: none; padding: 0; } input[type='submit'] { cursor: pointer; } .form input[type='email'], .form input[type='password'] { width: 100%; } /* modules/login.css */ :root { --loginBorderRadius: 0.25em; --loginHeaderBackgroundColor: #282830; --loginInputBorderRadius: 0.25em; } .login__header { background-color: #282830; background-color: var(--loginHeaderBackgroundColor); border-top-left-radius: 0.25em; border-top-left-radius: var(--loginBorderRadius); border-top-right-radius: 0.25em; border-top-right-radius: var(--loginBorderRadius); color: #fff; padding: 1.5em; text-align: center; text-transform: uppercase; } .login__title { font-size: 1rem; margin: 0; } .login__body { background-color: #fff; padding: 1.5em; position: relative; } .login__body::before { background-color: #fff; content: ''; height: 0.5em; left: 50%; margin-left: -0.25em; margin-top: -0.25em; position: absolute; top: 0; -webkit-transform: rotate(45deg); -ms-transform: rotate(45deg); transform: rotate(45deg); width: 0.5em; } .login input[type='email'], .login input[type='password'] { border: 0.0625em solid #e5e5e5; padding: 1em 1.25em; } .login input[type='email'] { border-top-left-radius: 0.25em; border-top-left-radius: var(--loginInputBorderRadius); border-top-right-radius: 0.25em; border-top-right-radius: var(--loginInputBorderRadius); } .login input[type='password'] { border-bottom-left-radius: 0.25em; border-bottom-left-radius: var(--loginInputBorderRadius); border-bottom-right-radius: 0.25em; border-bottom-right-radius: var(--loginInputBorderRadius); border-top: 0; } .login input[type='submit'] { background-color: #1dabb8; border-radius: 0.25em; border-radius: var(--loginInputBorderRadius); color: #fff; font-weight: 700; -webkit-box-ordinal-group: 2; -ms-flex-order: 1; order: 1; padding: 0.75em 1.25em; -webkit-transition: background-color 0.3s; -o-transition: background-color 0.3s; transition: background-color 0.3s; } .login input[type='submit']:focus, .login input[type='submit']:hover { background-color: #198d98; } .login__footer { -webkit-box-align: center; -ms-flex-align: center; align-items: center; background-color: #fff; border-bottom-left-radius: 0.25em; border-bottom-left-radius: var(--loginBorderRadius); border-bottom-right-radius: 0.25em; border-bottom-right-radius: var(--loginBorderRadius); display: -webkit-box; display: -ms-flexbox; display: flex; -webkit-box-pack: justify; -ms-flex-pack: justify; justify-content: space-between; padding-bottom: 1.5em; padding-left: 1.5em; padding-right: 1.5em; } .login__footer p { margin: 0; } nav { width: 100%; height: 50px; line-height: 50px; } nav ul { float: right; margin-right: 30px; } nav ul li { list-style-type: none; display: inline-block; transition: 0.7s all; font-size: 25px; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; border: 2px solid transparent; outline: none; } nav ul li:hover { background-color: rgb(58, 58, 252); border: 2px solid rgb(22, 223, 223); border-radius: 25px; } nav ul li a { text-decoration: none; color: #fff; padding: 30px; font-weight: 500; } </style> </head> <body> <div class="align"> <nav> <ul> <!-- <li><a href="#">Discover</a></li> --> <li><a href="/" class="home">Home</a></li> <!-- <li><a href="#">History</a></li> --> <li><a href="/login">Login</a></li> <li><a href="/logout">Log Out</a></li> </ul> </nav> </div> <div class="grid"> <form action='login' method='POST' class="form login"> <header class="login__header"> <h3 class="login__title">Login</h3> </header> <div class="login__body"> <div class="form__field"> <input type='email' name='email' id='email' placeholder='email' required> </div> <div class="form__field"> <input type='password' name='password' id='password' placeholder='password' required> </div> </div> <footer class="login__footer"> <input type='submit' name='submit'"> <p><span class="icon icon--info">?</span><a href="#">Forgot Password</a></p> </footer> </form> </div> </body> '''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return login_html

    email = request.form['email']
    if email in users and request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('protected'))
        # return redirect("/", code=302)

    return """<script>alert('Bad Login');window.location.replace("/");</script>"""

@app.route('/redirected-login', methods=['GET', 'POST'])
def redirected_login():
    if request.method == 'GET':
        return """<script>alert('Restricted Access');window.location.replace("https://req-bot.github.io/Validator/");</script>"""

    email = request.form['email']
    if email in users and request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('protected'))

    return """<script>alert('Bad Login');window.location.replace("https://req-bot.github.io/Validator/");</script>"""

@app.route('/protected')
@flask_login.login_required
def protected():
    global curr_acc
    its_id=flask_login.current_user.id
    curr_acc=its_id
    print("User Logged In Successfully..!!!")
    return """<script>alert('Logged in as: {0}');window.location.replace("/");</script>""".format(its_id)


@app.route('/logout')
def logout():
    its_id=flask_login.current_user.id
    print("User Logged Out Successfully..!!!")
    flask_login.logout_user()
    return """<script>alert('Logged out of: {0}');window.location.replace("https://req-bot.github.io/Validator/");</script>""".format(its_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    # return 'Unauthorized', 401
    return redirect("https://req-bot.github.io/Validator/", code=302)


data = dict()
codes = []
old_code = ""
pi=1
kk=[]
logs_data=dict()
while(os.environ.get('sheet'+str(pi))!=None):
    kk.append(os.environ.get('sheet'+str(pi)))
    pi=pi+1

print("Data Feeded Successfully...")

# kk = [os.environ.get('sheet1'),os.environ.get('sheet2')]
for i in range(len(kk)):
    data[str(i+1)] = dict()

total_acc=0

def sub_redeem(cid, name, acc_mail, code, sheetno):
    global acc_data,data,logs_data
    # print(cid,name,sheetno)
    URL = 'https://lordsmobile.igg.com/project/gifts/ajax.php?game_id=1051029902'
    payload = {
        'ac': 'get_gifts',
        'type': '0',
        'iggid': str(cid),
        'charname': '',
        'cdkey': str(code),
        'lang': 'en',
    }
    response = requests.post(URL, data=payload)
    # print(response.text)
    finalme = str(response.json()['msg'])
    finalme = cleanhtml(finalme)
    # print(code,name,cid,finalme,sheetno)
    data[str(sheetno)][code][name] = {
        "Game Name": name, "Game ID": cid, "Gifts/Message": finalme}
    if(acc_mail==curr_acc):
        acc_data[name]={"Game Name": name, "Gifts/Message": finalme}
    logs_data[name]={"Game Name": name, "Gifts/Message": finalme}

def mid_redeem(kk,code,j):
    global total_acc
    dataf = pd.read_csv(kk[j])
    temp = list(dataf['ID'])
    total_acc=total_acc+len(temp)
    names = list(dataf['Game Name'])
    acc_mail=list(dataf['WebID'])
    c = len(temp)
    for i in range(1, c + 1):
        background_thread = Thread(target=sub_redeem, args=(
            temp[i-1], names[i-1],acc_mail[i-1], code, j+1))
        background_thread.start()

def redeem(code):
    import datetime
    import random
    itime=datetime.datetime.now()
    global codes,data,total_acc
    total_acc=0
    codes.append(code)
    global acc_data,logs_data
    acc_data=dict()
    logs_data=dict()
    for j in range(len(kk)):
        data[str(j+1)][code] = dict()
        background_thread = Thread(target=mid_redeem, args=(kk,code,j))
        background_thread.start()
    while(total_acc!=len(logs_data.keys()) or total_acc==0 or len(logs_data.keys())==0):
        pass
    mtime=datetime.datetime.now()
    difference = mtime - itime
    total_time=difference
    from discord_webhook import DiscordWebhook, DiscordEmbed
    imgs=['https://media.istockphoto.com/id/517188688/photo/mountain-landscape.jpg?s=612x612&w=0&k=20&c=A63koPKaCyIwQWOTFBRWXj_PwCrR4cEoOw2S9Q7yVl8=','https://wallpaperset.com/w/full/1/6/4/125537.jpg','https://hips.hearstapps.com/hmg-prod/images/meadow-in-rocky-mountain-national-park-royalty-free-image-1592402262.jpg','https://img.freepik.com/free-photo/wide-angle-shot-single-tree-growing-clouded-sky-during-sunset-surrounded-by-grass_181624-22807.jpg?size=626&ext=jpg&ga=GA1.2.574225619.1677755888&semt=ais','https://thumbs.dreamstime.com/b/nature-panorama-mountain-landscape-sunset-norway-44518447.jpg','https://thumbs.dreamstime.com/b/landscape-nature-mountan-alps-rainbow-76824355.jpg','https://images.hdqwalls.com/download/best-nature-image-1440x900.jpg','https://www.teahub.io/photos/full/13-137210_best-nature-wallpapers-ever-wallpaper-nature-hd.jpg','https://w0.peakpx.com/wallpaper/867/35/HD-wallpaper-best-nature-views-scenery.jpg','https://images.unsplash.com/photo-1610878180933-123728745d22?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8Y2FuYWRhJTIwbmF0dXJlfGVufDB8fDB8fA%3D%3D&w=1000&q=80','https://i.natgeofe.com/n/e16c207c-c151-47ea-bbfd-85bafefc19ee/18-iconic-patagonia-torres-del-paine-national-park-chile.jpg?w=636&h=425','https://media.istockphoto.com/id/1350993173/photo/winding-coast-road-in-corsica.jpg?b=1&s=170667a&w=0&k=20&c=ysJU3NQUzj_GgVmwtCVvwa8XzzWPfnF3OSh3i4MxLIQ=']
    itsmyurl=os.environ.get("webhook_url")
    webhook = DiscordWebhook(url=itsmyurl)
    embed = DiscordEmbed(title='Here is Report For You 📝', description="🚀 For Code :- '**{0}**' Redeemption is Successful ✅".format(code), color='03b2f8')
    embed.set_author(name='Royal 😎', icon_url='https://cdn.pixabay.com/photo/2016/12/28/08/15/hummingbird-1935665__340.png')
    embed.set_image(url=random.choice(imgs))
    embed.set_thumbnail(url='https://raw.githubusercontent.com/req-bot/LM-Code-Redeem/master/LionKingLogo.jpg')
    embed.set_footer(text='Time Taken :- ' + str(total_time.total_seconds()) + " seconds", icon_url='https://png.pngtree.com/element_pic/00/16/09/2057e0eecf792fb.jpg')
    embed.set_timestamp()
    for k in logs_data.keys():
        embed.add_embed_field(name="😎  "+str(k) +"  🤗", value="> "+str(logs_data[k]["Gifts/Message"])+"\n🧿 ~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~ ⛄ ~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~~-~ 🧿", inline=False)
    webhook.add_embed(embed)
    response = webhook.execute()

@app.route("/", methods=["POST", "GET"])
@flask_login.login_required
def home():
    global curr_acc,codes
    curr_acc=flask_login.current_user.id
    global old_code
    if request.method == "POST":
        code = request.form.get("todo")
        code = code.upper()
        # print("Received code :-",code)
        if code in codes:
            print("code was duplicate")
            return render_template('home.html')
        old_code = code
        background_thread = Thread(target=redeem, args=(code,))
        background_thread.start()
    return render_template('home.html')


# background data feed to home page
@app.route("/result", methods=["POST", "GET"])
@flask_login.login_required
def result():
    try:
        tmpd = dict()
        global data, old_code
        sheetno = request.args.get('sheetno')
        l = []
        for v in data[str(sheetno)][old_code]:
            l.append(data[str(sheetno)][old_code][v])
        tmpd["code"] = old_code
        tmpd["rdata"] = l
        return jsonify(tmpd)
    except Exception as e:
        print(e)
        return "{0}",format(e)

@app.route("/gifts", methods=["POST", "GET"])
@flask_login.login_required
def gifts():
    global old_code
    its_tmp=dict()
    try:
        l = []
        for v in acc_data:
            l.append(acc_data[v])
        its_tmp["code"]=old_code
        its_tmp["rdata"] = l
        return jsonify(its_tmp)
    except Exception as e:
        print(e)
        return "{0}",format(str(e))

# latest code result only respect to sheet
@app.route("/sheet-results", methods=["POST", "GET"])
@flask_login.login_required
def sheet_results():
    global data, old_code
    sheetno = request.args.get('sheetno')
    return render_template('sheet-results.html', value=data[str(sheetno)][old_code], key=old_code)


@app.route("/data", methods=["POST", "GET"])  # data api
@flask_login.login_required
def send_data():
    global data
    sheetno = request.args.get('sheetno')
    # print("sheet no. :-",sheetno)
    return jsonify(data[str(sheetno)])


@app.route("/reset", methods=["POST", "GET"])
@flask_login.login_required
def reset():
    global codes
    codes = []


@app.route("/codefromrequest", methods=["POST", "GET"])
def codefromrequest():
    global old_code
    code = request.args.get("code")
    if(code == None):
        return "Empty Code"
    code = code.upper()
    # print("Received code :-",code)
    if code in codes:
        print("code was duplicate")
        return render_template('home.html')
    old_code = code
    background_thread = Thread(target=redeem, args=(code,))
    background_thread.start()
    return "code added to task successfully"

@app.route("/awake", methods=["POST", "GET"])
def awake():
    return "Yes I Am On..!!!"

if __name__ == '__main__':
    app.run(debug=True)
