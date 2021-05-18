from flask import Flask, render_template, url_for, request
import requests
import json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask("__main__")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)

#------------------------STEPS---------
#inside python shell
#from flaskapi import db
#db.create_all()

class Users(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    role = db.Column(db.String(15))

    def __repr__(self):
        return 'Created user %d' % self.id

class Spelling(db.Model):
    id = db.Column(db.Integer)
    word = db.Column(db.String(50), primary_key=True)
    count = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return 'Created %s' % self.word

class Grammar(db.Model):
    id = db.Column(db.Integer)
    word = db.Column(db.String(50), primary_key=True)
    count = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return 'Created %s' % self.word





@app.route("/api/v1/check/<text>", methods=["GET"])
def getMistakes(text):
    if request.method == "GET":
        input_text = text
        url = "https://api.languagetool.org/v2/check?language=el-GR&text=%s" % input_text
        #url = "http://localhost:8081/v2/check?language=el-GR&text=%s" % input_text
        response = requests.get(url)
        json_obj = json.loads(response.text)
        return json_obj
    else:
        return ""


@app.route("/user/<role>/<id>", methods=["GET","POST"])
def users(role,id):
    if request.method == "POST":
        exists = db.session.query(Users.id).filter_by(id=id).first()
        if(not exists):
            new_user = Users(id=id, role=role)
            try:
                db.session.add(new_user)
                db.session.commit()
            except:
                return "Could not add user"
        else:
            return "User already exists"


@app.route("/mistakes/delete_by_id/<id>",methods=["POST"])
def deleteById(id):
    if request.method == "POST":
        db.session.query(Spelling).filter_by(id=id).delete()
        try:
            db.session.commit()
        except:
            return "Could not delete records"    

@app.route("/mistakes/<id>/<type_of_mistake>/<word>", methods=["POST"])
def addData(id,word,type_of_mistake):
    if request.method == "POST":
        word_to_add = word
        if type_of_mistake == 'spelling':
            exists = db.session.query(Spelling.word).filter_by(word=word_to_add).first()
            if(exists):
                task = Spelling.query.get_or_404(word_to_add)
                task.count = task.count + 1
                try:
                    db.session.commit()
                except:
                    return "Could not update word count!"    
            else:        
                new_mistake = Spelling(id= id,word = word_to_add)
                try:
                    db.session.add(new_mistake)
                    db.session.commit()
                except:
                    return "ERROR" 
            return "SUCCESS!!!!!"
        elif type_of_mistake == 'grammar':
            exists = db.session.query(Grammar.word).filter_by(word=word_to_add).first()
            if(exists):
                task = Grammar.query.get_or_404(word_to_add)
                task.count = task.count + 1
                try:
                    db.session.commit()
                except:
                    return "Could not update word count!"    
            else:        
                new_mistake = Grammar(id=id,word = word_to_add)
                try:
                    db.session.add(new_mistake)
                    db.session.commit()
                except:
                    return "ERROR" 
            return "SUCCESS!!!!!"



@app.route("/mistakes/<type_of_mistake>", methods=["GET"])
def getData(type_of_mistake):
    if request.method == "GET":
        if type_of_mistake == 'spelling':
            try:
                data = Spelling.query.order_by(Spelling.date_created).all()
                lista = []
                for x in data:
                    temp_data = {
                        'word' : x.word,
                        'count' : x.count
                    }
                    lista.append(temp_data)
                lista = json.dumps(lista)    
                return lista
            except:
                return ""    
        elif type_of_mistake == 'grammar':
            try:
                data = Grammar.query.order_by(Grammar.date_created).all()
                lista = []
                for x in data:
                    temp_data = {
                        'word' : x.word,
                        'count' : x.count
                    }
                    lista.append(temp_data)
                lista = json.dumps(lista)    
                return lista
            except:
                return ""     

if __name__ == "__main__":
    app.run(debug=True)
