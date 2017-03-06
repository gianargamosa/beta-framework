import tornado.web
from tornado.options import define, options
import restor

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