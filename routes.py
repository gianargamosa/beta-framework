import restor
from server import *

routes = [
  (restor.routes('/'), HomeController),
  (restor.routes('/users'), UsersController),
]