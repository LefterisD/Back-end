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

# ------------------------STEPS---------
# inside python shell
#from flaskapi import db
# db.create_all()


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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stu_name = db.Column(db.String(40))
    stu_class = db.Column(db.String(20))
    user_id = db.Column(db.String(30))
    role = db.Column(db.String(15))
    num_words = db.Column(db.Integer)
    num_spelling = db.Column(db.Integer)
    num_grammar = db.Column(db.Integer)
    num_punctuation = db.Column(db.Integer)
    grade = db.Column(db.String(10))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return 'Created essay %d' % self.id


class ModelWeights(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    user_id = db.Column(db.String(30), primary_key=True)
    role = db.Column(db.String(15))
    spelling_w = db.Column(db.Float)
    grammar_w = db.Column(db.Float)
    punctuation_w = db.Column(db.Float)

    def __repr__(self):
        return 'Updated weights '


class Spelling(db.Model):
    id = db.Column(db.String(50))
    sec_id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50))
    count = db.Column(db.Integer, default=1)
    role = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return 'Created %s' % self.word


class Grammar(db.Model):
    id = db.Column(db.String(50))
    sec_id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50))
    count = db.Column(db.Integer, default=1)
    role = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return 'Created %s' % self.word


class Syntax(db.Model):
    id = db.Column(db.String(50))
    sec_id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50))
    count = db.Column(db.Integer, default=1)
    role = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return 'Created %s' % self.word

# kossy word count


class Wordcount(db.Model):
    id = db.Column((db.Integer), primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20))
    role = db.Column(db.String(15))
    count = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

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


'''@app.route("/weights/update/<role>/<id>/<feedback>",methods=["POST"])
def updateWeights(role,id,feedback):
    if(request.method ==  "POST"):
        user_id = id
        if(feedback == "no"):
            weight_to_remove_spelling = 0.2
            weight_to_add_grammar = 0.12
            weight_to_add_punctuation = 0.08

            exists = db.session.query(ModelWeights).filter_by(user_id=id).filter_by(role=role).first()

            if(exists):
                weights = ModelWeights.query.get_or_404(id)
                weights.spelling_w = weights.spelling_w + weight_to_remove_spelling 
                weights.grammar_w = weights.grammar_w - weight_to_add_grammar
                weights.punctuation_w = weights.punctuation_w - weight_to_add_punctuation

                try:
                    db.session.commit()
                except:
                    return "Error could not update weights"
     
        else:
            return feedback
        return ""            
'''


@app.route("/weights/update/<role>/<id>/<type>/<computed_grade>/<user_grade>", methods=["POST"])
def updateWeights(role, id, type, computed_grade, user_grade):
    if(request.method == "POST"):
        user_id = id

        exists = db.session.query(ModelWeights).filter_by(
            user_id=id).filter_by(role=role).first()
        computed_grade = float(computed_grade)
        user_grade = float(user_grade)
        if exists:
            weights = ModelWeights.query.get_or_404(id)
            if type == "spelling":
                if(computed_grade > user_grade):
                    grade_division = user_grade / computed_grade
                    grade_division = round(grade_division, 2)
                    weights.spelling_w = weights.spelling_w + grade_division

                    grade_division_balance = grade_division / 2
                    grade_division_balance = round(grade_division_balance, 2)

                    weights.grammar_w = weights.grammar_w - grade_division_balance
                    weights.punctuation_w = weights.punctuation_w - grade_division_balance
                else:
                    grade_division = computed_grade / user_grade
                    grade_division = round(grade_division, 2)
                    weights.spelling_w = weights.spelling_w - grade_division

                    grade_division_balance = grade_division / 2
                    grade_division_balance = round(grade_division_balance, 2)

                    weights.grammar_w = weights.grammar_w + grade_division_balance
                    weights.punctuation_w = weights.punctuation_w + grade_division_balance
            elif type == "grammar":
                if(computed_grade > user_grade):
                    grade_division = user_grade / computed_grade
                    grade_division = round(grade_division, 2)
                    weights.grammar_w = weights.grammar_w + grade_division

                    grade_division_balance = grade_division / 2
                    grade_division_balance = round(grade_division_balance, 2)

                    weights.spelling_w = weights.spelling_w - grade_division_balance
                    weights.punctuation_w = weights.punctuation_w - grade_division_balance
                else:
                    grade_division = computed_grade / user_grade
                    grade_division = round(grade_division, 2)
                    weights.grammar_w = weights.grammar_w - grade_division

                    grade_division_balance = grade_division / 2
                    grade_division_balance = round(grade_division_balance, 2)

                    weights.spelling_w = weights.spelling_w + grade_division_balance
                    weights.punctuation_w = weights.punctuation_w + grade_division_balance
            elif type == "punctuation":
                if(computed_grade > user_grade):
                    grade_division = user_grade / computed_grade
                    grade_division = round(grade_division, 2)
                    weights.punctuation_w = weights.punctuation_w + grade_division

                    grade_division_balance = grade_division / 2
                    grade_division_balance = round(grade_division_balance, 2)

                    weights.spelling_w = weights.spelling_w - grade_division_balance
                    weights.grammar_w = weights.grammar_w - grade_division_balance
                else:
                    grade_division = computed_grade / user_grade
                    grade_division = round(grade_division, 2)
                    weights.punctuation_w = weights.punctuation_w - grade_division

                    grade_division_balance = grade_division / 2
                    grade_division_balance = round(grade_division_balance, 2)

                    weights.spelling_w = weights.spelling_w + grade_division_balance
                    weights.grammar_w = weights.grammar_w + grade_division_balance
            try:
                db.session.commit()
            except:
                return "Error could not update weights"
        else:
            return feedback
        return ""


