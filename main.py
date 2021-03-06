import sys  # sys нужен для передачи argv в QApplication
import time
import threading
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
import pandas as pd
from window import Ui_MainWindow  # Это наш конвертированный файл дизайна
import connect_bd
from datetime import date


def errors(r):
    msg = QMessageBox()
    msg.setText(r)
    # msg.setInformativeText('Проверьте введенные параметры')
    msg.setWindowTitle("Ошибка")
    msg.exec()




class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    del_cod = ["'", "Decimal", "')}", '(', '[', ']', ')', '}', ',']

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.view_data_detaly.clicked.connect(self.view_s)
        self.ok_worker.clicked.connect(self.insert_smena)
        self.workers.setText(connect_bd.workers().to_string(header=False, index=False, col_space=20))
        self.view_day.clicked.connect(self.calender_view)
        self.calendar.setDate(date.today())
        self.ok_go.clicked.connect(self.controllas)
        self.go.clicked.connect(self.change)
        self.y = 0
        self.pushButton.clicked.connect(self.clearing)
        self.progressBar.setValue(int(1))

    def view_s(self):
        x = str(connect_bd.view_details(self.id_detail_view.text())).replace('{', '\n')
        for i in self.del_cod:
            x = x.replace(f'{i}', '')
        self.view_window.setText(x)

    def insert_smena(self):
        if self.id_worker.text().isdigit() and self.id_detail.text().isdigit() \
                and self.id_operation.text().isdigit() and self.brak.text().isdigit() \
                and self.count_detail.text().isdigit() and self.time_stop.text().isdigit():
            if int(self.time_stop.text()) > 0 and int(self.count_detail.text()) > 0:
                errors('нельзя указывать и простой и детали одновременно')
            else:
                id_name_worker = int(self.id_worker.text())
                id_detaly = int(self.id_detail.text())
                id_operation = int(self.id_operation.text())
                tune = int(self.brak.text())
                count_detaly = int(self.count_detail.text())
                setting = bool(self.setting.isChecked())
                comment_s = self.lineEdit.text() if self.lineEdit.text() != '' else 'отсутствует'
                time_stop = self.time_stop.text()
                x = connect_bd.inserts(id_name_worker, id_detaly, id_operation, tune, count_detaly, setting, comment_s, time_stop, self.y)
                if self.y != 0:
                    self.clearing()
                self.y = 0
                msg = QMessageBox()
                msg.setText(x)
                msg.exec()
        else:
            errors("Неверные данные!")

    def clearing(self):
        self.id_worker.clear()
        self.id_detail.clear()
        self.id_operation.clear()
        self.count_detail.clear()
        self.brak.setText(str(0))
        self.time_stop.setText(str(0))
        self.lineEdit.clear()
        self.setting.setChecked(0)

    def calender_view(self):
        self.tableWidget.clear()
        x = self.calendar.date()
        dates = [x.year(), x.month(), x.day()]
        zapros = connect_bd.updates(dates)
        zapros_1 = pd.DataFrame(zapros, columns=['№', 'исполнитель', 'деталь', 'операция', 'брак', 'кол-во', 'наладка', 'комментарий', 'простой', 'проверено'])
        self.numbers_view = zapros_1['№'].to_list()
        headers = zapros_1.columns.values.tolist()
        for index, row in zapros_1.iterrows():
            for i in range(len(row)):
                self.tableWidget.setHorizontalHeaderLabels(headers)
                self.tableWidget.setItem(index, i, QTableWidgetItem(str(row[i])))

    def controllas(self):
        number = self.password_2.text()
        self.password_2.clear()
        if len(number)>0:
            x = connect_bd.controll(self.numbers_view, number)
            errors(x)
        else:
            errors('введите пароль')

    def change(self):
        password = self.password.text()
        self.password.clear()
        if self.number_line.text() == '':
            errors('введите номер строки для изменения')
        else:
            number = self.number_line.text()
            self.number_line.clear()
            if len(password)>0:
                x = connect_bd.chars(password, number)
                if x == 1:
                    errors('пароль неверный')
                elif x == 2:
                    errors('ошибка')
                elif len(x) == 0:
                    errors('такой записи не найдено')
                else:
                    self.wk.setCurrentIndex(1)
                    time.sleep(0.5)
                    x = x[0]
                    self.id_worker.setText(str(x['id_name_worker']))
                    self.id_detail.setText(str(x['id_detaly']))
                    self.id_operation.setText(str(x['id_operation']))
                    self.count_detail.setText(str(x['count_detaly']))
                    self.brak.clear()
                    self.brak.setText(str(x['tune']))
                    self.time_stop.clear()
                    self.time_stop.setText(str(x['time_stop']))
                    self.lineEdit.setText(str(x['commentars']))
                    if x['setting'] == 1:
                        self.setting.setChecked(1)
                    self.y = number
                    self.time_update = time.time()
                    # self.timeses()
                    t = threading.Thread(target=self.timeses(), name='potok')
                    r = threading.Thread(target=self.ok())
                    t.start()
                    r.start()
            else:
                errors('введите пароль')
    def ok(self):
        pass

    def timeses(self):
        now = time.time() - self.time_update
        self.progressBar.setValue(int(now))
        if now > 180:
            self.y = 0
        # print(self.y)
        t = threading.Timer(3.6, self.timeses)
        t.daemon = True
        if self.y != 0:
            t.start()
        else:
            self.progressBar.setValue(int(1))
            self.clearing()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()