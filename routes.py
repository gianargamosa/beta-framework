import restor
from controllers.HomeController import HomeController
from controllers.UsersController import UsersController

routes = [
  (restor.routes('/'), HomeController),
  (restor.routes('/users'), UsersController),
]