@app.route("/add/user/weights/<role>/<id>/<w1>/<w2>/<w3>", methods=["POST"])
def setUserWeights(role, id, w1, w2, w3):
    if request.method == "POST":
        exists = db.session.query(ModelWeights).first()
        if(exists):
            user_exists = db.session.query(ModelWeights).filter_by(
                user_id=id).filter_by(role=role).first()
            if(user_exists):
                pass
            else:
                new_user_weight = ModelWeights(
                    user_id=id, role=role, spelling_w=w1, grammar_w=w2, punctuation_w=w3)
                try:
                    db.session.add(new_user_weight)
                    db.session.commit()
                except:
                    return "Could not add user"
        else:
            new_user_weight = ModelWeights(
                user_id=id, role=role, spelling_w=15, grammar_w=3.5, punctuation_w=1.5)
            try:
                db.session.add(new_user_weight)
                db.session.commit()
            except:
                return "Could not add first user"
        return ""


@app.route("/weights/by/<role>/<id>", methods=["GET"])
def getWeights(role, id):
    if request.method == "GET":
        user_exists = db.session.query(ModelWeights).filter_by(
            user_id=id).filter_by(role=role).first()
        if(user_exists):
            weight_data = ModelWeights.query.filter(
                ModelWeights.user_id == id).filter(ModelWeights.role == role).first()
            weights = []

            temp_weights = {
                "spelling_w": weight_data.spelling_w,
                "grammar_w": weight_data.grammar_w,
                "punctuation_w": weight_data.punctuation_w
            }

            weights.append(temp_weights)
            weights = json.dumps(weights)
            return weights
        else:
            return ""
    return ""


@app.route('/test/route', methods=["GET"])
def test():
    if request.method == "GET":
        weight_data = ModelWeights.query.order_by(ModelWeights.user_id).all()
        temp_arr = []

        for x in weight_data:
            temp_obj = {
                "w1": x.spelling_w,
                "w2": x.grammar_w,
                "w3": x.punctuation_w,
            }
            temp_arr.append(temp_obj)
        temp_arr = json.dumps(temp_arr)
        return temp_arr


@app.route("/weights/all", methods=["GET"])
def getAverageWeights():
    if request.method == "GET":
        weight_data = ModelWeights.query.order_by(ModelWeights.user_id).all()
        weights = []
        count = 0
        ws = 0
        wg = 0
        wp = 0

        for w in weight_data:
            ws = ws + w.spelling_w
            wg = wg + w.grammar_w
            wp = wp + w.punctuation_w
            count = count + 1

        if(count != 0):
            temp_weights = {
                "spelling_w": ws/count,
                "grammar_w": wg/count,
                "punctuation_w": wp/count
            }
        else:
            temp_weights = {
                "spelling_w": 13,
                "grammar_w": 5,
                "punctuation_w": 2
            }

        weights.append(temp_weights)
        weights = json.dumps(weights)

        return weights


@app.route("/user/user_info", methods=["POST"])
def userInfo():
    if request.method == "POST":
        id = request.form.get("id")
        role = request.form.get("role")
        age = request.form.get('age')
        education = request.form.get('level')
        mother_tongue = request.form.get('MT')

        new_info = UserInfo(id=id, role=role, age=age,
                            education=education, mother_tongue=mother_tongue)
        try:
            db.session.add(new_info)
            db.session.commit()
        except:
            return "Could not update info"
    return ""


