# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 15:45:34 2020

@author: abdulkadarb
"""

import requests
from bs4 import BeautifulSoup as bs
requests.adapters.DEFAULT_RETRIES = 10


def get_episode_count(title_id):
    try:        
        url="https://www.imdb.com/title/{}"    
       
        page=requests.get(url.format(title_id, 'true'))
        
        title=bs(page.content, features='lxml').findAll("a", {"class"
            : "bp_item np_episode_guide np_right_arrow"})
        
        episode_count=title[0].text.strip().split('\n')[-1]
    except:
        episode_count="NA"
        
    return(episode_count)
    

get_episode_count("tt4917224")
