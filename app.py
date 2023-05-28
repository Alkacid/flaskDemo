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
Description = None
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


# 在 Web 应用程序中呈现数据
@app.route('/table')
def index():
    cursor = cnx.cursor()
    cursor.execute("describe borrow")
    Description = cursor.fetchall()
    header = [col[0] for col in Description]
    isInt = ['int' in str(col[1]) for col in Description]
    isFloat = ['float' in str(col[1]) for col in Description]
    isDate = ['date' in str(col[1]) for col in Description]
    print(header)
    colType = zip(isInt, isFloat, isDate)
    query = "SELECT * FROM borrow"
    cursor.execute(query)
    data = cursor.fetchall()
    # print(data)
    # 确定表的长度和宽度

    return render_template('table.html', header=header, data=data, colType=colType, zip=zip)


@app.route('/table/sort', methods=['POST'])
def sort_by():
    print('you are here')
    if request.method == 'POST':
        # cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sortItem = request.form['sortItem']
        sortDirect = request.form['sortDirect']
        cursor.execute("SELECT * FROM borrow ORDER BY " + sortItem + " " + sortDirect)
        data = cursor.fetchall()
        query = "describe borrow"
        cursor.execute(query)
        header = [col[0] for col in cursor.fetchall()]
        return render_template('table.html', data=data, header=header)


def create_html_table(header, data):
    # Header row
    header_row = "<tr>"
    for column in header:
        header_row += f"<th>{column}</th>"
    header_row += "</tr>"

    # Data rows
    data_rows = ""
    for item in data:
        data_row = "<tr>"
        for column in item:
            data_row += f"<td>{column}</td>"
        data_row += "</tr>"
        data_rows += data_row

    # Assemble the HTML table
    html_table = f"""
        <table class="table table-striped table-bordered table-hover"
                       style="width: 80%; table-layout: auto; margin: auto auto" id="table">
            <thead>
                {header_row}
            </thead>
            <tbody>
                {data_rows}
            </tbody>
        </table>
    """

    return html_table


def create_mysql_query(formData):
    sortItem = formData['sortItem']
    sortDirect = formData['sortDirect']
    del formData['sortItem']
    del formData['sortDirect']
    query = 'SELECT * FROM borrow  WHERE 1 = 1 '
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
    # sortItem = formData['sortItem']
    # sortDirect = formData['sortDirect']
    # del formData['sortItem']
    # del formData['sortDirect']
    #
    # query = 'SELECT * FROM borrow  WHERE 1 = 1 '
    #
    # for key in formData.keys():
    #     if formData[key] == '':
    #         continue
    #     query = query + " and %s = '%s'" % (key, formData[key])
    #
    # if sortItem != 'default':
    #     query = query + ' ORDER BY ' + sortItem + " " + sortDirect
    query = create_mysql_query(formData)
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    # print(data)
    header = [col[0] for col in cursor.description]
    # print(header)
    table = create_html_table(header, data)
    # print(table)
    return table


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
    return render_template('contact.html')


if __name__ == '__main__':
    # test_1()
    app.run(host='0.0.0.0')
