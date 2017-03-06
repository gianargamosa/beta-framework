import tornado.web
from tornado.options import define, options
import restor

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