import restor
import tornado.web
from tornado.options import define, options
import sys
from peewee import *
from forms import *
from forms import requirements
import yaml
import os
import bcrypt
import pry

with open("database.yml", 'r') as ymlfile:
  config = yaml.load(ymlfile)
  
database = MySQLDatabase(config['mysql']['database'], host=config['mysql']['host'], port=config['mysql']['port'], user=config['mysql']['username'], passwd=config['mysql']['password'])

class ApplicationModel(Model):
  class Meta:
    database = database

class Users(ApplicationModel):
  id = PrimaryKeyField(unique=True)
  username = CharField()
  email = CharField()
  avatar = CharField()
  password = CharField()

user_form = Validates(**{
    'username': TextField(required=True, messages={'required': 'Please enter username'}),
    'email': EmailField(required=True, min_length=8, messages={'min_length': 'email must be 8 char long', 'required': 'Please enter email'}),
    'password': TextField(required=True, min_length=8, messages={'min_length': 'password must be 8 char long', 'required': 'Please enter password'}),
})

login_form = Validates(**{
    'email': EmailField(required=True, messages={'required': 'Please enter email'}),
    'password': TextField(required=True, messages={'required': 'Please enter password'}),
})

class HomeController(restor.ApplicationController):
    def new(self):
        self.render("home/new.html", errors=None)

    @tornado.web.authenticated
    def index(self):
        self.render("home/index.html")

    def check_permission(self, email, password):
        user = Users.select().where(Users.email == self.form.data['email']).first()
        if email == user.email and password == user.password:
            return True
        return False

    def get_current_user(self):
        user_auth = self.get_secure_cookie("user")
        if not user_auth: return None
        return Users.select().where(Users.email == user_auth).first()

    @request(login_form)
    def create(self):
        if self.form.is_valid:
            user = Users.select().where(Users.email == self.form.data['email']).first()
            password = bcrypt.hashpw(tornado.escape.utf8(self.form.data["password"]), bcrypt.gensalt())
            auth = self.check_permission(self.form.data["email"], self.form.data["password"])
            if auth:
                self.set_secure_cookie("user", str(self.form.data["email"]))
                self.redirect("/home")
            else:
                self.render("home/new.html", errors=None)
        else:
            self.render("home/new.html", errors=self.form.errors.iteritems())

    @tornado.web.authenticated
    def show(self, id):
        self.write(self.current_user)
        # user = Users.get()
        # self.render("home/show.html")

    @request(login_form)
    def update(self, id):
        if self.form.is_valid:
            pass
        else:
            pass

    def edit(self, id):
        self.render("home/edit.html")

    def destroy(self, id):
        self.clear_cookie("user")
        self.redirect("/home")

class UsersController(restor.ApplicationController):
    def new(self):
        self.render("user/new.html", errors=None)

    def index(self):
        users = Users.select()
        self.render("user/index.html", users=users)

    @request(user_form)
    def create(self):
        if self.form.is_valid:
            data_source = [self.form.data]
            for data_dict in data_source:
                Users.create(**data_dict)
            self.redirect("/users")
        else:
            self.render("user/new.html", errors=self.form.errors.iteritems())

    def show(self, id):
        user = Users.select().where(Users.id == id).first()
        self.render("user/show.html", user=user)

    @request(user_form)
    def update(self, id):
        if self.form.is_valid:
            for user in Users.select().where(Users.id == id):
                user.username = self.form.data['username']
                user.email = self.form.data['email']
                user.password = self.form.data['password']
                user.save()
            self.redirect("/users")
        else:
            user = Users.select().where(Users.id == id).first()
            self.render("user/edit.html", user=user, errors=self.form.errors.iteritems())

    def edit(self, id):
        user = Users.select().where(Users.id == id).first()
        self.render("user/edit.html", user=user, errors=None)

    def destroy(self, id):
        user = Users.get(Users.id == id)
        user.delete_instance()
        self.redirect("/users")

settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), 'templates'),
    static_path=os.path.join(os.path.dirname(__file__), 'assets'),
    cookie_secret='base64:Fgujl/rycGx7k9yubIANKCfM9hZWLgrxy52xXnD5pjc=',
    xsrf_cookies=True,
    login_url="/home/new",
    debug=True,
)

def make_app():
    return tornado.web.Application([
        (restor.routes('/home'), HomeController),
        (restor.routes('/users'), UsersController),
    ], **settings)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.options.parse_command_line()
    print 'Starting Gradle on <http://localhost:%s>' % 8888
    tornado.ioloop.IOLoop.instance().start()
