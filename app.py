from flask import Flask
from flask import request,jsonify
import json
from secrets import token_hex,randbelow
import datetime
import pytz
import shelve
import threading
import re


key="admin"
app=Flask(__name__)
glock=threading.Lock()
db=shelve.open("data.db")
if db.get("post_id") is None:
    db["post_id"]=0
    db['posts']=[]
if db.get("user_id") is None:
    db["user_id"]=0
    db['users']=[]
class Post:
    def __init__(self,msg,user_id=None):
        self.id=self.get_id()
        self.msg=msg
        self.key=self.get_key()
        self.timestamp=self.get_timestamp()
        self.user_id=user_id

    def __repr__(self):
        return f"<Post id:{self.id} msg:{self.msg} key:{self.key} time:{self.timestamp} user:{self.user_id}>"
    def get_key(self):
        return token_hex(32)
    def get_timestamp(self):
        return datetime.datetime.now(tz=pytz.utc)
    def get_id(self):
        with glock:
            db['post_id']+=1
            return db['post_id']


class User:
    def __init__(self,username,role=0):
        self.username=username
        self.id=self.get_id()
        self.role = role  # 0 user 1 admin
        self.key=self.get_key()
        self.timestamp=self.get_timestamp()

    def get_key(self):
        if self.role:
            return token_hex(40)
        else:
            return token_hex(38)
    def get_timestamp(self):
        return datetime.datetime.now(tz=pytz.utc)
    def get_id(self):
        with glock:
            db['user_id']+=1
            return db['user_id']

@app.route("/random/<int:sides>")
def roll(sides):
    if sides<=0:
        return jsonify({"err":"'need a positive number of sides"}),400
    return jsonify({"num",randbelow(sides)+1})
@app.route("/post",methods=["POST"])
def create():
    data=json.loads(request.data)
    post=None
    if data.get("user_id", None) is None:
        post=Post(data['msg'],None)
    else:
        if data.get("user_key",None) is None:
            return jsonify({"err": "bad request"}), 400
        for user in db['users']:
            if user.key==data["user_key"] and user.id==data['user_id']:
                post=Post(data['msg'],user.id)
                break
        if post is None:
            return jsonify({"err":"forbid"}),403
    with glock:
        db['posts']+=[post]
    return jsonify({
        "id":post.id,
        "key":post.key,
        "timestamp":post.timestamp,
        "user_id":post.user_id
    })
@app.route("/user",methods=["POST"])
def create_user():
    data=json.loads(request.data)
    role=0
    if not data.get("key",None) is None:
        if data['key']==key:
            role=1
    if data.get("username",None) is None:
        return jsonify({"err":"bad request"}),400
    user=User(data['username'],role)
    with glock:
        db['users']+=[user]
    return jsonify({
        "id":user.id,
        "key":user.key,
        "timestamp":user.timestamp,
        "username":user.username
    })

@app.route("/post/<int:id>")
def read_post(id:int):
    with glock:
        for post in db['posts']:
            if post.id==id:
                return jsonify({
                    "id":post.id,
                    "timestamp":post.timestamp,
                    "msg":post.msg,
                    "user_id":post.user_id
                })
    return jsonify({"err":"not found the post."}),404
@app.route("/post/<int:id>/<key>",methods=['DELETE'])
def delete(id:int,key:str):
    with glock:
        if len(key)==64:
            for index,post in enumerate(db['posts']):
                if post.id == id:
                    if post.key==key:
                        p=db['posts']
                        p.pop(index)
                        db['posts']=p
                        return jsonify({
                            "id": post.id,
                            "timestamp": post.timestamp,
                            "key": post.key,
                            "user_id": post.user_id
                        })
                    else:
                        return jsonify({"err":"forbid"}),403
        elif len(key)==76:
            for index, user in enumerate(db['users']):
                if user.key == key:
                    for index_1, post in enumerate(db['posts']):
                        if post.id == id:
                            if post.user_id==user.id:
                                p = db['posts']
                                p.pop(index_1)
                                db['posts'] = p
                                return jsonify({
                                    "id": post.id,
                                    "timestamp": post.timestamp,
                                    "key": post.key,
                                    "user_id": post.user_id
                                })
            return jsonify({"err": "forbid"}), 403
        elif len(key)==80:
            for index, user in enumerate(db['users']):
                if user.key == key:
                    for index_1, post in enumerate(db['posts']):
                        if post.id == id:
                            p = db['posts']
                            p.pop(index_1)
                            db['posts'] = p
                            return jsonify({
                                "id": post.id,
                                "timestamp": post.timestamp,
                                "key": post.key,
                                "user_id": post.user_id
                            })
            return jsonify({"err": "forbid"}), 403
        else:
            return jsonify({"err": "forbid"}), 403
    return jsonify({"err":"not found the post."}), 404
@app.route("/search/<int:id>")
def search(id:int):
    posts=[]
    with glock:
        for post in db['posts']:
            if post.user_id==id:
                posts.append(
                    {
                        "id":post.id,
                        "msg":post.msg,
                        "timestamp":post.timestamp
                    }
                )
    return jsonify({
        "posts":posts
    })
@app.route("/search_msg/<msg>")
def search_msg(msg):
    posts=[]
    with glock:
        for post in db['posts']:
            if re.match(msg,post.msg):
                posts.append(
                    {
                        "id":post.id,
                        "msg":post.msg,
                        "timestamp":post.timestamp
                    }
                )
    return jsonify({
        "posts":posts
    })
@app.route("/search_ts/<int:st>/<int:et>")
def search_time(st,et):
    posts = []
    with glock:
        for post in db['posts']:
            if st<post.timestamp.timestamp()<et:
                posts.append(
                    {
                        "id": post.id,
                        "msg": post.msg,
                        "timestamp": post.timestamp
                    }
                )
    return jsonify({
        "posts": posts
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)