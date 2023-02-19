import json
import requests
from bs4 import BeautifulSoup as bs
from googleapiclient.discovery import build
# from decouple import config
import os
from apps.home.models import ScrappedVideoData, ScrappedChannelData

def get_url(route='', page_type='channel', section_type='videos'):
    base_url = 'https://www.youtube.com/'
    if(page_type == 'video'):
        return base_url + 'watch?v=' + route
    return base_url + route + '/' + section_type

def get_json_data(route='', page_type='channel', section_type='videos'):
    url = get_url(route, page_type, section_type)
    response = requests.get(url, headers={'Accept-Language': 'en-US,en;q=0.8'})
    soup = bs(response.text, 'html.parser')
    ytInitData = ''
    for i in soup.find_all('script'):
        if(i.text[0:17] == 'var ytInitialData'):
            ytInitData = i.text
    if(ytInitData == ''):
        return ''
    return json.loads(ytInitData[20:-1])

def get_channel_data(channelName):
    json_data = get_json_data(route=channelName, page_type='channel', section_type='videos')
    if(json_data == ''):
        return {'channel-title' : ''}
    channel_title = json_data.get('microformat',{}).get('microformatDataRenderer',{}).get('title','')
    channel_description = json_data.get('microformat',{}).get('microformatDataRenderer',{}).get('description','')
    channel_url = json_data.get('microformat',{}).get('microformatDataRenderer',{}).get('urlCanonical', '')
    temp_channel_thumbnail = json_data.get('microformat',{}).get('microformatDataRenderer',{}).get('thumbnail', '').get('thumbnails','')
    if(len(temp_channel_thumbnail)>0):
        channel_thumbnail = temp_channel_thumbnail[0]
    channel_videos_count = json_data.get('header',{}).get('c4TabbedHeaderRenderer',{}).get('videosCountText',{}).get('runs',[])
    if(len(channel_videos_count)>0):
        channel_videos_count = channel_videos_count[0].get('text','')
    tabs = json_data.get('contents',{}).get('twoColumnBrowseResultsRenderer',{}).get('tabs',[])
    video_content = {}
    if(len(tabs) > 1):
        tab = tabs[1]
        # video_content['tab-title'] = tab.get('tabRenderer',{}).get('title','')
        contents = tab.get('tabRenderer',{}).get('content',{}).get('richGridRenderer',{}).get('contents',[])
        channel_contents = []
        for content in contents:
            c = {}
            vr = content.get('richItemRenderer',{}).get('content',{}).get('videoRenderer',{})
            c['videoid'] = vr.get('videoId','')
            c['video-label'] = vr.get('title',{}).get('accessibility',{}).get('accessibilityData',{}).get('label','')
            des = ''
            for i in vr.get('descriptionSnippet',{}).get('runs',[]):
                des = des + i.get('text','')
            c['video-description'] = des
            c['video-published-time'] = vr.get('publishedTimeText',{}).get('simpleText','')
            c['video-length'] = vr.get('lengthText',{}).get('accessibility',{}).get('accessibilityData',{}).get('label','')
            c['video-viewcount'] = vr.get('viewCountText',{}).get('simpleText','')
            c['video-thumbnail'] = {}
            if(len(vr.get('thumbnail',{}).get('thumbnails',[])) > 0):
                c['video-thumbnail'] = vr.get('thumbnail',{}).get('thumbnails',[])[0] 
            if(not vr.get('videoId','') == ''):
                channel_contents.append(c)
        video_content[tab.get('tabRenderer',{}).get('title','')] = channel_contents
    return {
        'channel-id' : channelName,
        'channel-title' : channel_title,
        'channel-description' : channel_description,
        'channel-url' : channel_url,
        'channel-thumbnail' : channel_thumbnail,
        'channel-videos-count' : channel_videos_count,
        'channel-video-content' : video_content
    }

def get_video_data(videoId):
    jsondata = get_json_data(route=videoId, page_type='video')
    video_title = ''
    video_view_count = ''
    video_likes = ''
    publisheddate = ''
    publishedreldate = ''
    video_content = jsondata.get('contents',{}).get('twoColumnWatchNextResults',{}).get('results',{}).get('results',{}).get('contents',[])
    if(len(video_content) > 0): 
        content = video_content[0].get('videoPrimaryInfoRenderer',{})
        _video_title = content.get('title',{}).get('runs',[])
        if(len(_video_title) > 0):
            video_title = _video_title[0].get('text','')
        video_view_count = content.get('viewCount',{}).get('videoViewCountRenderer',{}).get('viewCount',{}).get('simpleText','')
        _video_likes_dislikes = content.get('videoActions',{}).get('menuRenderer',{}).get('topLevelButtons',[])
        if(len(_video_likes_dislikes) > 0):
            video_likes = _video_likes_dislikes[0].get('segmentedLikeDislikeButtonRenderer',{}).get('likeButton',{}).get('toggleButtonRenderer',{}).get('defaultText',{}).get('accessibility',{}).get('accessibilityData',{}).get('label','')
        publisheddate = content.get('dateText',{}).get('simpleText','')
        publishedreldate = content.get('relativeDateText',{}).get('simpleText','')
    
    video_owner = ''
    video_owner_url = ''
    video_description = ''
    if(len(video_content) > 1):
        content = video_content[1].get('videoSecondaryInfoRenderer',{})
        _video_owner = content.get('owner',{}).get('videoOwnerRenderer',{}).get('title',{}).get('runs',[])
        if(len(_video_owner) > 0):
            video_owner = _video_owner[0].get('text','')
            video_owner_url = _video_owner[0].get('navigationEndpoint',{}).get('browseEndpoint',{}).get('canonicalBaseUrl','')
        _video_description = content.get('description',{}).get('runs',[])
        if(len(_video_description) > 0):
            video_description = _video_description[0].get('text','')

    comments = get_video_comments(videoId)

    return ({
        'video-id' : videoId,
        'video-title' : video_title,
        'video-view-count' : video_view_count,
        'video-likes' : video_likes,
        'video-published-date' :publisheddate,
        'video-published-reldate' : publishedreldate,
        'video_owner' : video_owner,
        'video-owner-url' : video_owner_url,
        'video-description' : video_description,
        'video-comments' : comments
    })

