from flask import Flask,request,render_template,redirect,url_for,send_file,flash,jsonify,g,make_response
import datetime
import swiftclient
import json
from decimal import Decimal
import os
import os.path
import connect_filedb
import urllib
from Crypto.Cipher import DES
import base64
import hashfile
from requests import Session
from cloudant import Cloudant
from Crypto import Random
import hashlib
import os
from collections import defaultdict



iv = Random.get_random_bytes(8)

app = Flask(__name__)
app.secret_key = 'random string'
port = int(os.getenv('VCAP_APP_PORT', 8080))

app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.before_request
def before_request():
    g.dbname, g.client=connect_db()


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/upload',methods=['POST'])
def add_to_container():
    file_name=request.files['file']
    filnameext=file_name.filename
    if file_name.filename== '':
        flash("No Selected File")
        return render_template('index.html')

    if file_name and allowed_file(filnameext):
        text = file_name.read()
        print text
        if text:
            hash_md5 = hashlib.md5()
            hash_md5.update(text)
            hash_filedata = hash_md5.hexdigest()
            print hash_filedata
            flag1, flag, maxver=findfile(filnameext,hash_filedata)
            currdate = str(datetime.datetime.utcnow())
            if flag is True:
                flash("File already exist in database")
                return render_template('index.html')
            if flag is False and flag1 is True:
                new_ver=maxver+1
                my_document=upload_db(filnameext,text,new_ver,hash_filedata,currdate)
                flash("new version of same file")
                return render_template('index.html')
            if flag1 is False:
                ver=1
                my_document=upload_db(filnameext,text,ver,hash_filedata,currdate)
                flash("new file")
                return render_template('index.html')

@app.route('/display', methods=['POST'])
def display_file():
    finaldict={}
    count=1
    my_database = g.client[g.dbname]
    for document in my_database:

        if 'file_name' in document:
            namesdict={}
            versdict = {}

            filename = document['file_name']
            version=document['version_num']
            date=document['date']
            versdict[version]=date

            namesdict[filename]=versdict
            finaldict[count]=namesdict
            count+=1
    return render_template('download.html',namesdict=finaldict)

@app.route('/download', methods=['POST'])
def download_file():

    filename = str(request.form.get("filename"))

    versionnum=request.form.get("ver_num")

    my_database = g.client[g.dbname]
    for document in my_database:

        if 'file_name' in document:

            file_name = document['file_name']
            if filename==file_name:

                if 'version_num' in document:

                    version=document['version_num']
                    if int(version) == int(versionnum):

                        foo=str(document['file_contents'])
                        response=make_response(foo)
                        response.headers["Content-Disposition"] = "attachment; filename=" + filename
                        return response
    return "File not found"

@app.route('/delete', methods=['POST'])
def delete():
    filename = str(request.form.get("filename1"))
    print filename
    versionnum = request.form.get("version1")
    print versionnum
    my_database = g.client[g.dbname]
    for document in my_database:

        if 'file_name' in document:

            file_name = document['file_name']
            if filename == file_name:

                if 'version_num' in document:

                    version = document['version_num']
                    if int(version) == int(versionnum):
                        document.delete()
                        return "File Deleted"


def upload_db(pfilename,text,version_num,hashdata,currdate):
    my_database = g.client[g.dbname]
    entry = {

        'file_name':pfilename ,
        'file_contents': text,
        'version_num': version_num,
        'hash_content': hashdata,
        'date': currdate
    }
    my_document = my_database.create_document(entry)
    return my_document


def findfile(pfilename,hash_filedata):
    flag=False
    flag1=False
    maxver=0
    my_database = g.client[g.dbname]
    for document in my_database:
        if 'file_name' in document:
            filename = document['file_name']
            if filename == pfilename and 'hash_content' in document:
                hashdata = document['hash_content']
                ver = int(document['version_num'])
                if ver>maxver:
                    maxver=ver

                if str(hashdata) == str(hash_filedata):
                    print hashdata
                    print "Same Hash Data"
                    flag=True
                    break
                else:
                    flag1=True
                    continue
            else:
                continue
        else:
            continue
    return flag1,flag,maxver




def connect_db():
    USERNAME,PASSWORD,URL,DATABASE_NAME=connect_filedb.getconfig()
    client = Cloudant(USERNAME, PASSWORD, url=URL)
    client.connect()
    session = client.session()
    if DATABASE_NAME in client.all_dbs():
        return DATABASE_NAME,client
    else:
        return "No such Database exist"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)