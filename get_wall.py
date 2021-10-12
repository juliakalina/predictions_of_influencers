# -*- coding: utf-8 -*-
"""Get_wall.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14XtJEN9f3pq5OFn5fItvQTF67xJtAeP9
"""

import vk
import time
import pandas as pd

version = 5.92
last_user = 10100
first_user= 10000
token = 'ef96c0a2ef96c0a2ef96c0a25befe05fdaeef96ef96c0a28fafeeb6ddabe8c8d15a9afa'
scope = 'users,wall'
step = 100

from google.colab import drive
drive.mount('/content/gdrive')


def parse_user_wall(response):
    res = []
    for item in response['items']:
        if item.get('deleted'):
            continue
        res.append({
            'post_id': item['id'],
            'owner_id': item['owner_id'],
            'from_id': item['from_id'],
            'text': item.get('text'),
            'reply_owner_id': item.get('reply_owner_id'),
            'reply_post_id': item.get('reply_post_id'),
            'num_comments': item.get('comments')['count'] if item.get('comments') else 0,
            'date': item.get('date')
        })
    return res


def get_user_wall(vk_api, user_id, timeout=0.5, max_count=1000):
    wall = []
    response = vk_api.wall.get(owner_id=user_id,
                               offset=0,
                               count=step,
                               v=version)
    wall.extend(parse_user_wall(response))
    time.sleep(timeout)
    
    num_wall = response['count']
    for offset in range(step,
                        min(step*((num_wall//step)+1), max_count),
                        step):
        response = vk_api.wall.get(owner_id=user_id,
                                   offset=offset,
                                   count=step,
                                   v=version)
        wall.extend(parse_user_wall(response))
        time.sleep(timeout)
    return wall


def parse_comment_post(response):
    res = []
    for item in response['items']:
        if item.get('deleted'):
            continue
        res.append({
            'post_id': item['post_id'],
            'owner_id': item['owner_id'],
            'comment_id': item['id'],
            'from_id': item['from_id'],
            'text': item.get('text'),
            'reply_to_user': item.get('reply_to_user'),
            'reply_to_comment': item.get('reply_to_comment'),
            'parents_stack': item.get('parents_stack'),
            'num_answer': item.get('thread')['count'] if item.get('thread') else 0,
            'date': item.get('date')
        })
    return res


def get_comment_post(vk_api, post, timeout=0.5, max_count=1000):
    if post['num_comments'] == 0:
        return []
    comments = []
    response = vk_api.wall.getComments(owner_id=post['owner_id'],
                                       post_id=post['post_id'],
                                       offset=0,
                                       count=step,
                                       v=version)
    comments.extend(parse_comment_post(response))
    time.sleep(timeout)
    #добираем оставшиеся
    num_comments = response['count']
    for offset in range(step,
                        min(step*((num_comments//step)+1), max_count),
                        step):
        response = vk_api.wall.getComments(owner_id=post['owner_id'],
                                           post_id=post['post_id'],
                                           offset=offset,
                                           count=step,
                                           v=version)
        comments.extend(parse_comment_post(response))
        time.sleep(timeout)
    return comments


def get_answer_comment(vk_api, comment, timeout=0.5, max_count=1000):
    if comment['num_answer'] == 0:
        return []
    answers = []
    response = vk_api.wall.getComments(owner_id=comment['owner_id'],
                                       post_id=comment['post_id'],
                                       offset=0,
                                       count=step,
                                       comment_id=comment['comment_id'],
                                       v=version)
    answers.extend(parse_comment_post(response))
    time.sleep(timeout)
    
    num_answers = response['count']
    for offset in range(step,
                        min(step*((num_answers//step) + 1), max_count),
                        step):
        response = vk_api.wall.getComments(owner_id=comment['owner_id'],
                                           post_id=comment['post_id'],
                                           offset=offset,
                                           count=step,
                                           comment_id=comment['comment_id'],
                                           v=version)
        answers.extend(parse_comment_post(response))
        time.sleep(timeout)
    return answers

from json import JSONDecoder


def main(first_user, last_user):
    all_posts = []
    all_comments = []
    all_answers = []

    session = vk.Session(access_token=token)
    vk_api = vk.API(session, scope=scope)
   
    for num, user in enumerate(range(first_user, last_user)):
      try:        
        posts = get_user_wall(vk_api=vk_api, user_id=user, timeout=0.34)
        comments = []
        for post in posts:
            comments.extend(get_comment_post(vk_api=vk_api, post=post, timeout=0.34))
        answers = []
        for comment in comments:
            answers.extend(get_answer_comment(vk_api=vk_api, comment=comment, timeout=0.34))
        all_posts.extend(posts)
        all_comments.extend(comments)
        all_answers.extend(answers)
      except Exception as e:
        print(e)
    return all_posts, all_comments, all_answers

if __name__ == '__main__':
    all_posts, all_comments, all_answers =\
                main(first_user, last_user)
    pd.DataFrame(all_posts).to_csv(f'/content/gdrive/My Drive/posts.csv')
    pd.DataFrame(all_comments).to_csv(f'/content/gdrive/My Drive/comments.csv')
    pd.DataFrame(all_answers).to_csv(f'/content/gdrive/My Drive/answers.csv')

!pip install vk