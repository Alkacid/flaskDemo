import datetime
import hashlib
import os

import mysql.connector
from flask import Flask, render_template, request, redirect

config = {
    'user': 'root',
    'password': '+654',
    'host': 'localhost',
    'database': 'stumanage',
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

headername = {'record_id': '记录ID', 'student_id': '学号', 'reason': '奖惩类型', 'type': '奖惩类型',
              'aap_date': '记录日期', 'class_id': '班级号', 'class_teacher': '班主任', 'class_name': '班级名',
              'college_id': '学院id',
              'college_name': '开课学院名称', 'grade_record_id': '成绩记录id', 'course_id': '课程号', 'grade': '分数',
              'course_name': '课程名', 'credits': '学分', 'hours': '学时', 'teacher_id': '授课教师id',
              'teacher_name': '授课教师', 'exam_time': '考试时间', 'exam_location': '考试地点', 'semester': '开课学期',
              'major_id': '专业编号', 'major_name': '专业名称',
              'major_record_id': '变更记录id', 'previous_major_id': '变更前专业', 'current_major_id': '变更后专业',
              'change_date': '变更日期', 'name': '姓名', 'gender': '性别', 'age': '年龄', 'birthdate': '出生日期',
              'hometown': '籍贯',
              'enrollment_date': '入学日期',

              }


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


def render_sheet(header, headername, data):
    return render_template('sheet.html', headername=headername, header=header, data=data)


# 在 Web 应用程序中呈现数据
@app.route('/table')
def table():
    cursor = cnx.cursor()
    cursor.execute("describe student_info")
    Description = cursor.fetchall()

    query = 'select * from student_info'
    cursor.execute(query)
    data = cursor.fetchall()

    header = [col[0] for col in Description]
    isInt = ['int' in str(col[1]) for col in Description]
    isFloat = ['float' in str(col[1]) for col in Description]
    isDate = ['date' in str(col[1]) for col in Description]
    colType = list(zip(isInt, isFloat, isDate))

    cursor.execute('select * from class')
    classes = cursor.fetchall()
    class_ids = [clazz[0] for clazz in classes]
    classes = ['\t'.join(map(str, clazz)) for clazz in classes]
    classes = dict(zip(class_ids, classes))
    print(classes)

    cursor.execute('select * from major')
    majors = cursor.fetchall()
    major_ids = [major[0] for major in majors]
    majors = ['\t'.join(map(str, major)) for major in majors]
    majors = dict(zip(major_ids, majors))

    sheet_html = render_sheet(header, headername, data)

    return render_template('table.html', sheet_html=sheet_html, header=header, headername=headername, colType=colType,
                           zip=zip, majors=majors, classes=classes)


def create_mysql_query(formData):
    sortItem = formData['sortItem']
    sortDirect = formData['sortDirect']
    del formData['sortItem']
    del formData['sortDirect']
    query = 'SELECT * FROM student_info  WHERE 1 = 1 '
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
    return render_sheet(header, headername, data)


from flask import jsonify


@app.route('/get-one-info', methods=['POST'])
def get_one_info():
    cursor = cnx.cursor()
    cursor.execute("describe student_info")
    Description = cursor.fetchall()
    header = [col[0] for col in Description]
    row_id = request.get_json()['row_id']
    query = "SELECT * from student_info where %s = '%s' " % (header[0], row_id)
    cursor.execute(query)
    info = cursor.fetchone()
    strinfo = []
    for i in info:
        if isinstance(i, datetime.date):
            i = i.strftime('%Y-%m-%d')
        strinfo.append(i)
    info = strinfo
    print(info)
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
