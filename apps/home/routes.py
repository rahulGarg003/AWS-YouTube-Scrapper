from apps.home import blueprint
from flask import render_template, current_app, redirect, url_for, flash
from apps.home.util import (
                                get_channel_data,
                                get_video_data,
                                insert_channel_data,
                                insert_video_data
                        )

from apps import mysqlDB

@blueprint.route('/')
def index():
    return render_template('home/index.html')

@blueprint.route('/channel/<string:channelId>')
def channel(channelId):
    try:
        if(not channelId.startswith('@')):
            flash('Please provide correct Channel Id')
            return redirect(url_for('home_blueprint.index'))
        channel_data = get_channel_data(channelName=channelId)
        if(channel_data['channel-title'] == ''):
            flash('Please provide correct Channel Id')
            return redirect(url_for('home_blueprint.index'))
        insert_channel_data(channeldata=channel_data, mysqldb=mysqlDB)
        current_app.logger.info(f'data posted to db for channel: {channelId}')
        return render_template('home/channel.html', channeldata = channel_data, thumburl = channel_data['channel-thumbnail']['url'])
    except Exception as err:
        current_app.logger.exception(err)
        return render_template('home/page-404.html')

@blueprint.route('/video/<string:videoId>')
def video(videoId):
    try:
        video_data = get_video_data(videoId=videoId)
        if(video_data['video-title'] == ''):
            flash('Please provide correct Video Id')
            return redirect(url_for('home_blueprint.index'))
        insert_video_data(videoData=video_data, mysqldb=mysqlDB)
        current_app.logger.info(f'data posted to db for video: {videoId}')
        return render_template('home/video.html', videodata = video_data, videoid=videoId)
    except Exception as err:
        current_app.logger.exception(err)
        return render_template('home/page-404.html')

