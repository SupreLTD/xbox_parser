from flask import Flask, send_file

app = Flask(__name__)


@app.route('/get_csv_box')
def get_csv_box():
    return send_file('data/box.csv', as_attachment=True)


app.run(host="0.0.0.0")
