import pymysql
import requests
import schedule
import time
import datetime
import matplotlib.pyplot as plt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.image import MIMEImage

url = "http://192.168.10.10//tar1090/chunks/chunks.json"

get_chunkjson = requests.get(url)

plane_file_list = []
id_list = []
real_num = []
planeNum = 0
messageNum = 0


def write_db(planeNum, messageNum):
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='168168',
                         database='plane')

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    print(type(today))
    # SQL 插入语句
    sql = 'INSERT INTO total(date,planeNum,messageNum) VALUES ("' + today + '","' + str(planeNum) + '","' + str(messageNum) + '");'

    print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 如果发生错误则回滚
        db.rollback()
        print(db.rollback())
    # 关闭不使用的游标对象
    cursor.close()
    # 关闭数据库连接
    db.close()

    get_img()


def get_img():
    day_list = []
    planenum_list = []
    messagenum_list = []
    # 打开数据库连接
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='168168',
                         database='plane')

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    for i in range(0, 8):

        # SQL 查询语句
        sql = "select * from total where TO_DAYS(date) = TO_DAYS(NOW())-" + str(i)

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表,以元组来存储
            results = cursor.fetchall()
            day_list.append(results[0][0])
            planenum_list.append(int(results[0][1]))
            messagenum_list.append(int(results[0][2]))
        except:
            print("错误：没有查找到数据")

    # 关闭不使用的游标对象
    cursor.close()
    # 关闭数据库连接
    db.close()

    # 画布
    plt.figure(figsize=(10, 5), dpi=100)
    # plt1
    x = day_list
    y1 = planenum_list
    plt.subplot(1, 2, 1)
    plt.xticks(rotation=45)  # 横坐标的数据旋转45°
    plt.plot(x, y1)
    plt.title("planeNum")
    for a, b in zip(x, y1):
        plt.text(a, b, b, ha='center', va='bottom', fontsize=8)

    # plt2
    x = day_list
    y2 = messagenum_list
    print(type(y2[0]))
    plt.subplot(1, 2, 2)
    plt.xticks(rotation=45)  # 横坐标的数据旋转45°
    plt.plot(x, y2)
    plt.title("msgNum")

    for a, b in zip(x, y2):
        plt.text(a, b, b, ha='center', va='bottom', fontsize=8)

    plt.suptitle("7 days data")

    f = plt.gcf()  # 获取当前图像
    f.savefig('./1.jpg')
    f.clear()  # 释放内存

    send_message()


def send_message():

    mail_host = "smtp.163.com"  # SMTP服务器地址
    mail_sender = "wpj1999@163.com"  # 账号
    mail_passwd = "QFYAWBNDMHYFADDO"  # 密码

    msg = MIMEMultipart('related')

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")

    msg["Subject"] = str(today)
    msg["From"] = mail_sender  # 发送人
    msg["To"] = "1241996582@qq.com"  # 接收人

    # html格式的邮件正文
    content = '''
    <body>
    <p>图片如下：</p>
    <p><img src="cid:testimage" alt="testimage"></p>
    </body>
    '''
    msg.attach(MIMEText(content, 'html', 'utf-8'))

    # 读取图片
    fp = open('./1.jpg', 'rb')  # 打开文件
    msgImage = MIMEImage(fp.read())  # 读入 msgImage 中
    fp.close()  # 关闭文件

    # 定义图片 ID，在 HTML 文本中引用
    msgImage.add_header('Content-ID', 'testimage')
    msg.attach(msgImage)

    ## 发送邮件
    s = smtplib.SMTP()  # 实例化对象
    s.connect(mail_host, 25)  # 连接163邮箱服务器，端口号为25
    s.login(mail_sender, mail_passwd)  # 登录邮箱
    s.sendmail(mail_sender, ["1241996582@qq.com"], msg.as_string())
    s.quit()


def get_info():
    for i in get_chunkjson.json()['chunks']:
        plane_file_list.append(i)
    plane_file_list.remove('current_large.gz')
    plane_file_list.remove('current_small.gz')

    for i in plane_file_list:
        try:
            url = "http://192.168.10.10//tar1090/chunks/" + i

            chunk_json = requests.get(url)

            global messageNum
            for k in chunk_json.json()['files']:
                messageNum += k['messages']

            for l in chunk_json.json()['files']:
                aircraft_list = l['aircraft']

                for m in aircraft_list:
                    id = m[0]
                    if id not in id_list:
                        if m[4] and m[5]:
                            id_list.append(id)

        except:
            pass
    write_db(len(id_list), messageNum)


schedule.every().day.at('15:12').do(get_info)

while True:
    schedule.run_pending()
    time.sleep(10)