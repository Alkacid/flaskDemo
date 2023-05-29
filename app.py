import hashlib
import os

import mysql.connector
from flask import Flask, render_template, request, redirect

config = {
    'user': 'root',
    'password': '+654',
    'host': 'localhost',
    'database': 'lab1',
    'raise_on_warnings': True
}
usersql = {
    'user': 'root',
    'password': '+654',
    'host': 'localhost',
    'database': 'edu_manage',
    'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)
app = Flask(__name__)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':

        userdata = mysql.connector.connect(**usersql)
        username = request.form['username']
        password = request.form['password']

        # 生成唯一的 salt 值
        salt = os.urandom(16).hex()
        hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        cursor = userdata.cursor()
        cursor.execute(
            "INSERT INTO user (username, password, salt) VALUES ( '%s', '%s', '%s');" % (username, hashed_password,
                                                                                         salt))
        userdata.commit()
        cursor.close()
        return redirect('/')
    else:
        return render_template('register.html')


def render_sheet(header, data):
    return render_template('sheet.html', header=header, data=data)


# 在 Web 应用程序中呈现数据
@app.route('/table')
def table():
    cursor = cnx.cursor()
    cursor.execute("describe book")
    Description = cursor.fetchall()
    print(Description)
    header = [col[0] for col in Description]
    isInt = ['int' in str(col[1]) for col in Description]
    isFloat = ['float' in str(col[1]) for col in Description]
    isDate = ['date' in str(col[1]) for col in Description]
    print(header)
    colType = list(zip(isInt, isFloat, isDate))
    query = "SELECT * FROM book"
    cursor.execute(query)
    data = cursor.fetchall()
    # print(data)
    # 确定表的长度和宽度
    sheet_html = render_sheet(header, data)

    return render_template('table.html', sheet_html=sheet_html, header=header, colType=colType, zip=zip)


@app.route('/table/sort', methods=['POST'])
def sort_by():
    print('you are here')
    if request.method == 'POST':
        # cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sortItem = request.form['sortItem']
        sortDirect = request.form['sortDirect']
        cursor.execute("SELECT * FROM book ORDER BY " + sortItem + " " + sortDirect)
        data = cursor.fetchall()
        query = "describe book"
        cursor.execute(query)
        header = [col[0] for col in cursor.fetchall()]

        return render_template('table.html', data=data, header=header, len=len(header))


def create_mysql_query(formData):
    sortItem = formData['sortItem']
    sortDirect = formData['sortDirect']
    del formData['sortItem']
    del formData['sortDirect']
    query = 'SELECT * FROM book  WHERE 1 = 1 '
    for key in formData.keys():
        if 'Lower' in key:
            lowerbound = formData[key]
        elif 'Upper' in key:
            upperbound = formData[key]
            if lowerbound == '' and upperbound == '':
                continue
            elif lowerbound != '' and upperbound != '':
                column = key.replace('Upper', '')
                query = query + " and %s between '%s' and '%s' " % (column, lowerbound, upperbound)
            else:
                column = key.replace('Upper', '')
                if lowerbound != '':
                    query = query + " and %s = '%s' " % (column, lowerbound)
                if upperbound != '':
                    query = query + " and %s = '%s' " % (column, upperbound)
        else:
            if formData[key] == '':
                continue
            query = query + " and %s = '%s' " % (key, formData[key])

    if sortItem != 'default':
        query = query + ' ORDER BY ' + sortItem + " " + sortDirect

    return query


@app.route('/get-table-data', methods=['POST'])
def get_table_data():
    formData = dict(request.form)
    print(formData)
    cursor = cnx.cursor()
    query = create_mysql_query(formData)
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    header = [col[0] for col in cursor.description]
    return render_sheet(header, data)


from flask import jsonify


@app.route('/get-one-info', methods=['POST'])
def get_one_info():
    cursor = cnx.cursor()
    cursor.execute("describe book")
    Description = cursor.fetchall()
    header = [col[0] for col in Description]
    row_id = request.get_json()['row_id']
    query = "SELECT * from book where %s = '%s' " % (header[0], row_id)
    cursor.execute(query)
    info = cursor.fetchone()
    data = {header[i]: info[i] for i in range(len(header))}

    primes = []
    for col in Description:
        if 'PRI' in col[3]:
            primes.append(col[0])
    response_obj = {
        "info": data,
        "primes": primes
    }
    response_text = jsonify(response_obj)
    return response_text


@app.route('/', methods=['GET', 'POST'])
def login():
    return redirect('/table')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userdata = mysql.connector.connect(**usersql)
        cursor = userdata.cursor()
        cursor.execute("SELECT * FROM user WHERE username= '%s'" % username)
        user = cursor.fetchone()

        print(user)
        if user:
            columns = [desc[0] for desc in cursor.description]
            # 将查询结果转换为字典类型
            user = dict(zip(columns, user))
            salt = user['salt']
            hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
            if hashed_password == user['password']:
                return redirect('/table')

        return render_template('login.html', error_msg='登录失败，请检查用户名和密码是否正确')

    return render_template('login.html')


@app.route('/contact', )
def contact():
    return render_template('contact.html', header=[1, 2, 3, 4, 5])


if __name__ == '__main__':
    app.run(host='0.0.0.0')