@app.route("/essays/all/role/<role>/id/<id>", methods=["GET"])
def getEssays(role, id):
    if request.method == "GET":
        try:
            temp_list = []
            essay_data = Essays.query.filter(
                Essays.user_id == id).filter(Essays.role == role).all()

            for essay in essay_data:
                essay_obj = {
                    "stu_name": essay.stu_name,
                    "stu_class": essay.stu_class,
                    "num_words": essay.num_words,
                    "num_spelling": essay.num_spelling,
                    "num_grammar": essay.num_grammar,
                    "num_punctuation": essay.num_punctuation,
                    "grade": essay.grade,
                }
                temp_list.append(essay_obj)
            temp_list = json.dumps(temp_list)
            return temp_list
        except:
            return "Error could not return essays"


@app.route("/essays/add/role/<role>/id/<id>/student/<student>/class/<stuClass>/spelling/<spelling>/grammar/<grammar>/puncutation/<punctuation>/words/<words>/<grade>", methods=["POST"])
def addEssay(role, id, student, stuClass, spelling, grammar, punctuation, words, grade):
    if request.method == "POST":
        new_essay = Essays(user_id=id, stu_name=student, stu_class=stuClass, role=role, num_words=words,
                           num_spelling=spelling, num_grammar=grammar, num_punctuation=punctuation, grade=grade)
        try:
            db.session.add(new_essay)
            db.session.commit()
        except:
            return "ERROR could not add essay"
    return ""


@app.route("/update_essay_count/user/<id>/role/<role>", methods=["GET", "POST"])
def update_essay_count(id, role):
    if request.method == "POST":
        exists = db.session.query(Users.id).filter_by(
            id=id).filter_by(role=role).first()
        if(exists):
            curr_user = Users.query.get_or_404(id)
            curr_user.essay_count = curr_user.essay_count + 1
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
            return "Error could not get essay counter"
    return ""


@app.route("/user/<role>/<id>", methods=["GET", "POST"])
def users(role, id):
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
        return ""


@app.route("/mistakes/delete_by_id/id/<id>/role/<role>", methods=["POST"])
def deleteById(id, role):
    if request.method == "POST":
        exists = db.session.query(Users.id).filter(
            Users.id == id, Users.role.like(role)).first()  # OLD filter_by(id=id).first()
        if(exists):
            curr_user = Users.query.filter(
                Users.id == id, Users.role.like(role)).first()
            curr_user.essay_count = 0
            try:
                db.session.commit()
            except:
                return "Could not update essay count!"
        # delete mistakes based on user id on both spelling and grammar tables
        db.session.query(Spelling).filter(Spelling.id == id).filter(
            Spelling.role == role).delete()
        try:
            db.session.commit()
        except:
            return "Could not delete spelling error for the user"
        db.session.query(Grammar).filter(Grammar.id == id).filter(
            Grammar.role == role).delete()
        try:
            db.session.commit()
        except:
            return "Could not delete grammar error for the user"
        db.session.query(Syntax).filter(Syntax.id == id).filter(
            Syntax.role == role).delete()
        try:
            db.session.commit()
        except:
            return "Could not delete syntax error for the user"
        db.session.query(Essays).filter(Essays.user_id ==
                                        id).filter(Essays.role == role).delete()
        try:
            db.session.commit()
        except:
            return "Could not delete syntax error for the user"
        db.session.query(Wordcount).filter(Wordcount.user_id ==
                                           id).filter(Wordcount.role == role).delete()
        try:
            db.session.commit()
        except:
            return "Could not delete wordcount error for the user"
        return ""


