import sys  # sys нужен для передачи argv в QApplication
import time
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog
import pandas as pd
from window import Ui_MainWindow  # Это наш конвертированный файл дизайна
import connect_bd
from datetime import date, timedelta
import openpyxl


def errors(r):
    msg = QMessageBox()
    msg.setText(r)
    msg.setWindowTitle("Ошибка")
    msg.exec()


class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    del_cod = ["'", "Decimal", "')}", '(', '[', ']', ')', '}', ',']

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.view_data_detaly.clicked.connect(self.view_s)
        self.ok_worker.clicked.connect(self.insert_smena)
        self.view_id.clicked.connect(self.id_name_workers)
        self.view_day.clicked.connect(self.calender_view)
        self.calendar.setDate(date.today())
        self.ok_go.clicked.connect(self.controllas)
        self.go.clicked.connect(self.change)
        self.y = 0
        self.numbers_view = []
        self.pushButton.clicked.connect(self.clearing)
        self.go_to.clicked.connect(self.view_data_works)
        self.on_to.setDate(date.today() - timedelta(30))
        self.to_to.setDate(date.today())
        self.stopp.clicked.connect(self.en)
        self.cancel_change.clicked.connect(self.cancel_ch)
        self.setting.clicked.connect(self.en)
        self.save_to.clicked.connect(self.safe_to_file)

    def cancel_ch(self):
        self.clearing()
        self.y = 0
        self.ok_worker.setText('записать')
        self.indikator.setText('')



    def en(self):
        if self.stopp.isChecked():
            x = True
        else:
            x = False
        self.spinBox.setEnabled(True if self.setting.isChecked() and x == False else False)
        self.time_stop.setEnabled(x)
        self.id_detail.setDisabled(x)
        self.id_operation.setDisabled(x)
        self.count_detail.setDisabled(x)
        self.brak.setDisabled(x)
        self.setting.setDisabled(x)

    def safe_to_file(self):
        on_to = self.on_to.text()
        to_to = self.to_to.text()
        on_to_1 = on_to.split(sep='.')
        on_to = date(int(on_to_1[2]), int(on_to_1[1]), int(on_to_1[0]))
        to_to_1 = to_to.split(sep='.')
        to_to = date(int(to_to_1[2]), int(to_to_1[1]), int(to_to_1[0]))
        if on_to < to_to:
            to_time = False
            ID_workers = self.who_to.text()
            if not ID_workers.isdigit():
                errors('введите правильный ID')
            else:
                name, data_night, data_day, data_stop, data_set, data_set_work = connect_bd.view_data_works_bd(on_to,
                                                                                                               to_to,
                                                                                                               ID_workers,
                                                                                                               to_time)
                if name == 1:
                    errors('такого исполнителя не найдено. проверьте ID')

                elif data_stop == 1:
                    if len(data_night) != 0:
                        name = str(name[0]['исполнитель'])
                        view_data_night = pd.DataFrame(data_night)
                        view_data_night['дата'] = view_data_night['дата'].dt.date
                        filename, _ = QFileDialog.getSaveFileName(self, '', name, '*.xlsx')
                        if filename == '':
                            pass
                        else:
                            view_data_night.to_excel(filename)
                    else:
                        view_data_night = 'нет строк для сохранения'
                        self.view_window.setText(view_data_night)




    def view_data_works(self):
        on_to = self.on_to.text()
        to_to = self.to_to.text()
        on_to_1 = on_to.split(sep='.')
        on_to = date(int(on_to_1[2]), int(on_to_1[1]), int(on_to_1[0]))
        to_to_1 = to_to.split(sep='.')
        to_to = date(int(to_to_1[2]), int(to_to_1[1]), int(to_to_1[0]))
        if on_to < to_to:
            to_time = True
            ID_workers = self.who_to.text()
            if not ID_workers.isdigit():
                errors('введите правильный ID')
            else:
                name, data_night, data_day, data_stop, data_set, data_set_work = connect_bd.view_data_works_bd(on_to, to_to, ID_workers, to_time)
                if name == 1:
                    errors('такого исполнителя не найдено. проверьте ID')

                elif data_stop == 1:
                    if len(data_night) != 0:
                        view_name = pd.DataFrame(name).to_string(header=False, col_space=25, index=False)
                        self.view_window.setText(view_name)
                        view_data_night = pd.DataFrame(data_night)
                        view_data_night['дата'] = view_data_night['дата'].dt.date
                        view_data_night = view_data_night.to_string(header=True, col_space=20, justify='center', index=False)
                    else:
                        view_data_night = 'нет строк для отображения'
                    self.view_window.append(view_data_night)

                else:
                    view_data_day = pd.DataFrame(data_day).to_string(header=True, col_space=20, justify='left', index=False)
                    view_data_night = pd.DataFrame(data_night).to_string(header=True, col_space=20, justify='left', index=False)
                    view_data_stop = pd.DataFrame(data_stop).to_string(header=True, col_space=20, justify='left', index=False)
                    view_name = pd.DataFrame(name).to_string(header=False,  col_space=30, index=False)
                    view_set = pd.DataFrame(data_set).to_string(header=True,  col_space=10, index=False, justify='left')
                    view_set_work = pd.DataFrame(data_set_work).to_string(header=True, col_space=10, index=False, justify='left')
                    self.view_window.setText(view_name)
                    self.view_window.append(view_data_day)
                    self.view_window.append(view_data_night)
                    self.view_window.append(view_data_stop)
                    self.view_window.append(view_set)
                    self.view_window.append(view_set_work)

        else:
            errors('неправильно выбраны даты')

    def id_name_workers(self):
        workers = connect_bd.workers()
        if workers != 'not ok':
            self.workers.setText(pd.DataFrame(workers, columns=['id', 'name']).to_string(header=False, index=False, col_space=14))
        else:
            errors('нет подключения')

    def view_s(self):
        x = str(connect_bd.view_details(self.id_detail_view.text())).replace('{', '\n')
        for i in self.del_cod:
            x = x.replace(f'{i}', '')
        self.view_window.setText(x)

    def insert_smena(self):
        if self.stopp.isChecked():
            if self.id_worker.text().isdigit() and self.time_stop.text().isdigit():
                id_name_worker = int(self.id_worker.text())
                id_detaly = 1
                id_operation = 1
                tune = 0
                count_detaly = 0
                setting = 0
                setting_work = 0
                comment_s = self.lineEdit.text()
                time_stop = self.time_stop.text()
                night = self.night.isChecked()
                x = connect_bd.inserts(id_name_worker, id_detaly, id_operation, tune, count_detaly, setting, comment_s, time_stop, night, setting_work, self.y)
                if x == 'успешно записано':
                    self.clearing()
                    self.y = 0
                    self.indikator.setText('')
                    self.ok_worker.setText('записать')
                    errors(x)
        else:
            if self.id_worker.text().isdigit() and self.id_detail.text().isdigit() \
                    and self.id_operation.text().isdigit() and self.brak.text().isdigit() \
                    and self.count_detail.text().isdigit() and self.time_stop.text().isdigit():
                id_name_worker = int(self.id_worker.text())
                id_detaly = int(self.id_detail.text())
                id_operation = int(self.id_operation.text())
                tune = int(self.brak.text())
                count_detaly = int(self.count_detail.text())
                setting = bool(self.setting.isChecked())
                setting_work = int(self.spinBox.text()) if setting == True else 0
                comment_s = self.lineEdit.text()
                time_stop = 0
                night = self.night.isChecked()
                x = connect_bd.inserts(id_name_worker, id_detaly, id_operation, tune, count_detaly, setting, comment_s, time_stop, night, setting_work, self.y)
                if x == 'успешно записано':
                    self.clearing()
                    self.y = 0
                    self.ok_worker.setText('записать')
                    self.indikator.setText('')
                    errors(x)
                else:
                    errors(x)

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
        self.night.setChecked(0)
        self.stopp.setChecked(0)
        self.en()

    def calender_view(self):
        self.tableWidget.clear()
        x = self.calendar.date()
        dates = [x.year(), x.month(), x.day()]
        zapros = connect_bd.updates(dates)
        if zapros != 'not ok':
            zapros_1 = pd.DataFrame(zapros, columns=['№', 'исполнитель', 'деталь', 'операция', 'брак', 'кол-во', 'наладка', 'комментарий', 'простой', 'проверено', 'ночная смена'])
            self.numbers_view = zapros_1['№'].to_list()
            headers = zapros_1.columns.values.tolist()
            for index, row in zapros_1.iterrows():
                for i in range(len(row)):
                    self.tableWidget.setHorizontalHeaderLabels(headers)
                    self.tableWidget.setItem(index, i, QTableWidgetItem(str(row[i])))
        else:
            errors('нет подключения')

    def controllas(self):
        number = self.password_2.text()
        self.password_2.clear()
        if len(number) > 0:
            x = connect_bd.controll(self.numbers_view, number)
            self.numbers_view = []
            self.tableWidget.clear()
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
            if len(password) > 0:
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
                    self.ok_worker.setText('изменить')
                    self.indikator.setText('режим изменения')
                    self.id_worker.setText(str(x['id_name_worker']))
                    self.night.setChecked(1) if x['night_works'] == 1 else self.night.setChecked(0)
                    if x['id_detaly'] > 1:
                        self.stopp.setChecked(0)
                        self.id_detail.setText(str(x['id_detaly']))
                        self.id_operation.setText(str(x['id_operation']))
                        self.count_detail.setText(str(x['count_detaly']))
                        self.brak.clear()
                        self.brak.setText(str(x['tune']))
                        self.en()
                    else:
                        self.id_detail.setText('1')
                        self.id_operation.setText('1')
                        self.count_detail.setText('0')
                        self.brak.clear()
                        self.brak.setText('0')
                        self.stopp.setChecked(1)
                        self.en()
                        self.time_stop.clear()
                        self.time_stop.setText(str(x['time_stop']))
                    self.lineEdit.setText(str(x['commentars']))
                    if x['setting'] == 1:
                        self.setting.setChecked(1)
                    self.y = number


            else:
                errors('введите пароль')


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()