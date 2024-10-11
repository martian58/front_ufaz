from flask import Flask, render_template

app = Flask(__name__, template_folder="templates", static_folder='static')



@app.route('/cvnocss')
def cvnocss():
    return render_template('pw1/cvnocss.html')

@app.route('/cvwithcss')
def cvwithcss():
    return render_template('pw1/cvwithcss.html')

if __name__ == '__main__':
    app.run(debug=True)
    