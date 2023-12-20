import json
import random
import requests

import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()
admin_username = os.getenv('ADMIN_USERNAME')
admin_password = os.getenv('ADMIN_PASSWORD')

# read config json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

number_of_users = config['number_of_users']
max_posts_per_user = config['max_posts_per_user']
max_likes_per_user = config['max_likes_per_user']


# getting authorization token
def get_token(username, password):
    url = "http://127.0.0.1:8000/api/token/"
    response = requests.post(url, data={"username": username, "password": password})
    return response.json()['access']


def create_user(username, email, password):
    url = "http://127.0.0.1:8000/api/users/"
    data = {"username": username, "email": email, "password": password}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 400 and 'username' in response.json():
        print(f"Looks like user: {username} already exist")
        new_username = f"{username}_{random.randint(100, 999)}"
        new_email = f"{new_username}@example.com"
        return create_user(new_username, new_email, password)
    return response.json()


def create_post(content, user_id):
    url = "http://127.0.0.1:8000/api/posts/"
    data = {"content": content, "creator": user_id}
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def post_vote(post_id, up_vote=True):
    url = "http://127.0.0.1:8000/api/votes/"
    data = {"post": post_id, "up_vote": up_vote}  # up_vote or down_vote
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200 and response.status_code != 201:
        print(f"Error voting on post {post_id}: {response.status_code}, {response.text}")
    else:
        return response.json()


# # # MAIN # # #
# admin token for user creation
token = get_token(admin_username, admin_password)
headers = {"Authorization": f"Bearer {token}"}
all_post_ids = []
user_details = []

# 01 create users and their posts
for i in range(number_of_users):
    username = f"user_{i}"
    email = f"user_{i}@example.com"
    password = "password123"
    user = create_user(username, email, password)

    # check if user creation was successful
    if 'username' in user:
        print(f"Created user: {user['username']}")
        user_details.append((username, password, user['id']))
    else:
        print(f"Failed to create user: {username}")
        continue

# 02 create posts for each user
for username, password, user_id in user_details:
    token = get_token(username, password)
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(random.randint(1, max_posts_per_user)):
        post_content = f"Content for {username}"
        post = create_post(post_content, user_id)
        all_post_ids.append(post['id'])
        print(f"Created post: {post['id']} by {username}")

# 03 post votes
for username, password, user_id in user_details:
    token = get_token(username, password)
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(random.randint(1, max_likes_per_user)):
        post_id = random.choice(all_post_ids)
        vote = post_vote(post_id, up_vote=True)
        print(f"User {username} voted on post: {post_id}")

print("Bot activity successfully ended")
