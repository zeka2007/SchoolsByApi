from datetime import datetime, date

date_format = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}


class Date:
    def __init__(self,
                 intervals: dict,
                 quarter: int):
        current_date = datetime.now()
        current_year = current_date.year

        if current_date.month in range(1, 8):
            if quarter <= 2:
                current_year = current_year - 1

        self.start_date = datetime(current_year,
                                   intervals[quarter].start_month,
                                   intervals[quarter].start_date)
        self.end_date = datetime(current_year,
                                 intervals[quarter].end_month,
                                 intervals[quarter].end_date)
