from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>welcome to my flask app! adding more text </h1> <div> <button> click me !</button> </div>"


if __name__ == '__main__':
    app.run(debug = True)

print("hello from server.py")

