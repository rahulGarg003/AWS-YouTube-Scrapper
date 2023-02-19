from apps import mysqlDB
from datetime import datetime

class ScrappedVideoData(mysqlDB.Model):
    video_id = mysqlDB.Column(mysqlDB.String(100), primary_key=True)
    video_title = mysqlDB.Column(mysqlDB.String(200), nullable=False)
    video_description = mysqlDB.Column(mysqlDB.String(10000), nullable=False)
    video_likes = mysqlDB.Column(mysqlDB.String(100), nullable=False)
    video_published_date = mysqlDB.Column(mysqlDB.String(100), nullable=False)
    video_owner = mysqlDB.Column(mysqlDB.String(100), nullable=False)
    video_view_count = mysqlDB.Column(mysqlDB.String(100), nullable=False)

class ScrappedChannelData(mysqlDB.Model):
    channel_id = mysqlDB.Column(mysqlDB.String(200), primary_key=True)
    channel_title = mysqlDB.Column(mysqlDB.String(200), nullable=False)
    channel_description = mysqlDB.Column(mysqlDB.String(10000), nullable=False)
    channel_url = mysqlDB.Column(mysqlDB.String(100), nullable=False)
    channel_videos_count = mysqlDB.Column(mysqlDB.String(100), nullable=False)