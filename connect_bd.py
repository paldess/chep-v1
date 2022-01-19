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


def inserts(id_name_worker, id_detaly, id_operation, tune, count_detaly, setting, comment_s, time_stop, night, setting_work, y):
    setting_work = setting_work if id_operation <= 50 and id_operation >= 35 else 0
    sql = f'SELECT time_work.works_time from time_work where id_detaly = {id_detaly} and id_operation ={id_operation};'
    if len(conects(sql))==0:
        return 'нет таких операций '
    if y == 0:
        sql = f"INSERT into smena(id_name_worker, id_detaly, id_operation, tune, count_detaly, " \
              f"setting, commentars, time_stop, night_works, setting_work) values({id_name_worker}, {id_detaly}, {id_operation}, {tune}, " \
              f"{count_detaly}, {setting}, '{comment_s}', {time_stop}, {night}, {setting_work});"
    else:
        sql = f"update smena set id_name_worker={id_name_worker}, id_detaly={id_detaly}, " \
              f"id_operation={id_operation}, tune={tune}, count_detaly={count_detaly}, setting={setting}, commentars='{comment_s}', time_stop={time_stop}, night_works={night}, setting_work={setting_work} where id = {y};"
    x = conects(sql)
    if x == 'not ok':
        return 'не записано. ошибка'
    else:
        return 'успешно записано'


def updates(date):
    sql = f"SELECT smena.id as '№'," \
          f" workers.name as 'исполнитель', " \
          f"detaly.name as 'деталь', " \
          f"id_operation as 'операция', tune as 'брак', " \
          f"count_detaly as 'кол-во', setting as 'наладка', commentars as 'комментарий', time_stop as 'простой',  controll as 'проверено', night_works as 'ночная смена' " \
          f"from smena join workers on smena.id_name_worker = workers.id join detaly on detaly.id = smena.id_detaly " \
          f"where date(smena.date_change)= '{date[0]}-{date[1]}-{date[2]}';"
    result = conects(sql)
    return result

def workers():
    sql = "select id, name from workers;"
    result = conects(sql)
    return result


def controll(list_number, password):
    sql = "select name, password_to_name from passwords;"
    result = conects(sql)
    sql = f'select id from smena where id in {list_number};'
    result_number = conects(sql)
    if result != 'not ok' and result_number != 'not ok':
        for i in result:
            if i['password_to_name'] == password:
                n = i["name"]
                if len(list_number) == 0:
                    return 'нет просмотренных результатов'
                for j in list_number:
                    sql = f'update smena set controll="{n}" where id={j};'
                    conects(sql)
                return f'строки {str([i["id"] for i in result_number]).replace("[", "").replace("]", "")} подтверждены'
        return 'неверный пароль'
    else:
        return ' неверный № записи или нет подключения'


def chars(password, number):
    sql = "select name, password_to_name from passwords;"
    result = conects(sql)
    if result != 'not ok':
        for i in result:
            if i['password_to_name'] == password:
                n = i["name"]
                sql = f'update smena set change_data="{n}" where id={number};'
                conects(sql)
                sql = f"select id_name_worker, id_detaly, id_operation, tune, setting, count_detaly, time_stop, commentars, night_works from smena where id={number};"
                result = conects(sql)
                return result
        return 1
    else:
        return 2

def view_data_works_bd(on_to, to_to, id, to_time):
    sql = f'select name as "исполнитель" from workers where id = {id}'
    name = conects(sql)
    if len(name) == 0:
        return 1, 1, 1, 1, 1, 1, 1
    elif to_time == True:
        sql = "select  SUM(time_work.works_time*smena.count_detaly) as 'общее время ночных, мин' from smena " \
              "join time_work on time_work.id_operation = smena.id_operation " \
              f"where smena.night_works=1 and smena.id_name_worker = {id} and smena.id_detaly=time_work.id_detaly and smena.date_change between date('{on_to}') and DATE_ADD('{to_to}', INTERVAL 1 DAY);"
        data = conects(sql)
        sql = "select  SUM(time_work.works_time*smena.count_detaly) as 'общее время дневных, мин' from smena " \
              "join time_work on time_work.id_operation = smena.id_operation " \
              f"where smena.night_works=0 and smena.id_name_worker = {id} and smena.id_detaly=time_work.id_detaly and smena.date_change between date('{on_to}') and DATE_ADD('{to_to}', INTERVAL 1 DAY);"
        data1 = conects(sql)
        sql = "select SUM(smena.time_stop) as 'общее время простоев, мин' from smena " \
              f"where id_name_worker = {id} and id_detaly = 1 and date_change between date('{on_to}') and DATE_ADD('{to_to}', INTERVAL 1 DAY);"
        data2 = conects(sql)
        sql = "select  SUM(setting) as 'кол-во наладок' from smena " \
              f"where id_name_worker = {id} and date_change between date('{on_to}') and DATE_ADD('{to_to}', INTERVAL 1 DAY);"
        data3 = conects(sql)
        sql = "select  SUM(setting_work) as 'инструментов налажено' from smena " \
              f"where id_name_worker = {id} and date_change between date('{on_to}') and DATE_ADD('{to_to}', INTERVAL 1 DAY);"
        data4 = conects(sql)
        sql = "select SUM(smena.time_stop) as 'общее время работы без ID детали, мин' from smena " \
              f"where id_name_worker = {id} and id_detaly = 0 and date_change between date('{on_to}') and DATE_ADD('{to_to}', INTERVAL 1 DAY);"
        data_not_id = conects(sql)
        return name, data, data1, data2, data3, data4, data_not_id
    else:
        # sql = "select detaly.name as 'деталь',  smena.id_operation as 'операция', smena.count_detaly as 'кол-во', smena.time_stop as 'простой станка', smena.date_change as 'дата' from smena " \
        #       "join detaly on smena.id_detaly = detaly.id " \
        #       f"where smena.date_change between '{on_to}' and DATE_ADD('{to_to}', INTERVAL 1 DAY) and smena.id_name_worker = {id};"
        sql = "select smena.id_detaly as 'ID детали', detaly.name as 'деталь', operation.name_operation as 'операция', smena.id_operation as 'номер операции', " \
              "time_work.works_time as 'время операции, мин', smena.tune as 'брак', smena.setting as 'наладка', smena.setting_work as 'инструментов в наладке'," \
              "smena.count_detaly as 'кол-во', smena.time_stop as 'простой станка', smena.controll as 'контроллер', smena.commentars as 'комментарий', " \
              "smena.date_change as 'дата'	from smena join detaly on smena.id_detaly = detaly.id join time_work on smena.id_detaly = time_work.id_detaly and smena.id_operation = time_work.id_operation " \
              f"join operation on operation.znach = smena.id_operation where smena.date_change between '{on_to}' and DATE_ADD('{to_to}', INTERVAL 1 DAY) and smena.id_name_worker = {id};"
        data = conects(sql)
        return name, data, 1, 1, 1, 1, 1
