#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup
import time
import argparse
import threading

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--threads', type=int, default=100, help='max number of threads to run, 1 account runs for each thread')
args = parser.parse_args()

class Bot:
    def __init__(self, email, password, proxy=None):
        self._email = email
        self._password = password
        self._proxy = self.setup_proxy(proxy)
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'}
        self._session = requests.Session()
        self._points = 0
        self._running = True

    def setup_proxy(self, proxy):
        if proxy is None:
            return None
        return {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

    def output(self, s):
        print("{}: {}").format(self._email, s)

    def login(self):
        payload = {'email': self._email, 'pw': self._password, "remember": "on", 'reqlogin': ''}
        self._session.get("https://www.linkcollider.com/page/login", headers=self._headers, proxies=self._proxy)
        self._session.post("https://www.linkcollider.com/action/login", payload, headers=self._headers, proxies=self._proxy)
        self.output('Logged In')

    def autosurf(self):
        for i in range(0, 20):
            points = self._points
            source = self._session.get("http://www.linkcollider.com/page/activity/autosurf", headers=self._headers, proxies=self._proxy)
            url = self.data_identifier(i, source, 'url')
            payload = self.data_identifier(i, source, 'post')
            if url is None or payload is None:
                return
            self._points = self.check_points(source)
            if args.verbose:
                self.output("url : {}\npoints: {}".format(url, self._points))
            else:
                self.output("points: {}".format(self._points))
            self._session.get(url, headers=self._headers, proxies=self._proxy)
            time.sleep(30)
            p = self._session.post("http://www.linkcollider.com/action/activity/autosurf", payload, headers=self._headers, proxies=self._proxy)
            self._points = self.check_points(source)
            if args.verbose:
                self.output("[Post Response Code] -> {}".format(p.status_code))
            if self._points == points:
                self.output("Not earning anymore points")
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
            self.output("key: {}").format(key)
            self.output("uid: {}").format(uid)
            self.output("posts: {}").format(posts)
            self.output("posts_reward: {}").format(posts_reward)
            self.output("posts_noref: {}").format(posts_noref)
            self.output("postsss: {}").format(postsss)
        if selector == 'url':
            built_url = "http://www.linkcollider.com/page/singlesurf/{0}/autosurf/{1}/{2}/{3}/?uid={4}&ss={5}".format(posts, key, posts_reward, posts_noref, uid, postsss)
            return built_url
        elif selector == 'post':
            payload = {'lc_key': key, 'pid': posts, 'ss': postsss, 'uid': uid}
            return payload

    def run(self):
        self.login()
        time.sleep(5)
        while self._running is True:
            self.autosurf()

def make_threads(accounts, proxies):
    q = []
    for n, account in enumerate(accounts):
        account = "{}|{}".format(account, proxies[n])
        q.append(account)
    threads = []
    for i in range(args.threads):
        account = q[i].split('|')
        email = account[0]
        password = account[1]
        proxy = account[2]
        bot = Bot(email, password, proxy)
        t = threading.Thread(target=bot.run)
        threads.append(t)
    return threads

def run_thread(threads):
    t = threads[0]
    del(threads[0])
    t.run()

def Main():
    with open('accounts.txt') as f:
        accounts = f.readlines()
    with open('proxies.txt') as f:
        proxies = f.readlines()
    threads = make_threads(accounts, proxies)
    while len(threads) >= 1:
        if threading.active_count() < args.threads:
            run_thread(threads)
        time.sleep(0.5)


if __name__ == "__main__":
    Main()

