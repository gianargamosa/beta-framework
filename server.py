import restor
import tornado.web
from tornado.options import define, options
import sys
from peewee import *
from forms import *
from forms import requirements
import yaml
import os
import pickle

with open("database.yml", 'r') as ymlfile:
  cfg = yaml.load(ymlfile)
  
database = MySQLDatabase(cfg['MYSQL']['DB_DATABASE'], host=cfg['MYSQL']['DB_HOST'], port=cfg['MYSQL']['DB_PORT'], user=cfg['MYSQL']['DB_USERNAME'], passwd=cfg['MYSQL']['DB_PASSWORD'])

class AbstractModel(Model):
  class Meta:
    database = database

class Users(AbstractModel):
  id = PrimaryKeyField()
  username = CharField(unique=True)
  email = CharField()
  avatar = CharField()
  password = CharField()

user_form = Validator(**{
    'username': TextField(required=True, messages={'required': 'Please enter username'}),
    'email': EmailField(required=True, min_length=8, messages={'min_length': 'email must be 8 char long', 'required': 'Please enter email'}),
    'password': TextField(required=True, min_length=8, messages={'min_length': 'password must be 8 char long', 'required': 'Please enter password'}),
})

class HomeController(restor.ApplicationController):
    def new(self):
        self.render("new.html")

    def index(self):
        self.render("templates/example/index.html", user="arman gian")

    def create(self):
        self.write("CREATE")

    def show(self, id):
        user = Users.get()
        # print pickle.dumps(user)
        # self.write()

    def update(self, id):
        self.write("UPDATE " + id)

    def edit(self, id):
        self.write(id)

    def destroy(self, id):
        self.write(id)

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
    login_url="/sign_in",
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
    tornado.ioloop.IOLoop.instance().start()