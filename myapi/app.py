#!/usr/bin/python3

"""
Web application to showcase your REST API skills
"""

import connexion

app = connexion.App(__name__, specification_dir="./")

app.add_api("swagger.yml")


@app.route("/")
def home():
    from flask import render_template
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
