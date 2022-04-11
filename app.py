import os
import uuid
import time

from flask import Flask, render_template, request, url_for, redirect, Response
from werkzeug.utils import secure_filename

from model import predict_cells, concentrate, alive_cells

from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CUR_LOADING = 0

def generate():
    yield "data:" + str(CUR_LOADING) + "\n\n"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    global CUR_LOADING
    CUR_LOADING = 0
    progress()

    if request.method == 'GET':
        return render_template('index.html', show_result="hidden")

    if request.method == 'POST':
        # list of uploaded files
        progress()
        files_list = []

        session_uid = uuid.uuid4().hex

        res2 = {}
        res2['cnt1'] = 0
        res2['cnt2'] = 0
        res2['path'] = []

        dilution = request.form.get('coeff')

        info = []

        if dilution == '':
            info.append("Не заполнена степень разведения")
            return render_template('index.html', show_result="visible", add_info=info)

        cur_files_list = request.files.getlist('image_uploads')

        if cur_files_list[0].filename == "":
            info.append("Не выбраны файлы")
            return render_template('index.html', show_result="visible", add_info=info)

        list_len = int(100/len(cur_files_list))

        for file in cur_files_list:
            CUR_LOADING = 3
            progress()

            filename = session_uid + '_' + secure_filename(file.filename)

            # add to disk and list
            if file and allowed_file(filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                files_list.append(filename)

                # drop old files
                now = time.time()
                drop_files = os.listdir(app.config['UPLOAD_FOLDER'])
                for cur_file in drop_files:
                    mtime = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], cur_file)).st_mtime
                    if now - mtime > 15*60:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], cur_file))


                cnt1, cnt2, pic = predict_cells(file)

                CUR_LOADING += list_len
                progress()

                res2['cnt1'] += cnt1
                res2['cnt2'] += cnt2
                res2['path'].append(pic)

        if res2['cnt1'] != 0:
            have_data = "visible"
        else:
            have_data = "hidden"

        calive, ccells = concentrate(dilution, len(res2['path']), res2['cnt1'], res2['cnt2'])

        info.append(f"Живых клеток: {res2['cnt1']}")
        info.append(f"Мёртвых клеток: {res2['cnt2']}")
        info.append(f"Количество живых клеток в 1мл суспензии: {round(calive/1_000_000, 2)}e+06")
        info.append(f"Общее количество клеток в 1мл суспензии: {round(ccells/1_000_000, 2)}e+06")
        info.append(f"Жизнеспособность культуры: {alive_cells(res2['cnt1'], res2['cnt2'])}%")

        CUR_LOADING = 100
        progress()

        return render_template('index.html', add_info=info, show_result=f"{have_data}", files_list=res2['path'])


@app.route('/progress')
def progress():
    return Response(generate(), mimetype='text/event-stream')

@app.route('/display/<filename>')
def display_image(filename):
	return redirect(url_for('static', filename='photos/' + filename), code=301)

@app.route('/methodology')
def methodology():
    return render_template('methodology.html')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8099)