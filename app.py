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

cnx = mysql.connector.connect(**config)
app = Flask(__name__)
root = False
usernow = 0
headername = {'record_id': '记录ID', 'student_id': '学号', 'reason': '奖惩原因', 'type': '奖惩类型',
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


def render_sheet(header, headername, data, deletable, editable):
    return render_template('sheet.html', headername=headername, header=header, data=data, deletable=deletable,
                           editable=editable, root=root)


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
    header, colType = get_header_and_types(Description)
    if root:
        query = 'select * from student_info'
        cursor.execute(query)
        data = cursor.fetchall()

        cursor.execute('select * from class')
        classes = cursor.fetchall()
        class_ids = [clazz[0] for clazz in classes]
        classes = ['\t'.join(map(str, clazz)) for clazz in classes]
        classes = dict(zip(class_ids, classes))
        # print(classes)

        cursor.execute('select * from major')
        majors = cursor.fetchall()
        major_ids = [m[0] for m in majors]
        majors = ['\t'.join(map(str, m)) for m in majors]
        majors = dict(zip(major_ids, majors))

        sheet_html = render_sheet(header, headername, data, deletable=True, editable=True)

        return render_template('table.html', sheet_html=sheet_html, header=header, headername=headername,
                               colType=colType,
                               zip=zip, majors=majors, classes=classes, usernow=usernow)

    else:
        query = 'select * from student_info where student_id= ' + usernow
        cursor.execute(query)
        data = list(cursor.fetchone())
        return render_template('self_info.html', header=header, colType=colType, data=data, headername=headername,
                               zip=zip, usernow=usernow)


@app.route('/major')
def major():
    cursor = cnx.cursor()
    cursor.execute("describe major")
    Description = cursor.fetchall()
    query = 'select * from major'
    cursor.execute(query)
    data = cursor.fetchall()

    header, colType = get_header_and_types(Description)
    if root:
        deletable = False
        editable = True
    else:
        deletable = False
        editable = False

    sheet_html = render_sheet(header, headername, data, deletable=deletable, editable=editable)

    return render_template('major.html', sheet_html=sheet_html, header=header, headername=headername, colType=colType,
                           zip=zip, root=root, usernow=usernow)


@app.route('/majorchange')
def majorchange():
    cursor = cnx.cursor()
    cursor.execute("describe major_change_info")
    Description = cursor.fetchall()
    if root:
        query = 'select * from major_change_info'
    else:
        query = 'select * from major_change_info where student_id= ' + usernow
    cursor.execute(query)
    data = cursor.fetchall()

    header, colType = get_header_and_types(Description)

    sheet_html = render_sheet(header, headername, data, deletable=False, editable=False)

    return render_template('majorchange.html', sheet_html=sheet_html, header=header, headername=headername,
                           colType=colType, root=root,
                           zip=zip, usernow=usernow)


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
                           colType=colType, root=root,
                           zip=zip, usernow=usernow)


@app.route('/coursegrades')
def coursegrades():
    cursor = cnx.cursor()
    cursor.execute("describe grade_info")
    Description = cursor.fetchall()
    if root:
        query = 'select * from grade_info'
        deletable = True
        editable = True
    else:
        query = 'select * from grade_info where student_id = ' + usernow
        deletable = True
        editable = False
    cursor.execute(query)
    data = cursor.fetchall()

    header, colType = get_header_and_types(Description)

    sheet_html = render_sheet(header, headername, data, deletable=deletable, editable=editable)

    return render_template('coursegrades.html', sheet_html=sheet_html, header=header, headername=headername,
                           colType=colType, root=root,
                           zip=zip, usernow=usernow)


@app.route('/awards')
def awards():
    cursor = cnx.cursor()
    cursor.execute("describe awards_info")
    Description = cursor.fetchall()
    if root:
        query = 'select * from awards_info'
        deletable = True
        editable = True
    else:
        query = 'select * from awards_info where student_id= ' + usernow
        deletable = False
        editable = False
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()

    header, colType = get_header_and_types(Description)

    sheet_html = render_sheet(header, headername, data, deletable=deletable, editable=editable)

    return render_template('awards.html', sheet_html=sheet_html, header=header, headername=headername,
                           colType=colType, root=root,
                           zip=zip, usernow=usernow)


def create_mysql_search(formData, tableName, stu=''):
    sortItem = formData['sortItem']
    sortDirect = formData['sortDirect']
    del formData['sortItem']
    del formData['sortDirect']
    query = 'SELECT * FROM ' + tableName
    query = query + (' WHERE 1 = 1 ' if stu == '' else (' where student_id=%s  ' % stu))
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
        query = query + ' ORDER BY convert( ' + sortItem + " using GBK) " + sortDirect

    return query


@app.route('/get-table-data', methods=['POST'])
def get_table_data():
    formData = dict(request.form)
    # print(formData)
    tableName = ''
    deletable = True
    keys = formData.keys()
    stu = ''
    if 'major_record_id' in keys:  # 专业变更
        tableName = 'major_change_info'
        deletable = False
        editable = False
        stu = '' if root else usernow
    elif 'grade_record_id' in keys:  # 成绩和选课
        tableName = 'grade_info'
        deletable = True
        editable = True if root else False
        stu = '' if root else usernow
    elif 'record_id' in keys:  # 奖惩信息
        tableName = 'awards_info'
        deletable = True if root else False
        editable = True if root else False
        stu = '' if root else usernow
    elif 'name' in keys:  # 学生信息
        tableName = 'student_info'
        deletable = True
        editable = True
    elif 'major_name' in keys:  # 专业信息
        deletable = False
        tableName = 'major'
        editable = True if root else False
    elif 'course_name' in keys:  # 课程信息
        tableName = 'coursemanagement'
        deletable = False
        editable = True
    cursor = cnx.cursor()
    query = create_mysql_search(formData, tableName, stu)
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
    elif 'grade' in keys:
        status = cursor.callproc('editcg', args=args)
    elif 'reason' in keys:
        status = cursor.callproc('editaward', args=args)
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
    elif 'reason' in keys:
        results = cursor.callproc('insertaward', args=args)

    status = results[-1]
    if status:
        return 'OK'
    else:
        return '不OK'


