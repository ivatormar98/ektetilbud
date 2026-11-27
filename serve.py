"""Local preview with the same clean URLs as GitHub Pages (/om -> om.html): python serve.py [port]"""
import functools, http.server, os, sys

class Handler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) and os.path.exists(path + ".html"):
            self.path = self.path.split("?")[0].split("#")[0] + ".html"
        return super().send_head()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8772
http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida"))).serve_forever()
