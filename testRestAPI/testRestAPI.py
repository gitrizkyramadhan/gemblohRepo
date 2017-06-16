from flask import Flask, request, Response, json
from flask_cors import cross_origin, CORS
import MySQLdb
from bot import Bot


app = Flask(__name__)
CORS(app)


MYSQL_HOST = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PWD = ""
MYSQL_DB1 = "bangjoni72"
MYSQL_DB2 = "bangjoni133"

linebot = None

@app.route('/')
def hello_world():
    return 'Hello, youre access Rest Python'


@app.route('/auth')
def auth():
    username = request.args.get('Username')
    password = request.args.get('Password')
    db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB2)
    cursor = db_connect.cursor()
    cursor.execute("SELECT * from User where username = " + username + " and password = " + password + "")
    data = cursor.fetchone()
    if data is None:
        return 'User and Pass wrong!'
    else:
        return 'Login sukses';


def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError


@app.route('/getBJPay', methods=['GET'])
def getbjp():
    db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB2)
    cur = db_connect.cursor()
    # cur.execute("select * from bjpay_account")
    cur.execute("select va_no, msisdn, phone_number, CAST(amount AS CHAR) from bjpay_account")
    data = cur.fetchall()

    print data
    response = app.response_class(
        response=json.dumps(data, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )
    print(response)
    return response


@app.route('/getTransBJPay', methods=['POST'])
def gettransbjp():
    notelp = request.form['notelp']
    print(notelp)
    db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB2)
    cur = db_connect.cursor()
    query = "select id,user_id,va_no from account_statement where va_no = '" + notelp + "'"
    cur.execute(query)
    data = cur.fetchall()
    print(data)
    return json.dumps(data)


@app.route('/getBJPay1Pulsa', methods=['POST'])
def gettransbjp1puls():
    msisdn = request.form['msisdn']
    print(msisdn)
    db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB2)
    cur = db_connect.cursor()
    query = "select dtm,msisdn,result,trxid,partner_trxid,mesg from 1pulsa_pulsa_token where msisdn = '" + msisdn + "'"
    cur.execute(query)
    data = cur.fetchall()
    print(data)
    return json.dumps(data)


@app.route('/getKomplain', methods=['GET'])
def getkomplain():
    db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB1)
    cur = db_connect.cursor()
    query = "select id,ticket_id,user_id,cust_name,contact_phone,bjpay_phone,complaint,pic,bj_desc from complaint"
    cur.execute(query)
    data = cur.fetchall()
    print(data)
    return json.dumps(data)


@app.route('/getTopup', methods=['GET'])
def getTopup():
    db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB1)
    cur = db_connect.cursor()
    query = "select msisdn,dtm,va_no,`phone`,paid from bjpay"
    cur.execute(query)
    data = cur.fetchall()
    print(data)
    return json.dumps(data)


@app.route('/updatePicComp', methods=['POST'])
def updatePicComp():
    service = request.form['service']
    detail = request.form['detail']
    pic = request.form['pic']
    bjdesc = request.form['bjdesc']
    telp = request.form['telp']
    try:
        db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB1)
        cur = db_connect.cursor()
        query = "update complaint set service = '" + service + "' , detail = '" + detail + "' , pic = '" + pic + "', bj_desc = '" + bjdesc + "' where bjpay_phone = '" + telp + "'"
        cur.execute(query)
        db_connect.commit()
        return json.dumps("sukses")
    except MySQLdb.Error, e:
        print("ERROR")
        return json.dumps("ERROR")


@app.route('/getCompforUpdt', methods=['POST'])
def getCompforUpdt():
    kode = request.form['id']
    print(kode)
    db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB1)
    cur = db_connect.cursor()
    query = "select id, user_id,bjpay_phone, service, complaint, pic, status, CAST(trx_date AS CHAR) from complaint where id =" + kode
    cur.execute(query)
    data = cur.fetchall()
    print(data)
    return json.dumps(data)


@app.route('/getAccountStatement', methods=['POST'])
def getAccountStatement():
    kode = request.form['id']
    db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB2)
    cur = db_connect.cursor()

    query = "select va_no, msisdn, phone_number, CAST(amount AS CHAR), CAST(register_date AS CHAR), CAST(update_time AS CHAR) from bjpay_account where phone_number ='" + kode + "'"
    cur.execute(query)
    data = cur.fetchall()

    query_statement = "select id, CAST(trx_date AS CHAR), type, CAST(amount AS CHAR), description, trx_id from account_statement where va_no ='" + kode + "'"
    cur.execute(query_statement)
    data_statement = cur.fetchall()

    account = {'account':data, 'statements':data_statement}
    print(account)
    return json.dumps(account)


@app.route('/sendMessage', methods=['POST'])
def sendMessage():
    message = request.form['message']
    msisdn = request.form['msisdn']
    print linebot
    linebot.send_text_message(msisdn, message)
    return json.dumps("sukses")

@app.route('/getTopupDetail', methods=['GET'])
def getTopupDetail():
    msisdn = request.args.get('msisdn')
    phone = request.args.get('phone')
    db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB1)
    cur = db_connect.cursor()
    query = "select msisdn,CONVERT(CONVERT(dtm,DATETIME),CHAR),va_no,`phone`,paid, CONVERT(amount, CHAR), bank_type from bjpay where msisdn = '%s' or phone_number = '%s'" % (msisdn, phone)
    cur.execute(query)
    data = cur.fetchall()
    print(data)
    return json.dumps(data)


if __name__ == '__main__':
    with open('BJCONFIG.txt') as f:
        content = f.read().splitlines()
    f.close()

    LINE_TOKEN=content[11].split('=')[1]
    linebot = Bot(LINE_TOKEN)

    app.run(host='0.0.0.0', port=8080)
    app.debug = True



