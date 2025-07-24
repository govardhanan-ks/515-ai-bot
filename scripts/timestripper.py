import datetime
import calendar

class TimeStripper:
    def __init__(self):
        pass

    def get_week_of_month(self, date):
        first_day = date.replace(day=1)
        dom = date.day
        adjusted_dom = dom + first_day.weekday()
        week_num =  (adjusted_dom - 1) // 7 + 1
        return min(week_num, 5)
    
    def ordinal(self,n):
        return "%d%s" % (n, "tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])


    def get_week_string(self, date):
        week_num = self.get_week_of_month(date)
        month_name = date.strftime("%B").capitalize()
        return f"{self.ordinal(week_num)} Week of {month_name} {date.year}"

