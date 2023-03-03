from flask import Flask, render_template

app = Flask(__name__)

# configure app
app.config.from_mapping(
    SECRET_KEY='dev'
)

@app.get('/')
def index():
    return render_template('index.html')

from blueprints import auth
import db

# register blueprints
app.register_blueprint(auth.bp)

# Auto close db connection after each response regardless of success or error
app.teardown_appcontext(db.on_response_close)

app.run(debug=True)
