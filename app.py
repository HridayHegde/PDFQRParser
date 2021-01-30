import os

from waitress import serve

from flask import Flask, render_template, request, redirect, url_for, send_from_directory,jsonify
from werkzeug.utils import secure_filename
from threading import Thread
from pathlib import Path

#session handling
from uuid import uuid4
from flask import session
import queue


import json
import MainHandler as MH
import shutil

from os import listdir
from os.path import isfile, join
from datetime import datetime


# Initialize the Flask application
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
th = Thread()
#finished = "running"
#sessionid = ""
MYDIR = os.path.dirname(__file__)
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'OriginFolder/'
app.config['OUTPUT_FOLDER'] = 'OutputFolder/'
app.config['ZIP_FOLDER'] = 'ZipOutput/'
app.config['MAIN_FOLDER'] =''
app.config['TEMPLATE_FOLDER']='TemplateGenerator/Uploads/'
app.config['TEMPLATE_OUTPUT']='TemplateGenerator/Output/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['pdf','PDF'])

#session Handling
statusdict = {}

    
def createdefaultfolders():
    try:
        shutil.rmtree(app.config['UPLOAD_FOLDER']+session.get('number')+"/")
    except OSError as e:
        print(e)
    try:
        shutil.rmtree(app.config['OUTPUT_FOLDER']+session.get('number')+"/")
    except OSError as e:
        print(e)
    try:
        os.mkdir(app.config['UPLOAD_FOLDER']+session.get('number')+"/")
    except OSError as e:
        print(e)
    try:
        os.mkdir(app.config['OUTPUT_FOLDER']+session.get('number')+"/")
    except OSError as e:
        print(e)


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    global statusdict
    session['number'] = str(uuid4())
    print(session.get('number'))
    createdefaultfolders()
    #global sessionid
    sessionid = session.get('number')
    #finished = "running" 
    statusdict[session.get('number')] = "running"
    
    

    return render_template('index.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded files
    uploaded_files = request.files.getlist("file[]")
    filenames = []
    global th
    #global finished
    print("IM here")
    filenames = []
    for file in uploaded_files:
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            print(file)
            # Make the filename safe, remove unsupported chars
            filename, file_extension = os.path.splitext(file.filename)
            filename = secure_filename(Path(filename).stem)
            z = filename
            filename = filename+file_extension
            
            
            # Move the file form the temporal folder to the upload
            # folder we setup
           
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+session.get('number')+"/", filename))
            #os.remove(file)
            # Save the filename into a list, we'll use it later
            
            x = z+"_RequiredFiledsOnly.csv"
            #filenames.append(filename)
            #filenames.append(x)
            
            # Redirect the user to the uploaded_file route, which
            # will basicaly show on the browser the uploaded file
    # Load an html page with a link to each uploaded file
    
    #th = Thread(target=upload_async, args=(session.get('number'),))
    #que = queue.Queue()
    th = Thread(target=upload_async, args=(session.get('number'),))
    
    print(th)
    th.start()
    #th.join()
    
    
    filenames.append("output_zip.zip")
    
    head = "Output"
    print("Processing.....")
    return render_template('loading.html', filenames=filenames,heading=head)

@app.route('/status')
def upload_thread_status():
    #print( "Return the status of the worker thread")
    global statusdict
    #print(finished)
    
    status = "running"
    if  statusdict[session.get('number')] == 'finished':
        print("Task Completed")
        status = 'finished'
    elif  statusdict[session.get('number')] == "errored":
        status = "errored"
    else:
        status = "running"
    return jsonify(dict(status=(status)))



def upload_async(sessionid):
    print(" The worker function ")
    global statusdict
    
    status = MH.DecryptQR(app.config['UPLOAD_FOLDER']+sessionid+"/",app.config['OUTPUT_FOLDER']+sessionid+"/",sessionid)
    
    statusdict[sessionid] =  status

@app.route('/result')
def result():
    """ Just give back the result of your heavy work """
    filenames = [f for f in listdir(app.config["OUTPUT_FOLDER"]+session.get('number')+"/") if isfile(join(app.config["OUTPUT_FOLDER"]+session.get('number')+"/", f))]
    
    session['finished'] = 'running'

    now = datetime.now()
    dt_string1 = now.strftime("%d-%m-%Y_%H-%M-%S")
    print(":::::::::::::::::::::::::::::::::: Process Ended at "+str(dt_string1)+" ::::::::::::::::::::::::::::::::::")
    return render_template('upload_main.html', filenames=filenames,heading="Output")

@app.route('/error')
def error():
    
    return render_template("error.html")

@app.route('/uploadjson', methods=['POST'])
def uploadmain():
    # Get the name of the uploaded files
    
    uploaded_files = request.files.getlist("file[]")
    try:
        os.remove("requiredFields.json")
    except:
        print("File Doesnt Exist")

    uploaded_files[0].save("./requiredFields.json")
    print("JSON UPLOADED")
    return render_template('index.html',scroll='json')

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploadtemp/<filename>')
def uploaded_template(filename):
    
    return send_from_directory(app.config['TEMPLATE_OUTPUT'],filename,mimetype='application/octet-stream')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER']+session.get('number')+"/",filename)

@app.route('/download')
def download_file():
    filename = "requiredFields.json"

    return send_from_directory(app.config['MAIN_FOLDER'],filename,as_attachment=True,)






if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    serve(app,host='0.0.0.0',port=50541,threads = True)