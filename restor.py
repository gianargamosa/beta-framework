import tornado.ioloop
import tornado.web
import traceback
import tornado.httputil
import tornado.escape
from tornado.options import define, options
import sys

def routes(prefix, id_regex='[0-9a-f]+'):
    _id = "(?P<_id>%s)" % id_regex
    _arg1 = "(?:/(?P<_arg1>edit|delete|destroy))?"
    _arg2 = "(?P<_arg2>new)"
    route = "(?:/(?:(?:%s%s)|%s))?" % (_id, _arg1, _arg2)
    return r'' + prefix + route


class ApplicationController(tornado.web.RequestHandler):
    def get(self, _id=None, _arg1=None, _arg2=None, **kwargs):
        if not _id and not _arg2 and not _arg1:
            self.index(**kwargs)
        elif _id and not _arg2 and not _arg1:
            self.show(_id, **kwargs)
        elif not _id and not _arg1 and _arg2 == 'new':
            self.new(**kwargs)
        elif _id and not _arg2 and _arg1 == 'edit':
            self.edit(_id, **kwargs)
        elif _id and not _arg2 and _arg1 == 'destroy':
            self.destroy(_id, **kwargs)
        elif _id and not _arg2 and _arg1 == 'create':
            self.create(_id, **kwargs)
        else:
            raise tornado.web.HTTPError(404)

    def post(self, _id=None, _arg1=None, _arg2=None, **kwargs):
        if not _id and not _arg1 and not _arg2:
            self.create(**kwargs)
        elif _id and not _arg1 and not _arg2:
            self.update(_id, **kwargs)
        elif _id and not _arg2 and _arg1 == 'delete':
            self.destroy(_id, **kwargs)
        else:
            raise tornado.web.HTTPError(404)

    def put(self, _id=None, _arg1=None, _arg2=None, **kwargs):
        if _id and not _arg1 and not _arg2:
            self.update(_id, **kwargs)
        else:
            raise tornado.web.HTTPError(404)

    def delete(self, _id=None, _arg1=None, _arg2=None, **kwargs):
        if _id and not _arg1 and not _arg2:
            self.destroy(_id, **kwargs)
        else:
            raise tornado.web.HTTPError(404)

    def index(self, **kwargs):
        self.write({"hola": ["hola", 1, {"option": True}, True]})
        # self.write("Hola Mundo", iter=True)
        # raise tornado.web.HTTPError(405)

    def new(self, **kwargs):
        raise tornado.web.HTTPError(405)

    def create(self, **kwargs):
        raise tornado.web.HTTPError(405)

    def show(self, _id, **kwargs):
        raise tornado.web.HTTPError(405)

    def edit(self, _id, **kwargs):
        raise tornado.web.HTTPError(405)

    def update(self, _id, **kwargs):
        raise tornado.web.HTTPError(405)

    def destroy(self, _id, **kwargs):
        raise tornado.web.HTTPError(405)


    def write_error(self, status_code, **kwargs):
        if "application/json" in self.request.headers.get("Accept", ""):
            self.set_header('Content-Type', 'application/json')
            response = {
                'error': True,
                'response': None,
                'code': status_code,
                'status': self._reason,
            }
            if self.settings.get("serve_traceback") and "exc_info" in kwargs:
                exc_info = traceback.format_exception(*kwargs["exc_info"])
                response['debug'] = exc_info
            self.finish(response)
        else:
            super(ApplicationController, self).write_error(status_code, **kwargs)


    def write(self, chunk):
        status_code = self.get_status()
        if status_code == 200 and \
                "application/json" in self.request.headers.get("Accept", ""):
            self.set_header('Content-Type', 'application/json')
            status_code = self.get_status()
            response = {
                'error': (status_code != 200 or None),
                'code': status_code,
                'status': tornado.httputil.responses[status_code],
            }
            if isinstance(chunk, (list,tuple)) and not isinstance(chunk, basestring):
                super(ApplicationController, self).write(tornado.escape.json_encode(response)[:-1]+',"reponse": [')
                for i in range(len(chunk)): 
                    if i > 0:
                        super(ApplicationController, self).write(", " + tornado.escape.json_encode(chunk[i]))
                    else:
                        super(ApplicationController, self).write(tornado.escape.json_encode(chunk[i]))
                super(ApplicationController, self).write("]}")
            else:
                response["response"] = chunk
                super(ApplicationController, self).write(response)
        else:
            super(ApplicationController, self).write(chunk)


# application = tornado.web.Application([
#     (action_routes('/animal'), ResourceHandler)
# ], debug=True)


# if __name__ == "__main__":
#     application.listen(8888)
#     tornado.options.parse_command_line()
#     tornado.ioloop.IOLoop.instance().start()