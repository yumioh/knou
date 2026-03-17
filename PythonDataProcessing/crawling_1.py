from datetime import datetime
import calendar


WORK_DT = datetime.now().strftime('%Y%m%d')
print(WORK_DT)

dt = datetime.strptime(WORK_DT, '%Y%m%d')


w = datetime.strptime(WORK_DT, '%Y%m%d').weekday()
print(w)


d = dt.replace(day = calendar.monthrange(dt.year, dt.month)[1])
print(d)