@app.route("/role/<role>/id/<id>/type/<type_of_mistake>/word/<word>", methods=["POST"])
def addData(role, id, type_of_mistake, word):
    if request.method == "POST":
        word_to_add = word
        if type_of_mistake == 'spelling':
            exists = db.session.query(Spelling.word).filter(Spelling.word == word_to_add, Spelling.role.like(
                role), Spelling.id.like(id)).first()  # filter(Spelling.word ==word_to_add, Spelling.role.like(role)).first()
            if(exists):
                task = Spelling.query.filter(Spelling.word == word_to_add, Spelling.role.like(
                    role), Spelling.id.like(id)).first()  # .get_or_die_404(word_to_add) if primary key is the word
                task.count = task.count + 1
                try:
                    db.session.commit()
                except:
                    return "Could not update word count!"
            else:
                new_mistake = Spelling(id=id, word=word_to_add, role=role)
                try:
                    db.session.add(new_mistake)
                    db.session.commit()
                except:
                    return "ERROR"
            return "SUCCESS!!!!!"
        elif type_of_mistake == 'grammar':
            exists = db.session.query(Grammar.word).filter(Grammar.word == word_to_add, Grammar.role.like(
                role), Grammar.id.like(id)).first()  # filter(Grammar.id ==id, Grammar.role.like(role)).first()
            if(exists):
                task = Grammar.query.filter(Grammar.word == word_to_add, Grammar.role.like(
                    role), Grammar.id.like(id)).first()
                task.count = task.count + 1
                try:
                    db.session.commit()
                except:
                    return "Could not update word count!"
            else:
                new_mistake = Grammar(id=id, word=word_to_add, role=role)
                try:
                    db.session.add(new_mistake)
                    db.session.commit()
                except:
                    return "ERROR"
            return "SUCCESS!!!!!"
        elif type_of_mistake == 'syntax':
            exists = db.session.query(Syntax.word).filter(Syntax.word == word_to_add, Syntax.role.like(
                role), Syntax.id.like(id)).first()  # filter(Syntax.id ==id, Syntax.role.like(role)).first()
            if(exists):
                task = Syntax.query.filter(Syntax.word == word_to_add, Syntax.role.like(
                    role), Syntax.id.like(id)).first()
                task.count = task.count + 1
                try:
                    db.session.commit()
                except:
                    return "Could not update word count!"
            else:
                new_mistake = Syntax(id=id, word=word_to_add, role=role)
                try:
                    db.session.add(new_mistake)
                    db.session.commit()
                except:
                    return "ERROR"
            return "SUCCESS!!!!!"
        return ""


@app.route("/mistakes_by_user/<id>/role/<role>/type/<type_of_mistake>", methods=["GET"])
def getMistakesByUser(id, role, type_of_mistake):
    if request.method == "GET":
        if type_of_mistake == "spelling":
            try:
                data = Spelling.query.filter_by(
                    id=id).filter_by(role=role).all()
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
                data = Grammar.query.filter_by(
                    id=id).filter_by(role=role).all()
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
                        'word': x.word,
                        'count': x.count
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
                        'word': x.word,
                        'count': x.count
                    }
                    lista.append(temp_data)
                lista = json.dumps(lista)
                return lista
            except:
                return ""


@app.route("/mistakes/get_all/role/<role>/id/<id>", methods=["GET"])
def getMistakesCount(role, id):
    if request.method == "GET":
        try:
            data = Spelling.query.order_by(Spelling.date_created).filter(
                Spelling.id == id).filter(Spelling.role == role).all()
            data2 = Grammar.query.order_by(Grammar.date_created).filter(
                Grammar.id == id).filter(Grammar.role == role).all()
            data3 = Syntax.query.order_by(Syntax.date_created).filter(
                Syntax.id == id).filter(Syntax.role == role).all()
            listaCount = []
            countS = 0
            countG = 0
            countSti = 0
            for x in data:
                countS = countS + x.count
            spelling_count = {
                'countS': countS
            }
            for x in data2:
                countG = countG + x.count
            grammar_count = {
                'countG': countG
            }
            for x in data3:
                countSti = countSti + x.count
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


# kossy wordcount
@app.route("/mistakes/<wordCount>/<id>/<role>", methods=["POST"])
def addCount(wordCount, id, role):
    if request.method == "POST":
        # exist=db.session.query(Wordcount).first()
        exists = db.session.query(Wordcount.user_id).filter_by(
            user_id=id).filter_by(role=role).first()
        if(exists):
            wcount = Wordcount.query.filter(
                Wordcount.user_id == id, Wordcount.role.like(role)).first()
            #wcount = Wordcount.query.get_or_404(3000)
            wcount.count = wcount.count + int(wordCount)
            try:
                db.session.commit()
            except:
                return "Could not add count"
        else:
            print("DEN UPARXEI O XRHSTHS", exists)
            newcount = Wordcount(user_id=id, role=role, count=wordCount)
            try:
                db.session.add(newcount)
                db.session.commit()
            except:
                return "Could not add count"
        return ""


@app.route("/getTotalWords/<id>/<role>", methods=["GET"])
def getTotalWords(id, role):
    if request.method == "GET":
        exists = db.session.query(Wordcount.user_id).filter_by(
            user_id=id).filter_by(role=role).first()

        if(exists):
            try:
                data = Wordcount.query.filter(
                    Wordcount.user_id == id, Wordcount.role.like(role)).first()
                print(data.count)
                temp_list = []
                temp_average = 0
                temp_average = data.count
                temp_obj = {
                    "averageWords": temp_average
                }
                temp_list.append(temp_obj)
                temp_list = json.dumps(temp_list)
                return temp_list
            except:
                return "error"
        return "user does not exist"


if __name__ == "__main__":
    app.run(debug=True)
