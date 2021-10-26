import time
import main
import pandas as pd
import pymysql.cursors
import pymysql.err
import settings

def conects(sql):
    try:
        connection = pymysql.connect(host=settings.host,
                                     user=settings.user,
                                     password=settings.password,
                                     database=settings.database,
                                     cursorclass=pymysql.cursors.DictCursor,
                                     autocommit=True)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            connection.close()
            return result
    except pymysql.connect.Error as error:
        main.errors(str(error))
        return 'not ok'

def view_details(number):
    if not number.isdigit():
        return 'введите целое числовое значение'
    sql = f"SELECT id, name as 'деталь', id_diam as 'диаметр заготовки', length_detaly as 'длина заготовки' from detaly where id = {number};"
    result = conects(sql)
    sql1 = f"select time_work.id_operation as '№ операции', " \
               f"operation.name_operation as ' ', time_work.works_time as 'время' " \
               f"from time_work join operation on operation.znach = time_work.id_operation where id_detaly = {number};"
    result1 = conects(sql1)
    return 'не существующая деталь' if result == None else result, result1


def inserts(id_name_worker, id_detaly, id_operation, tune, count_detaly, setting, comment_s, time_stop, y):
    if y == 0:
        sql = f"INSERT into smena(id_name_worker, id_detaly, id_operation, tune, count_detaly, " \
              f"setting, commentars, time_stop) values({id_name_worker}, {id_detaly}, {id_operation}, {tune}, " \
              f"{count_detaly}, {setting}, '{comment_s}', {time_stop});"
    else:
        sql = f"update smena set id_name_worker={id_name_worker}, id_detaly={id_detaly}, " \
              f"id_operation={id_operation}, tune={tune}, count_detaly={count_detaly}, setting={setting}, commentars='{comment_s}', time_stop={time_stop} where id = {y};"
    x = conects(sql)
    if x == 'not ok':
        pass
    else:
        return 'успешно записано'


def updates(date):
    sql = f"SELECT smena.id as '№'," \
          f" workers.name as 'исполнитель', " \
          f"detaly.name as 'деталь', " \
          f"id_operation as 'операция', tune as 'брак', " \
          f"count_detaly as 'кол-во', setting as 'наладка', commentars as 'комментарий', time_stop as 'простой',  controll as 'проверено' " \
          f"from smena join workers on smena.id_name_worker = workers.id join detaly on detaly.id = smena.id_detaly " \
          f"where date(smena.date_change)= '{date[0]}-{date[1]}-{date[2]}';"
    result = conects(sql)
    return result

def workers():
    sql = "select id, name from workers;"
    result = pd.DataFrame(conects(sql), columns=['id', 'name'])
    return result


def controll(list_number, password):
    sql = "select name, password_to_name from passwords;"
    result = conects(sql)
    for i in result:
        if i['password_to_name'] == password:
            n = i["name"]
            for j in list_number:
                sql = f'update smena set controll="{n}" where id={j};'
                conects(sql)
            return 'изменения приняты'
    return 'пароль неверный'



def chars(password, number):
    sql = "select name, password_to_name from passwords;"
    result = conects(sql)
    for i in result:
        if i['password_to_name'] == password:
            n = i["name"]
            try:
                sql = f'update smena set change_data="{n}" where id={number};'
                conects(sql)
            except pymysql.Error as error:
                # print(error)
                return 2
            sql = f"select id_name_worker, id_detaly, id_operation, tune, setting, count_detaly, time_stop, commentars from smena where id={number};"
            result = conects(sql)
            return result
    return 1

