from curses import flash
from flask import Flask, request, jsonify, Response
from flask_mongoengine import MongoEngine
import json
from multiprocessing import Value
# from mongoengine import connect

counter = Value('i',0)
app = Flask(__name__)

# db =connect(host='mongodb://localhost:27017/mydb')
app.config['MONGODB_SETTINGS'] = {'db': 'epiko','host': 'localhost','port': 27017}

db = MongoEngine()
db.init_app(app)

class Blog(db.Document):
    bid = db.IntField(unique=True)
    header=db.StringField(max_length=20,required=True)
    image = db.StringField(required=True)
    description =db.StringField(max_length=50,required=True)
    article=db.StringField(max_length=1000,required=True)
    like = db.IntField()
    
    def to_json(self):
        return {"bid":self.bid,
                "header": self.header,
                "image":self.image,
                "description": self.description,
                "article":self.article
                }

class Login(db.Document):
    email=db.EmailField(max_length=30,required=True)
    password=db.StringField(max_length=30,required=True)

    def to_json(self):
        return {"email":self.email,
                "password":self.password}

class Like(db.Document):
    lid=db.IntField()
    like=db.IntField()

    def to_json(self):
        return {"lid":self.lid,"like":self.like}

class Addhoc(db.Document):
    comment = db.StringField(max_length=1000)

    def to_json(self):
        return {"comment":self.comment}

@app.route('/like/<bid>',methods=['POST'])
def Likes(bid):
    record =Blog.objects.get(bid=bid)    
    with counter.get_lock():
        counter.value += 1
        out = counter.value
        user=Like(like=record["like"])
        user.save()
    return jsonify("Like added once")

# @app.route('/unlike/<bid>',methods=['POST'])
# def UnLike(bid):
#     record =Blog.objects.get(bid=bid)    
#     with counter.get_lock():
#         counter.value -= 1
#         out = counter.value
#         user=Like(like=record["like"])
#         user.save()
#     return jsonify("Like added once")

# @app.route('/unlike/<lid>', methods=['DELETE'])
# def UnLike(lid):
#     Like.objects.get(lid=lid).delete()
#     return jsonify("Data deleted")

@app.route('/like',methods=['GET'])
def LikeView():  
    queryset=Like.objects.all()
    a = queryset.count()
    # Addhoc.objects.count(out)
    return jsonify(count=a)

# @app.route('/dislike/<bid>',methods=['[POST'])
# def dislike(bid):
#     Blog.objects.get(bid=bid)    
#     with counter.get_lock():
#         counter.value -= 1
#         out = counter.value
#     return jsonify(count=out)

@app.route("/comment/<bid>",methods=["POST"])
def commentview(bid):
    Blog.objects.get(bid=bid)                 #.update(**record)
    record=json.loads(request.data)
    user=Addhoc(comment=record["comment"]) #id=record["id"],
    user.save()
    return jsonify(user.to_json())

@app.route('/addrecord', methods=['POST'])
def Create_record():
    record = json.loads(request.data)
    user = Blog(bid=record['bid'],header=record['header'],image=record["image"] ,description=record['description'],article=record["article"])
    user.save()
    return jsonify(user.to_json())

@app.route('/getdata')
def GetView():
    user = Blog.objects.all()
    # return Response(user,mimetype="application/json", status=200)
    return Response(user.to_json(),mimetype="application/json", status=200)

@app.route('/login',methods=['POST'])
def LoginView():
    record = json.loads(request.data)
    user = Login(email=record['email'],password=record['password'])
    user.save()
    # if user:
    #     return jsonify(user.to_json())
    # else:
    #     return jsonify({"error":"Email id not found"})
    return jsonify(user.to_json())

@app.route('/update/<int:bid>',methods=['PUT'])
def UpdateView(bid):
    user = request.get_json()
    Blog.objects.get(bid=bid).update(**user)
    return jsonify("Data updated")

@app.route('/delete/<int:bid>', methods=['DELETE'])
def DeleteView(bid):
    Blog.objects.get(bid=bid).delete()
    return jsonify("Data deleted")

if __name__=="__main__":
    app.run(debug=True)
