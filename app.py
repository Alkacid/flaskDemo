import mysql.connector
from flask import Flask, render_template, request, redirect

config = {
    'user': 'root',
    'password': '+654',
    'host': 'localhost',
    'database': 'lab1',
    'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)
app = Flask(__name__)


# 在 Web 应用程序中呈现数据
@app.route('/table')
def index():
    cursor = cnx.cursor()

    query = "describe book"
    cursor.execute(query)
    header = [col[0] for col in cursor.fetchall()]

    query = "SELECT * FROM book"
    cursor.execute(query)
    data = cursor.fetchall()
    # print(data)
    # 确定表的长度和宽度

    return render_template('table.html', header=header, data=data)


@app.route('/table/sort', methods=['POST'])
def sort_by():
    if request.method == 'POST':
        # cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sortby = request.form['sortby']
        direct = request.form['direct']
        cursor.execute("SELECT * FROM book ORDER BY " + sortby + " " + direct)
        data = cursor.fetchall()
        query = "describe book"
        cursor.execute(query)
        header = [col[0] for col in cursor.fetchall()]
        print(data)
        print(header)
        return render_template('table.html', data=data, header=header)


from flask import jsonify


# 新路由/get-table-data，用于返回JSON格式的表格数据
@app.route('/get-table-data')
def get_table_data():
    cursor = cnx.cursor()
    sortby = request.args.get('sortby', '')
    direct = request.args.get('direct', '')  # 从请求获取搜索值参数
    if sortby == 'default':
        print('deeeeeefault')
        cursor.execute("SELECT * FROM book")
    else:
        cursor.execute("SELECT * FROM book ORDER BY " + sortby + " " + direct)
    rows = cursor.fetchall()
    print(jsonify(rows).data)
    # Return table data as JSON
    return jsonify(rows)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == 'qwer' or True:
            return redirect('/table')

    else:
        return render_template('home.html')


@app.route('/contact', )
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    # test_1()
    app.run(host='0.0.0.0')
