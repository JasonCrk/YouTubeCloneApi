from enum import Enum


class SortByEnum(Enum):
    UPLOAD_DATE = 'upload_date'
    VIEW_COUNT = 'view_count'
    RATING = 'rating'


class UploadDateEnum(Enum):
    LAST_HOUR = 'last_hour'
    TODAY = 'today'
    THIS_WEEK = 'this_week'
    THIS_MONTH = 'this_month'
    THIS_YEAR = 'this_year'