import datetime
import hashlib
import os

import mysql.connector
from flask import Flask, render_template, request, redirect
from flask import jsonify

config = {
    'user': 'root',
    'password': '+654',
    'host': 'localhost',
    'database': 'stu',
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
              'course_name': '课程名', 'credits': '学分', 'hours': '学时', 'teacher': '授课教师'
    , 'exam_time': '考试时间', 'exam_location': '考试地点', 'semester': '开课学期',
              'major_id': '专业编号', 'major_name': '专业名称',
              'major_record_id': '变更记录id', 'previous_major_id': '变更前专业编号',
              'current_major_id': '变更后专业编号',
              'change_date': '变更日期', 'name': '姓名', 'gender': '性别', 'age': '年龄', 'birthdate': '出生日期',
              'hometown': '籍贯',
              'enrollment_date': '入学日期', 'previous_major_name': '变更前专业名称', 'current_major_name': '变更后专业名称'

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


def render_sheet(header, headername, data, deletable, editable):
    return render_template('sheet.html', headername=headername, header=header, data=data, deletable=deletable,
                           editable=editable)


def get_header_and_types(Description):
    header = [col[0] for col in Description]
    isInt = ['int' in str(col[1]) for col in Description]
    isFloat = ['float' in str(col[1]) for col in Description]
    isDate = ['date' in str(col[1]) for col in Description]
    colType = list(zip(isInt, isFloat, isDate))
    return header, colType


@app.route('/table')
def table():
    cursor = cnx.cursor()
    cursor.execute("describe student_info")
    Description = cursor.fetchall()

    query = 'select * from student_info'
    cursor.execute(query)
    data = cursor.fetchall()

    header, colType = get_header_and_types(Description)
    # header = [col[0] for col in Description]
    # isInt = ['int' in str(col[1]) for col in Description]
    # isFloat = ['float' in str(col[1]) for col in Description]
    # isDate = ['date' in str(col[1]) for col in Description]
    # colType = list(zip(isInt, isFloat, isDate))

    cursor.execute('select * from class')
    classes = cursor.fetchall()
    class_ids = [clazz[0] for clazz in classes]
    classes = ['\t'.join(map(str, clazz)) for clazz in classes]
    classes = dict(zip(class_ids, classes))
    # print(classes)

    cursor.execute('select * from major')
    majors = cursor.fetchall()
    major_ids = [major[0] for major in majors]
    majors = ['\t'.join(map(str, major)) for major in majors]
    majors = dict(zip(major_ids, majors))

    sheet_html = render_sheet(header, headername, data, deletable=True, editable=True)

    return render_template('table.html', sheet_html=sheet_html, header=header, headername=headername, colType=colType,
                           zip=zip, majors=majors, classes=classes)


@app.route('/major')
def major():
    cursor = cnx.cursor()
    cursor.execute("describe major")
    Description = cursor.fetchall()
    query = 'select * from major'
    cursor.execute(query)
    data = cursor.fetchall()

    header, colType = get_header_and_types(Description)

    sheet_html = render_sheet(header, headername, data, deletable=False, editable=True)

    return render_template('major.html', sheet_html=sheet_html, header=header, headername=headername, colType=colType,
                           zip=zip)


@app.route('/majorchange')
def majorchange():
    cursor = cnx.cursor()
    cursor.execute("describe major_change_info")
    Description = cursor.fetchall()
    query = 'select * from major_change_info'
    cursor.execute(query)
    data = cursor.fetchall()

    header, colType = get_header_and_types(Description)

    sheet_html = render_sheet(header, headername, data, deletable=False, editable=False)

    return render_template('majorchange.html', sheet_html=sheet_html, header=header, headername=headername,
                           colType=colType,
                           zip=zip)


@app.route('/coursemanage')
def coursemanage():
    cursor = cnx.cursor()
    cursor.execute("describe coursemanagement")
    Description = cursor.fetchall()
    query = 'select * from coursemanagement'
    cursor.execute(query)
    data = cursor.fetchall()

    header, colType = get_header_and_types(Description)

    sheet_html = render_sheet(header, headername, data, deletable=False, editable=True)

    return render_template('coursemanage.html', sheet_html=sheet_html, header=header, headername=headername,
                           colType=colType,
                           zip=zip)


@app.route('/coursegrades')
def coursegrades():
    cursor = cnx.cursor()
    cursor.execute("describe grade_info")
    Description = cursor.fetchall()
    query = 'select * from grade_info'
    cursor.execute(query)
    data = cursor.fetchall()

    header, colType = get_header_and_types(Description)

    sheet_html = render_sheet(header, headername, data, deletable=True, editable=True)

    return render_template('coursegrades.html', sheet_html=sheet_html, header=header, headername=headername,
                           colType=colType,
                           zip=zip)


def create_mysql_search(formData, tableName):
    sortItem = formData['sortItem']
    sortDirect = formData['sortDirect']
    del formData['sortItem']
    del formData['sortDirect']
    query = 'SELECT * FROM ' + tableName + ' WHERE 1 = 1 '
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
            # query = query + " and %s = '%s' " % (key, formData[key])
            query = query + " and %s like '%%%s%%' " % (key, formData[key])

    if sortItem != 'default':
        query = query + ' ORDER BY ' + sortItem + " " + sortDirect

    return query


@app.route('/get-table-data', methods=['POST'])
def get_table_data():
    formData = dict(request.form)
    print(formData)
    tableName = ''
    deletable = True
    keys = formData.keys()
    if 'major_record_id' in keys:
        tableName = 'major_change_info'
        deletable = False
        editable = False
    elif 'grade_record_id' in keys:
        tableName = 'grade_info'
        deletable = True
        editable = True
    elif 'name' in keys:
        tableName = 'student_info'
        deletable = True
        editable = True
    elif 'major_name' in keys:
        deletable = False
        tableName = 'major'
        editable = True
    elif 'course_name' in keys:
        tableName = 'coursemanagement'
        deletable = False
        editable = True
    cursor = cnx.cursor()
    query = create_mysql_search(formData, tableName)
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    header = [col[0] for col in cursor.description]
    return render_sheet(header, headername, data, deletable, editable)


@app.route('/edit-table', methods=['POST'])
def edit_table():
    editData = dict(request.form)
    print(editData)
    keys = editData.keys()
    cursor = cnx.cursor()
    args = list(editData.values())
    status = ''
    args.append(status)
    if 'gender' in keys:
        status = cursor.callproc('editstu', args=args)
    elif 'major_name' in keys:
        status = cursor.callproc('editmajor', args=args)
    elif 'course_name' in keys:
        status = cursor.callproc('editcm', args=args)

    status = status[-1]
    if status:
        return 'OK'
    else:
        return '不OK'


@app.route('/insert-table', methods=['POST'])
def insert_table():
    insertData = dict(request.form)
    print(insertData)
    keys = insertData.keys()
    cursor = cnx.cursor()
    args = list(insertData.values())
    status = ''
    args.append(status)
    if 'gender' in keys:
        results = cursor.callproc('insertstu', args=args)
    elif 'major_name' in keys:
        results = cursor.callproc('insertmajor', args=args)
    elif 'course_name' in keys:
        results = cursor.callproc('insertcm', args=args)
    elif 'grade' in keys:
        results = cursor.callproc('insertcg', args=args)

    status = results[-1]
    if status:
        return 'OK'
    else:
        return '不OK'


@app.route('/get-one-info', methods=['POST'])
def get_one_info():
    cursor = cnx.cursor()
    requ = request.get_json()
    print(requ)
    tableName = ''
    if 'student_id' in requ:
        tableName = 'student_info'
        row_id = requ['student_id']
        primes = ['student_id']
    elif 'major_id' in requ:
        tableName = 'major'
        row_id = requ['major_id']
        primes = ['major_id']
    elif 'course_id' in requ:
        tableName = 'coursemanagement'
        row_id = requ['course_id']
        primes = ['course_id']
    cursor.execute('desc ' + tableName)
    Description = cursor.fetchall()
    header = [col[0] for col in Description]
    query = "SELECT * from %s where %s = '%s' " % (tableName, header[0], row_id)
    print(query)
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

    response_obj = {
        "info": data,
        "primes": primes
    }
    response_text = jsonify(response_obj)
    return response_text


@app.route('/delete-one', methods=['POST'])
def delete_one():
    requ = request.get_json()
    print(requ)
    cursor = cnx.cursor()
    if 'student_id' in requ:
        row_id = requ['student_id']
        print(row_id)
        status = cursor.callproc('delstu', args=(row_id, ''))

    if status[-1]:
        return 'OK'
    else:
        return '不OK'


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


@app.route('/select-stu', methods=['POST'])
def render_select():
    cursor = cnx.cursor()
    requ = request.get_json()
    sid = requ['student_id']
    print(sid)
    if sid == '':
        query = ''
    else:
        query = " where student_id like '%%%s%%' " % sid
    print(query)
    cursor.execute('select student_id, name from student_info ' + query)
    students = cursor.fetchall()
    sids = [clazz[0] for clazz in students]
    students = ['\t'.join(map(str, clazz)) for clazz in students]
    students = dict(zip(sids, students))
    return render_template('selector_stu.html', students=students)


@app.route('/select-course', methods=['POST'])
def render_course():
    cursor = cnx.cursor()
    requ = request.get_json()
    sid = requ['course_id']
    print(sid)
    if sid == '':
        query = ''
    else:
        query = " where course_id like '%%%s%%' " % sid
    print(query)
    cursor.execute('select course_id, course_name from coursemanagement ' + query)
    courses = cursor.fetchall()
    sids = [clazz[0] for clazz in courses]
    courses = ['\t'.join(map(str, clazz)) for clazz in courses]
    courses = dict(zip(sids, courses))
    return render_template('selector_course.html', courses=courses)


@app.route('/contact', )
def contact():
    return render_template('contact.html', header=[1, 2, 3, 4, 5])


if __name__ == '__main__':
    app.run(host='0.0.0.0')
