from enum import Enum


class SearchSortOptions(Enum):
    UPLOAD_DATE = 'upload_date'
    VIEW_COUNT = 'view_count'
    RATING = 'rating'


class SearchUploadDate(Enum):
    LAST_HOUR = 'last_hour'
    TODAY = 'today'
    THIS_WEEK = 'this_week'
    THIS_MONTH = 'this_month'
    THIS_YEAR = 'this_year'


class VideoSortOptions(Enum):
    MOST_POPULAR = 'most_popular'
    RECENTLY_UPLOADED = 'recently_uploaded'
    OLDEST_UPLOADED = 'oldest_uploaded'
