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
    essay_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return 'Created user %d' % self.id

class UserInfo(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    role = db.Column(db.String(15))
    age = db.Column(db.Integer, default=0)
    education = db.Column(db.String(50))
    mother_tongue = db.Column(db.String(50))
    
    def __repr__(self):
        return 'Created user info %d' % self.id

class Essays(db.Model):
    id = db.Column(db.Integer, primary_key=True , autoincrement=True)
    user_id = db.Column(db.String(30))
    role = db.Column(db.String(15))
    num_words = db.Column(db.Integer)
    num_spelling = db.Column(db.Integer)
    num_grammar = db.Column(db.Integer)
    num_punctuation = db.Column(db.Integer)
    grade = db.Column(db.String(10))
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return 'Created essay %d' % self.id

class Spelling(db.Model):
    id = db.Column(db.Integer)
    word = db.Column(db.String(50), primary_key=True)
    count = db.Column(db.Integer, default=1)
    role = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return 'Created %s' % self.word

class Grammar(db.Model):
    id = db.Column(db.Integer)
    word = db.Column(db.String(50), primary_key=True)
    count = db.Column(db.Integer, default=1)
    role = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return 'Created %s' % self.word

class Syntax(db.Model):
    id = db.Column(db.Integer)
    word = db.Column(db.String(50), primary_key=True)
    count = db.Column(db.Integer, default=1)
    role = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return 'Created %s' % self.word

#kossy word count
class Wordcount(db.Model):
    id = db.Column((db.Integer), primary_key=True)
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


@app.route("/user/user_info",methods=["POST"])
def userInfo():
    if request.method == "POST":
        id = request.form.get("id")
        role = request.form.get("role")
        age = request.form.get('age')
        education = request.form.get('level')
        mother_tongue = request.form.get('MT')

        new_info = UserInfo(id=id, role=role, age=age, education= education, mother_tongue = mother_tongue)
        try:
            db.session.add(new_info)
            db.session.commit()
        except:
            return "Could not update info"   
    return ""         

            

@app.route("/essays/all", methods=["GET"])
def getEssays():
    if request.method == "GET":
        try:
            temp_list = []
            essay_data = Essays.query.order_by(Essays.date_created).all()

            for essay in essay_data:
                essay_obj = {
                    "essay" : essay.id,
                    "num_words" : essay.num_words,
                    "num_spelling" : essay.num_spelling,
                    "num_grammar" : essay.num_grammar,
                    "num_punctuation" : essay.num_punctuation,
                    "grade" : essay.grade,
                }
                temp_list.append(essay_obj)
            temp_list = json.dumps(temp_list)
            return temp_list    
        except:
            return "Error could not return essays"    

@app.route("/essays/add/role/<role>/id/<id>/spelling/<spelling>/grammar/<grammar>/puncutation/<punctuation>/words/<words>/<grade>",methods=["POST"])
def addEssay(role,id,spelling,grammar,punctuation,words,grade):
    if request.method == "POST":
        new_essay = Essays(user_id=id,role=role,num_words=words,num_spelling=spelling,num_grammar=grammar,num_punctuation=punctuation,grade=grade)
        try:
            db.session.add(new_essay)
            db.session.commit()
        except:
            return "ERROR could not add essay"    
    return ""        


@app.route("/update_essay_count/user/<id>/role/<role>",methods=["GET","POST"])
def update_essay_count(id,role):
    if request.method == "POST":
        exists = db.session.query(Users.id).filter_by(id=id).filter_by(role=role).first()
        if(exists):
            curr_user = Users.query.get_or_404(id)
            curr_user.essay_count = curr_user.essay_count + 1;
            try:
                db.session.commit()
            except:
                return "Could not update essay count!" 
    elif request.method == "GET":
        try:
            data = Users.query.filter_by(id=id).filter_by(role=role).first()
            total_essays = [{
                "essayCount": data.essay_count
            }]
            total_essays = json.dumps(total_essays)
            return total_essays
        except:
            return ""
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


@app.route("/mistakes/delete_by_id/id/<id>/role/<role>",methods=["POST"])
def deleteById(id,role):
    if request.method == "POST":
        exists = db.session.query(Users.id).filter(Users.id ==id, Users.role.like(role)).first() #OLD filter_by(id=id).first()
        if(exists):
            curr_user = Users.query.get_or_404(id)
            curr_user.essay_count = 0;
            try:
               db.session.commit()
            except:
                return "Could not update essay count!" 
            #delete mistakes based on user id on both spelling and grammar tables
            db.session.query(Spelling).filter(Spelling.id == id).filter(Spelling.role == role).delete()
            try:
                db.session.commit()
            except:
                return "Could not delete spelling error for the user"
            db.session.query(Grammar).filter(Grammar.id == id).filter(Grammar.role == role).delete()
            try:
                db.session.commit()
            except:
                return "Could not delete grammar error for the user"    
            db.session.query(Syntax).filter(Syntax.id == id).filter(Syntax.role == role).delete()
            try:
                db.session.commit()
            except:
                return "Could not delete syntax error for the user"    
            db.session.query(Essays).filter(Essays.user_id == id).filter(Essays.role == role).delete()
            try:
                db.session.commit()
            except:
                return "Could not delete syntax error for the user"    
            db.session.query(Wordcount).delete()
            try:
                db.session.commit()
            except:
                return "Could not delete syntax error for the user"    
        return ""          
                    
              

@app.route("/role/<role>/id/<id>/type/<type_of_mistake>/word/<word>", methods=["POST"])
def addData(role,id,type_of_mistake,word):
    if request.method == "POST":
        word_to_add = word
        if type_of_mistake == 'spelling':
            exists = db.session.query(Spelling.word).filter(Spelling.word ==word_to_add, Spelling.role.like(role), Spelling.id.like(id)).first() #filter(Spelling.word ==word_to_add, Spelling.role.like(role)).first()
            if(exists):
                task = Spelling.query.get_or_404(word_to_add)
                task.count = task.count + 1
                try:
                    db.session.commit()
                except:
                    return "Could not update word count!"    
            else:        
                new_mistake = Spelling(id= id,word = word_to_add, role=role)
                try:
                    db.session.add(new_mistake)
                    db.session.commit()
                except:
                    return "ERROR" 
            return "SUCCESS!!!!!"
        elif type_of_mistake == 'grammar':
            exists = db.session.query(Grammar.word).filter(Grammar.word ==word_to_add, Grammar.role.like(role), Grammar.id.like(id)).first() #filter(Grammar.id ==id, Grammar.role.like(role)).first()
            if(exists):
                task = Grammar.query.get_or_404(word_to_add)
                task.count = task.count + 1
                try:
                    db.session.commit()
                except:
                    return "Could not update word count!"    
            else:        
                new_mistake = Grammar(id=id,word = word_to_add, role=role)
                try:
                    db.session.add(new_mistake)
                    db.session.commit()
                except:
                    return "ERROR" 
            return "SUCCESS!!!!!"
        elif type_of_mistake == 'syntax':
            exists = db.session.query(Syntax.word).filter(Syntax.word ==word_to_add, Syntax.role.like(role), Syntax.id.like(id)).first() #filter(Syntax.id ==id, Syntax.role.like(role)).first()
            print(exists)
            if(exists):
                task = Syntax.query.get_or_404(word_to_add)
                task.count = task.count + 1
                try:
                    db.session.commit()
                except:
                    return "Could not update word count!"    
            else:        
                new_mistake = Syntax(id=id,word = word_to_add,role=role)
                try:
                    db.session.add(new_mistake)
                    db.session.commit()
                except:
                    return "ERROR" 
            return "SUCCESS!!!!!"    
        return ""    



@app.route("/mistakes_by_user/<id>/role/<role>/type/<type_of_mistake>", methods=["GET"])
def getMistakesByUser(id,role,type_of_mistake):
    if request.method == "GET":
        if type_of_mistake == "spelling":
            try:
                data = Spelling.query.filter_by(id=id).filter_by(role=role).all()
                user_mistakes = []
                for mistake in data:
                    temp_data = {
                        'word': mistake.word,
                        'count': mistake.count
                    }
                    user_mistakes.append(temp_data)
                user_mistakes = json.dumps(user_mistakes)
                return user_mistakes    
            except:
                return ""
        elif type_of_mistake == "grammar":
            try:
                data = Grammar.query.filter_by(id=id).filter_by(role=role).all()
                user_mistakes = []
                for mistake in data:
                    temp_data = {
                        'word': mistake.word,
                        'count': mistake.count
                    }
                    user_mistakes.append(temp_data)
                user_mistakes = json.dumps(user_mistakes)
                return user_mistakes    
            except:
                return ""

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


@app.route("/mistakes/get_all", methods=["GET"])  
def getMistakesCount():
    if  request.method == "GET":
            try:
                data = Spelling.query.order_by(Spelling.date_created).all()
                data2= Grammar.query.order_by(Grammar.date_created).all()
                data3=Syntax.query.order_by(Syntax.date_created).all()
                listaCount = []
                countS = 0
                countG = 0
                countSti=0
                for x in data:
                    countS= countS + x.count
                spelling_count = {
                    'countS' : countS 
                }
                for x in data2:
                    countG = countG + x.count
                grammar_count = {
                    'countG' : countG 
                }
                for x in data3:
                    countSti= countSti + x.count
                syntax_count = {
                    'countSti':  countSti
                }
                listaCount.append(spelling_count)
                listaCount.append(grammar_count)
                listaCount.append(syntax_count)
                listaCount = json.dumps(listaCount) 
                return listaCount
            except:
                return ""                

#kossy wordcount
@app.route("/mistakes/<wordCount>", methods=["POST"])
def addCount(wordCount):
    if request.method == "POST":
        exist=db.session.query(Wordcount).first()
        if(exist):
            wcount = Wordcount.query.get_or_404(3000)
            wcount.count=wcount.count+ int(wordCount)
            try:
                db.session.commit()
            except: 
                return "Could not add count"
        else:
            newcount= Wordcount(count = wordCount ,id=3000)
            try:
                db.session.add(newcount)
                db.session.commit()
            except:
                return "Could not add count"
        return ""        
   

@app.route("/getTotalWords", methods=["GET"])
def getTotalWords():
    if request.method == "GET":
        try:
            data = Wordcount.query.order_by(Wordcount.date_created).all()
            temp_list = []
            temp_average = 0;
            for x in data:
                temp_average = x.count;
            temp_obj = {
                "averageWords" : temp_average
            }
            temp_list.append(temp_obj)
            temp_list = json.dumps(temp_list)
            return temp_list
        except:    
            return "error" 

if __name__ == "__main__":
    app.run(debug=True)
