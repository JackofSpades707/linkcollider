#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup
import time
import argparse
from getpass import getpass

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="Display debug information", action="store_true")
parser.add_argument('-e', '--email', help="email to use for login", type=str, default=input("Email: "))
parser.add_argument('-p', '--password', help="password to use for login", type=str, default=getpass())
args = parser.parse_args()

class Bot:
    def __init__(self):
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'}
        self._session = requests.Session()
        self._points = 0
        self._running = True

    def login(self, email, password):
        payload = {'email': email, 'pw': password, "remember": "on", 'reqlogin': ''}
        self._session.get("https://www.linkcollider.com/page/login", headers=self._headers)
        self._session.post("https://www.linkcollider.com/action/login", payload, headers=self._headers) # logged in

    def autosurf(self):
        for i in range(0, 20):
            points = self._points
            source = self._session.get("http://www.linkcollider.com/page/activity/autosurf", headers=self._headers)
            url = self.data_identifier(i, source, 'url')
            payload = self.data_identifier(i, source, 'post')
            if url is None or payload is None:
                return
            self._points = self.check_points(source)
            if args.verbose:
                print("url : {}\npoints: {}".format(url, self._points))
            else:
                print("points: {}".format(self._points))
            self._session.get(url, headers=self._headers)
            time.sleep(30)
            p = self._session.post("http://www.linkcollider.com/action/activity/autosurf", payload, headers=self._headers)
            self._points = self.check_points(source)
            if args.verbose:
                print("post data code - {}".format(p.status_code))
            if self._points == points:
                print("Not earning anymore points")
                self._running = False
                return

    def check_points(self, source):
        return BeautifulSoup(source.content, "html.parser").find(class_="color-red rtoken").get_text()

    def data_identifier(self, i, source, selector): # i valid values are 0-19
        try:
            key = re.findall(r"var key = .+;", source.text)[0].rstrip(';').strip('var key = ').strip("'")
            uid = re.findall(r"var uid = .+;", source.text)[0].rstrip(';').strip('var uid = ').strip("'")
            posts = re.findall(r"var posts = new Array.+;", source.text)[0].rstrip(';').strip('var posts = new Array').strip('(').strip(')').split(',')[i]
            posts_reward = re.findall(r"var postsreward = new Array.+;", source.text)[0].rstrip(';').strip('var postsreward = new Array').strip('(').strip(')').split(',')[i]
            posts_noref = re.findall(r"var postsnoreferrer = new Array.+;", source.text)[0].rstrip(';').strip('var postsnoreferrer = new Array').strip('(').strip(')').split(',')[i]
            postsss = re.findall(r"var postsss = new Array.+;", source.text)[0].rstrip(';').strip('var postsss = new Array').strip('(').strip(')').replace('"', '').split(',')[i]
        except IndexError:
            return None
        if args.verbose and selector == 'url':
            print(f"key: {key}")
            print(f"uid: {uid}")
            print(f"posts: {posts}")
            print(f"posts_reward: {posts_reward}")
            print(f"posts_noref: {posts_noref}")
            print(f"postsss: {postsss}")
        if selector == 'url':
            built_url = "http://www.linkcollider.com/page/singlesurf/{0}/autosurf/{1}/{2}/{3}/?uid={4}&ss={5}".format(posts, key, posts_reward, posts_noref, uid, postsss)
            return built_url
        elif selector == 'post':
            payload = {'lc_key': key, 'pid': posts, 'ss': postsss, 'uid': uid}
            return payload
        else:
            print("unsupported use of method : data_identifier...\nterminating...")
            raise SystemExit

    def run(self):
        self.login(args.email, args.password)
        time.sleep(5)
        while self._running is True:
            self.autosurf()


if __name__ == "__main__":
    bot = Bot()
    bot.run()
