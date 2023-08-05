from datetime import date, datetime

MON, TUE, WED, THU, FRI, SAT, SUN = range(7)

class holiday2020():
    HOLIDAYS = ((1, 1), #"new Year"
                (1, 24), #"new Year"
                (1, 25), #"new Year1"
                (1, 26), #"new Year2"
                (3, 1), #"3.1"
                (4, 30), #"Buddha Day"
                (5, 5), #"Children's Day"
                (6, 6), #"Memorial Day"
                (8, 15), #"Liberation Day"
                (9, 30), #"Thanksgiving"
                (10, 1), #"Thanksgiving1"
                (10, 2), #"Thanksgiving2"
                (10, 3), #"National Foundation Day"
                (10, 9), #"Hangul Day"
                (12, 25) #"Christmas"
                )

    def is_holiday(self, daytuple):
        HOLIDAYS = self.HOLIDAYS
        if daytuple in HOLIDAYS:
            return True
        else:
            return False

if __name__=='__main__':
    now = datetime.now()
    daytuple = (str(now.month),str(now.day))

    nowholiday = holiday2020()
    print(nowholiday.is_holiday(daytuple))