def get_video_comments(videoId):
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.environ.get('GCP_YOUTUBE_API_KEY')

    youtube = build(api_service_name, api_version, developerKey = DEVELOPER_KEY)

    # Put Any YouTube video ID.
    ID = videoId

    commentsdata = []
    data = youtube.commentThreads().list(part='snippet', videoId=ID, maxResults='100', textFormat="plainText").execute()

    for i in data["items"]:

        name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
        comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
        likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
        published_at = i["snippet"]['topLevelComment']["snippet"]['publishedAt'] 
        replies_count = i["snippet"]['totalReplyCount']

        comment_data = {
            'author-name': name, 
            'comment' : comment, 
            'likes' : likes, 
            'published_at' : published_at, 
            'replies_count' : replies_count,
            'replies' : []
        }

        TotalReplyCount = i["snippet"]['totalReplyCount']

        if TotalReplyCount > 0:

            parent = i["snippet"]['topLevelComment']["id"]

            data2 = youtube.comments().list(part='snippet', maxResults='100', parentId=parent,
                                            textFormat="plainText").execute()

            for i in data2["items"]:
                name = i["snippet"]["authorDisplayName"]
                comment = i["snippet"]["textDisplay"]
                likes = i["snippet"]['likeCount']
                published_at = i["snippet"]['publishedAt']

                comment_data['replies'].append({
                    'reply-author-name': name, 
                    'reply-comment' : comment, 
                    'likes' : likes, 
                    'published_at' : published_at
                })
        commentsdata.append(comment_data)

    while ("nextPageToken" in data):

        if(len(commentsdata) >= 50):
            break

        data = youtube.commentThreads().list(part='snippet', videoId=ID, pageToken=data["nextPageToken"],
                                                maxResults='100', textFormat="plainText").execute()

        for i in data["items"]:
            name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
            comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
            likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
            published_at = i["snippet"]['topLevelComment']["snippet"]['publishedAt']
            replies_count = i["snippet"]['totalReplyCount']
            comment_data = {
                'author-name': name, 
                'comment' : comment, 
                'likes' : likes, 
                'published_at' : published_at, 
                'replies_count' : replies_count,
                'replies' : []
            }

            TotalReplyCount = i["snippet"]['totalReplyCount']

            if TotalReplyCount > 0:

                parent = i["snippet"]['topLevelComment']["id"]

                data2 = youtube.comments().list(part='snippet', maxResults='100', parentId=parent,
                                                textFormat="plainText").execute()

                for i in data2["items"]:
                    name = i["snippet"]["authorDisplayName"]
                    comment = i["snippet"]["textDisplay"]
                    likes = i["snippet"]['likeCount']
                    published_at = i["snippet"]['publishedAt']

                    comment_data['replies'].append({
                        'reply-author-name': name, 
                        'reply-comment' : comment, 
                        'likes' : likes, 
                        'published_at' : published_at
                    })
            commentsdata.append(comment_data)
    return commentsdata

def insert_video_data(videoData, mysqldb):
    data = ScrappedVideoData(
        video_id = videoData['video-id'],
        video_title = videoData['video-title'],
        video_description = videoData['video-description'],
        video_likes = videoData['video-likes'],
        video_published_date = videoData['video-published-date'],
        video_owner = videoData['video_owner'],
        video_view_count = videoData['video-view-count']
    )
    exists = mysqldb.session.query(mysqldb.exists().where(ScrappedVideoData.video_id == videoData['video-id'])).scalar()
    if(exists):
        existingdata = ScrappedVideoData.query.filter_by(video_id = videoData['video-id'])
        existingdata.video_title = videoData['video-title'],
        existingdata.video_description = videoData['video-description'],
        existingdata.video_published_date = videoData['video-published-date'],
        existingdata.video_likes = videoData['video-likes'],
        existingdata.video_owner = videoData['video_owner']
        existingdata.video_view_count = videoData['video-view-count']
    else:
        mysqldb.session.add(data)
    mysqldb.session.commit()

def insert_channel_data(channeldata, mysqldb):
    data = ScrappedChannelData(
        channel_id = channeldata['channel-id'],
        channel_title = channeldata['channel-title'],
        channel_description = channeldata['channel-description'],
        channel_url = channeldata['channel-url'],
        channel_videos_count = channeldata['channel-videos-count']
    )
    exists = mysqldb.session.query(mysqldb.exists().where(ScrappedChannelData.channel_id == channeldata['channel-id'])).scalar()
    if(exists):
        existingdata = ScrappedChannelData.query.filter_by(channel_id = channeldata['channel-id'])
        existingdata.channel_title = channeldata['channel-title'],
        existingdata.channel_description = channeldata['channel-description'],
        existingdata.channel_url = channeldata['channel-url'],
        existingdata.channel_videos_count = channeldata['channel-videos-count']
    else:
        mysqldb.session.add(data)
    mysqldb.session.commit()