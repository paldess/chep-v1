import pandas as pd


a = pd.read_csv('settings.csv')
host = str(a['host'][0])
user = str(a['user'][0])
password = str(a['password'][0])
database = str(a['database'][0])
print(host)