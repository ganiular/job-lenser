from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# configure app
app.config.from_mapping(
    SECRET_KEY='dev'
)

from blueprints import auth, account
import db

# register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(account.bp)

# file downloads
@app.get('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory('uploads', filename, as_attachment=True)

# Auto close db connection after each response regardless of success or error
app.teardown_appcontext(db.on_response_close)

# Error handlers
@app.errorhandler(404)
def page_not_found(exeption):
    print('Error: page not found')
    return render_template('404.html'), 404

app.run(debug=True)
