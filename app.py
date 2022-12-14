import os
from os import getenv
from flask import Flask, after_this_request, send_file, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
from gt_converter import create_list, draw_dxf
app = Flask(__name__)
ALLOWED_EXTENSIONS = {"gt"}

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

app.secret_key = getenv("SECRET_KEY")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            to_convert = "uploads/" + filename
            data_list = create_list(to_convert)
            draw_dxf(to_convert, data_list)
            to_download = to_convert + "_export.dxf"
            print(to_download)
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(to_download)
                    os.remove(to_convert)
                except Exception as error:
                    app.logger.error("Error removing or closing downloaded file handle", error)
                return response
            return return_file(to_download)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

def return_file(to_download):
    return send_file(to_download)