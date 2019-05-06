# coding: utf-8
# Author: Bust Solutions

import bottle
from bottle import run, route, error, template, static_file, request, get
import psycopg2
import passlib
from passlib.hash import pbkdf2_sha256
from dbcredentials import userN, hostN, passwordN, databaseN 


bottle.TEMPLATE_PATH.insert(0, 'views')


@route("/")
def index():
    """Displays the landing page"""
    return template("index")


# Written by: Anton
def LoginError():
    """Function for flashing the error for login route"""
    with open('flash.txt', 'r') as file:
      Flash = file.read().replace('\n', '')
    return Flash


# Written by: Anton
def GetTheUser(UserEmail):
    """Function that retrieves specific user from the database"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    sql = """SELECT user_id, admin, user_email, user_password FROM PERSON where user_email = %s;"""
    cur.execute(sql, (UserEmail,))
    User = cur.fetchone()
    conn.close()
    print(User)
    return User


# Written by: Anton
# check if login is requiered to reach deeper templates.
@route("/user-login", method="POST")
def LoginCheck():
    """Function that retrieves the data from the login form and checks the credentials"""
    LoginInfo = [getattr(request.forms, "InputUserEmail1"), 
                 getattr(request.forms, "InputPassword1")]
    User = GetTheUser(LoginInfo[0])
    print(User)
    errorFlash = LoginError()
    UserId = User[0] 
    print(UserId)
    Admin = User[1] 
    UserEmail = User[2] 
    UserPassword = User[3]
    if LoginInfo[0] == UserEmail and pbkdf2_sha256.verify(LoginInfo[1], UserPassword) is True:
      if Admin == True:
          return template("admin-page", UId = UserId)
      elif Admin == False:
          return template("user-page", UId = UserId)
    else:
        return template("login-page"), errorFlash


@route("/login-page")
def Login():
    """Displays the login page"""
    return template("login-page")


@route("/register-page")
def Register():
    """Displays the register page"""
    return template("register-page")


def GetHomeName(UserId):
    """Function that gets the adress and home name of the admin logged in"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    sql = "SELECT home_name from PERSON join LIVES_IN on PERSON.user_id = LIVES_IN.user_id join HOME on LIVES_IN.home_id = HOME.home_id where PERSON.user_id = %s;"
    cur.execute(sql, (UserId,))
    HomeName = cur.fetchone()
    return HomeName


@route("/add-subuser/<UId>")
def RegisterSubUser(UId):
    """Displays the register page"""
    HomeInfo = GetHomeName(UId)
    print(HomeInfo)
    return template("register-subuser-page", HomeName=HomeInfo, UId=UId)


# Written by: Anton
def user_reg(userInfo):
    """Function that adds the user to the database"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    sql = """INSERT into PERSON(user_name, user_email, admin, user_password) values(%s, %s, %s, %s);"""
    cur.execute(sql, (userInfo[0], userInfo[1], userInfo[3], userInfo[2]))
    conn.commit()
    conn.close()


# Written by: Anton
@route("/show-users/<UId>")
def ShowUsers(UId):
    HomeName = GetHomeName(UId)
    return template("show-users", Users=GetUsers(HomeName), UId=UId)


# Written by: Anton
def GetUsers(HomeName):
    """Function that returns all users of a specific household"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    sql = "SELECT user_name from PERSON join LIVES_IN on PERSON.user_id = LIVES_IN.user_id join HOME on LIVES_IN.home_id = HOME.home_id where home_name = %s;"
    cur.execute(sql, (HomeName,))
    Users = cur.fetchall()
    return Users


#Written by: Victor
@route("/show-issues/<UId>")
def ShowIssues(UId):
    UsersChores = GetChores(UId)
    print(UsersChores)
    return template("show-issues", Chores=UsersChores, UId=UId)


