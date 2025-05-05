from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import pandas as pd
from django.urls import reverse

import io
from io import StringIO

from django.http import JsonResponse
import requests
import requests.auth
import os
from .forms import SearchForm
import environ
env = environ.Env()
environ.Env.read_env()

def index(request):
    return render(request, 'search_app/index.html')

def reddit_search(request):
    print("Request method:", request.method)
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            subreddit = request.POST.get('subreddit')
            key_word = request.POST.get('key_word')

            environ.Env.read_env('.env')
            print(os.environ)

            client_id = env('CLIENT_ID')
            client_secret = env('CLIENT_SECRET')
            username = env('R_USERNAME')
            password = env('R_PASSWORD')

            auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
            data = {'grant_type': 'password', 'username': username, 'password': password}
            headers = {'User-Agent': 'searchapp/0.1 by gabe-dev-account'}

            res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
            print(res.json())
            token = res.json()['access_token']
            headers = {'Authorization': f'bearer {token}', 'User-Agent': 'searchapp/0.0.1 by gabe-dev-account'}
    
            res = requests.get(f'https://oauth.reddit.com/r/{subreddit}/search/?q={key_word}&type=posts', headers=headers, params={'limit': '20', 'restrict_sr': True})
    
            context = res.json()
            
            rows = []
            for post in context['data']['children']:
                rows.append({'subreddit': post['data']['subreddit'],
                                'title': post['data']['title'], 
                                'selftext': post['data']['selftext'],
                                'upvote_ratio': post['data']['upvote_ratio'],
                                'ups': post['data']['ups'],
                                'downs': post['data']['downs'],
                                'score': post['data']['score'],
                                'url': post['data']['url'],
                                'created_utc': post['data']['created_utc']})
            df = pd.DataFrame(rows)
            request.session['results_csv'] = df.to_csv(index=False)
            results = df.to_html()
            with open("search_app/reddit_search.html", "w", encoding="utf-8") as text_file:
                text_file.write(results)
            return render(request, 'search_app/reddit_search.html', {'table': results})

def save_results(request):
    if request.method == 'POST':
        csv_str = request.session.get('results_csv')
        df = pd.read_csv(StringIO(csv_str))
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        response = HttpResponse(
            output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="searchresults.xlsx"'
        return response