@app.route('/add-course', methods=['POST'])
def add_course():
    cursor = cnx.cursor()
    requ = request.get_json()
    course_id = requ['course_id']
    args = [usernow, course_id, 0, '']
    results = cursor.callproc('insertcg', args=args)
    status = results[-1]
    if status:
        return 'OK'
    else:
        return '该课已被选中'


@app.route('/get-one-info', methods=['POST'])
def get_one_info():
    cursor = cnx.cursor()
    requ = request.get_json()
    # print(requ)
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
    elif 'grade_record_id' in requ:
        tableName = 'grade_info'
        row_id = requ['grade_record_id']
        primes = ['grade_record_id', 'student_id', 'course_id']
    elif 'record_id' in requ:
        tableName = 'awards_info'
        row_id = requ['record_id']
        primes = ['record_id', 'student_id']
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
        # print(row_id)
        status = cursor.callproc('delstu', args=(row_id, ''))
    elif 'grade_record_id' in requ:
        row_id = requ['grade_record_id']
        status = cursor.callproc('delcg', args=(row_id, ''))
    elif 'record_id' in requ:
        row_id = requ['record_id']
        status = cursor.callproc('delaward', args=(row_id, ''))

    if status[-1]:
        return 'OK'
    else:
        return '不OK'


@app.route('/select-stu', methods=['POST'])
def render_select():
    cursor = cnx.cursor()
    requ = request.get_json()
    sid = requ['student_id']
    # print(sid)
    if sid == '' or "'" in sid:
        query = ''
    else:
        query = " where student_id like '%%%s%%' or name like '%%%s%%' " % (sid, sid)
    # print(query)
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
    # print(sid)
    if sid == '' or "'" in sid:
        query = ''
    else:
        query = " where course_id like '%%%s%%' or course_name like '%%%s%%' " % (sid, sid)
    # print(query)
    cursor.execute('select course_id, course_name from coursemanagement ' + query)
    courses = cursor.fetchall()
    sids = [clazz[0] for clazz in courses]
    courses = ['\t'.join(map(str, clazz)) for clazz in courses]
    courses = dict(zip(sids, courses))
    return render_template('selector_course.html', courses=courses)


@app.route('/contact', )
def contact():
    return render_template('contact.html', header=[1, 2, 3, 4, 5])


def create_mysql_chart(formData, tableName, stu=''):
    sortItem = formData['sortItem']
    sortDirect = formData['sortDirect']
    del formData['sortItem']
    del formData['sortDirect']
    query = '''SELECT count(case when grade between 1 and 59 then 1 end) ,
            count(case when grade between 60 and 69 then 1 end),
            count(case when grade between 70 and 79 then 1 end),
            count(case when grade between 80 and 89 then 1 end),
            count(case when grade between 90 and 100 then 1 end)
 FROM ''' + tableName
    query = query + (' WHERE 1 = 1 ' if stu == '' else (' where student_id=%s  ' % stu))
    for key in formData.keys():
        if formData[key] == '':
            continue
        query = query + " and %s like '%%%s%%' " % (key, formData[key])

    return query


@app.route('/get-chart-data', methods=['POST'])
def get_chart_data():
    formData = dict(request.form)
    cursor = cnx.cursor()
    stu = '' if root else usernow
    query = create_mysql_chart(formData, 'grade_info', stu)
    print(query)
    cursor.execute(query)
    data = list(cursor.fetchone())
    print(data)
    return jsonify(data)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = cnx.cursor()

        cursor.execute("select * from user where username = '%s'  " % username)
        res = cursor.fetchone()
        if res:
            return render_template('register.html', error_msg='用户已被注册')

        cursor.execute("select * from student_info where student_id= '%s'  " % username)
        res = cursor.fetchall()
        if not bool(res):
            return render_template('register.html', error_msg='无学生信息')

        # 生成唯一的 salt 值
        salt = os.urandom(16).hex()
        hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

        cursor.execute(
            "INSERT INTO user (username, password, salt) VALUES ( '%s', '%s', '%s');" % (username, hashed_password,
                                                                                         salt))
        cnx.commit()
        cursor.close()
        return redirect('/')
    else:
        return render_template('register.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    global root
    global usernow
    # return redirect('/coursegrades')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = cnx.cursor()
        query = "SELECT * FROM user WHERE username= '%s'" % username
        print(query)
        cursor.execute(query)
        user = cursor.fetchone()

        # print(user, end=' ')
        if user:
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, user))
            salt = user['salt']
            hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
            if hashed_password == user['password']:
                if user['root']:
                    root = True
                else:
                    root = False
                usernow = username
                # print(root)
                return redirect('/table')

        return render_template('login.html', error_msg='登录失败，请检查用户名和密码是否正确')

    return render_template('login.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
