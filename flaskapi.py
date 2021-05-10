from flask import Flask, render_template, url_for, request
import requests, json
from flask_cors import CORS

app = Flask("__main__")
CORS(app)

@app.route("/api/v1/check/<text>", methods=["POST", "GET"])
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


if __name__ == "__main__":
    app.run(debug=True)
