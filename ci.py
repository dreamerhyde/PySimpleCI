#!/usr/bin/env python3
"""
Package:    PySimpleCI
Author:     Albert Liu (https://github.com/dreamerhyde)
Date:       2017-12-02
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import yaml
import logging
import os


class S(BaseHTTPRequestHandler):
    def config(self=None):
        with open("config.yaml", 'r') as stream:
            try:
                config = yaml.load(stream)
                return config
            except yaml.YAMLError as exc:
                print(exc)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        if self.path.endswith('favicon.ico'):
            return
        repos = self.config().get('repos', False)
        port = self.config().get('port', 3000)
        url = self.config().get('url', False)
        arg = self.path.split('/')
        arg.pop(0)
        # Pull
        if len(arg) > 1 and repos and repos[arg[0]]['remote'] == arg[1] and repos[arg[0]]['branch'] == arg[2]:
            self.wfile.write(
                "PySimpleCI accepted to execute the command:$ <b>sudo git pull {} {}</b>.<br/>".format(arg[1],
                                                                                                       arg[2]).encode(
                    "utf-8"))
            logging.info("IP:{}  {}".format(self.client_address, self.path))
            cmd = "cd {} && git pull {} {}".format(repos[arg[0]]['path'], repos[arg[0]]['remote'], repos[arg[0]]['branch'])
            if os.system(cmd) == 0:
                logging.info("Success execute command: {}".format(cmd))
            else:
                logging.ERROR("Error with execute command: {}".format(cmd))

        # Listed End Points
        elif len(arg) <= 1:
            for repo, data in repos.items():
                endPoint = "http://{}:{}/{}/{}/{}".format(url, port, repo, data['remote'], data['branch'])
                self.wfile.write("End Point: <b>{0}</b></br/>".format(endPoint).encode("utf-8"))
        # Error End Point
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(
                "<br/>PySimpleCI error accessed denied for the path: <b>{}</b>.<br/>".format(self.path).encode("utf-8"))
            self.wfile.write(
                "Please check your <b>config.yaml</b> file parameter '<b>repos</b>' first.".format(self.path).encode(
                    "utf-8"))

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()

    def do_HEAD(self):
        self._set_headers()


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        handlers=[logging.FileHandler('PySimpleCI.log', 'w', 'utf-8'), ])
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd with port {}...'.format(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == "__main__":
    with open("config.yaml", 'r') as stream:
        try:
            config = S.config()
            port = config.get('port', False)
            if (port):
                run(port=port)
            else:
                run()
        except yaml.YAMLError as exc:
            print(exc)