# Written by: Niklas & Victor
def issue_reg(UserInfo):
    """Function that adds the issue to the database"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    Name = UserInfo[0]
    Descript = UserInfo[1]
    Worth = UserInfo[2]
    Sql = """INSERT into CHORE(chore_name, chore_description, chore_worth) values(%s, %s, %s);"""
    cur.execute(Sql, (Name, Descript, Worth))
    Sql2 = """SELECT chore_id FROM CHORE order by chore_id DESC limit 1"""
    print (Sql2)
    cur.execute(Sql2)
    ChoreInfo = cur.fetchone()
    ChoreId = ChoreInfo[0]
    Sql3 = """INSERT into RESPONSIBILITY(chore_id, user_id) values(%s, %s)"""
    cur.execute(Sql3, (ChoreId, UserInfo[3]))
    conn.commit()
    conn.close()


# Written by: Anton
def home_reg(UserEmail, HomeName):
    """Function that adds the Home to the database"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    Sql = """INSERT into HOME(home_name) values(%s);"""
    cur.execute(Sql, (HomeName,))
    Sql2 = """Select user_id from PERSON where user_email = %s"""
    cur.execute(Sql2, (UserEmail,))
    UserInfo = cur.fetchone()
    UId = UserInfo[0]
    Sql3 = """Select home_id from HOME order by home_id DESC limit 1"""
    cur.execute(Sql3)
    HomeInfo = cur.fetchone()
    HomeId = HomeInfo[0]
    Sql4 = """INSERT into LIVES_IN(home_id, user_id) values(%s, %s)"""
    cur.execute(Sql4, (HomeId, UId))
    conn.commit()
    conn.close()


# Written by: Anton
@route("/user-registration/<UId>", method="POST")
def capture_registration(UId):
    """Function that retrieves the data from the registration form"""
    userInfo = [getattr(request.forms, "inputUserName4"), 
                getattr(request.forms, "inputEmail4"),
                pbkdf2_sha256.hash(getattr(request.forms, "inputPassword4")),
                getattr(request.forms, "inputAdmin4"),
                getattr(request.forms, "inputHomeName4")]
    user_reg(userInfo)
    home_reg(userInfo[1], userInfo[4])
    return template("successful-registration")
    
@route("/subuser-registration/<UId>", method="POST")
def CaptureSubuserRegistration(UId):
    """Function that retrieves the data from the registration form"""
    userInfo = [getattr(request.forms, "inputUserName4"), 
                getattr(request.forms, "inputEmail4"),
                pbkdf2_sha256.hash(getattr(request.forms, "inputPassword4")),
                getattr(request.forms, "inputAdmin4")]
    user_reg(userInfo)
    RegLivesIn(userInfo[1], UId)
    return template("admin-page", UId=UId)

def RegLivesIn(UserEmail, UId):
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    Sql = """Select home_id from LIVES_IN where user_id = %s"""
    cur.execute(Sql, (UId,))
    HomeId = cur.fetchone()
    Sql2 = """Select user_id from PERSON where user_email = %s"""
    cur.execute(Sql2, (UserEmail,))
    UserInfo = cur.fetchone()
    SUId = UserInfo[0]
    Sql4 = """INSERT into LIVES_IN(home_id, user_id) values(%s, %s)"""
    cur.execute(Sql4, (HomeId, SUId))
    conn.commit()
    conn.close()


#ISSUES NEEDS TO BE COLLECTED AND ADDED FOR A SPECIFIC HOUSEHOLD !
# Written by: Niklas & Victor & Gustaf
@route("/choreReg/<UId>", method="POST")
def capture_issue(UId):
    """Function that retrieves the data from the create-issue form"""
    issueInfo = [getattr(request.forms, "InputNameIssue"),
                getattr(request.forms, "CommentIssue"),
                getattr(request.forms, "WorthIssue"),
                getattr(request.forms, "UserIssue")]
    issue_reg(issueInfo)
    return template("admin-page", UId=UId)

#Written by: Victor and Niklas
@route("/bank/<UId>")
def ShowBank(UId):
    UsersPoints = GetBank(UId)
    return template("bank", points=UsersPoints, UId=UId)

#Written by: Victor and Niklas
def GetBank(UserId):
    """"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    sql = "SELECT account_balance from BANK_ACCOUNT where user_id = %s;"
    cur.execute(sql, (UserId,))
    Points = cur.fetchall()
    return Points

# Written by: Niklas & Victor
@route("/create-issue/<UId>")
def create_issue(UId):
    """Displays the create issue page"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    Sql = """SELECT home_id from LIVES_IN where user_id = %s"""
    cur.execute(Sql, (UId,))
    HomeId = cur.fetchone()
    Sql2 = """SELECT user_name, PERSON.user_id from PERSON join LIVES_IN on PERSON.user_id = LIVES_IN.user_id where home_id = %s"""
    cur.execute(Sql2, (HomeId,))
    HomesUsers = cur.fetchall()
    return template("create-issue", Users=HomesUsers, UId=UId)


# Written by: Victor
def GetChores(UserId):
    """Function that returns all CHORES from a specific PERSON"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    sql = "SELECT * from CHORE join RESPONSIBILITY on CHORE.chore_id = RESPONSIBILITY.chore_id where user_id = %s;"
    cur.execute(sql, (UserId,))
    GetAllChores = cur.fetchall()
    return GetAllChores


# Written by: Victor
def get_specific_issue(issue_id):
    """Function that returns all info about the CHORES/Issues"""
    conn = psycopg2.connect(user=userN, host=hostN, password=passwordN, database=databaseN)
    cur = conn.cursor()
    sql = "SELECT * FROM CHORE where chore_id = %s;"
    cur.execute(sql, (issue_id,))
    get_issue_description = cur.fetchall()
    return get_issue_description


'''
# Written by: Victor
def find_issue(issue_id):
    "hämtar alla artiklar, om artikel = id då har man hittat rätt artikel"
    issues = get_issue()
    found_issue = None
    for i in range(len(issues)):
      id, name, category, value, description, date = issues[i]
      if id == issue_id:
        found_issue = id
    return found_issue

# Written by: Victor
@route("/Chore/<ChoreId>")
def Chore(ChoreId):
    """Function that checks if an issue contains info and redirects to different routes."""
    FoudChore = GetChore(ChoreId)
    for Info in found_issue:
      if Info == None:
          return template("admin-page")
      else:
          return template("edit-issue", { "Info": Info })
'''

@error(404)
def error404(error):
    """Returns the error template"""
    return template("error")


@error(405)
def error405(error):
    """Returns the error template"""
    return template("error")


@route("/static/css/<filename:path>")
def static_css(filename):
    """Returns the static files, style and js files."""
    return static_file(filename, root="static/css")


@route("/static/<filename:path>")
def static_js(filename):
    """Returns the static files, style and js files."""
    return static_file(filename, root="static")


@route("/static/images/<filename:path>")
def static_images(filename):
    """Returns the static files, style and js files."""
    return static_file(filename, root="static/images")

run(host='localhost', port=8090, debug=True)

