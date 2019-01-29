#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import sys
import os
import random
import tkinter as tk
import tkinter.messagebox

import numpy as np
import pandas as pd

X_COLS = ['Dancability', 'Energy', 'Valance', 'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness']
Y_COL = 'HR perc'

MODE_NAMES = [
    'very light (50-60)',
    'light (60-70)',
    'moderate (70-80)',
    'hard (80-90)',
    'maximum (90-100)'
]


MODE_HRS = [50, 60, 70, 80, 90] # values for target HR levels


class MusicRecommender(object):
    def __init__(self, data_file, feature_dist, best_k):
        self.data_file = data_file
        self.feature_dist = feature_dist
        self.best_k = best_k
        self.root = tk.Tk()
        self.root.title('Music Recommender')
        self.v_age = tk.IntVar()
        self.v_age.set(20)
        self.v_target_hr_level = tk.IntVar()
        self.v_target_hr_level.set(0)
        self.v_playing = tk.StringVar()
        self.v_playing.set('Playing nothing')
        self.user_prefer = {
            'music': {}
        }
        self.cur_music_id = None
        self.learning_rate = 0.1
        self.init_ui()
        self.init_data()
        self.root.mainloop()

    def init_ui(self):
        """ init UI """
        main_frame = tk.Frame(self.root, width=200, height=200, padx=5, pady=10)
        main_frame.pack()
        user_frame = tk.Frame(main_frame, width=200, height=50)
        user_frame.pack(fill='y')
        tk.Label(user_frame, padx=5, pady=5, justify='left', text='Age').pack(side='left')
        tk.Entry(user_frame, width=10, textvariable=self.v_age).pack(side='left')
        for i in range(len(MODE_NAMES)):
            tk.Radiobutton(
                main_frame,
                variable=self.v_target_hr_level,
                text=MODE_NAMES[i],
                value=i
            ).pack(anchor='w')

        btn_frame = tk.Frame(main_frame, width=200, height=50)
        btn_frame.pack(fill='y')
        play_btn = tk.Button(btn_frame, text='Play next', state='active', command=self.command_play)
        play_btn.pack(side='left')
        like_btn = tk.Button(btn_frame, text='like', state='active', command=self.command_like)
        like_btn.pack(side='left')
        dislike_btn = tk.Button(btn_frame, text='dislike', state='active', command=self.command_dislike)
        dislike_btn.pack(side='left')
        
        music_frame = tk.Frame(main_frame, width=200, height=50)
        music_frame.pack(fill='y')
        self.playing_label = tk.Label(music_frame, pady=5, justify='center', textvariable=self.v_playing)
        self.playing_label.pack(side='left')
        
    def command_play(self):
        """ command implementation for play button
            Update music data when any newer data file exists
        """
        mtime = os.stat(self.data_file).st_mtime
        if mtime > self.last_mtime:
            self.init_data()
            print('data updated in timestamp %s, last %s' % (mtime, self.last_mtime))
        else:
            print('no need to update data, all is the latest')
        self.v_playing.set('Playing: %s' % self.next_music())

    def command_like(self):
        """ command implementation for like button """
        self.user_prefer['music'][self.cur_music_id] = 2
        print('probabilty of %s is improved' % self.cur_music_id)
        print('user prefer: %s' % self.user_prefer)

    def command_dislike(self):
        """ command implementation for dislike button """
        self.user_prefer['music'][self.cur_music_id] = 0.5
        print('probabilty of %s is reduced' % self.cur_music_id)
        print('user prefer: %s' % self.user_prefer)

    def init_data(self):
        """ init music data """
        self.last_mtime = os.stat(self.data_file).st_mtime
        data = {}
        df = pd.read_csv(self.data_file)
        df_dict = df.to_dict()
        for i, ID in df_dict['ID'].items():
            data[ID] = {
                'ID': ID,
                'Genre': df_dict['Genre'][i],
                'BPM': df_dict['Tempo'][i],
                'HR': df_dict['HR'][i],
            }
            # 0~1 features
            for col in X_COLS:
                data[ID][col] = df_dict[col][i]
        self.data = data

    def get_recommendation(self, feature, k):
        """ get a recommended music list
        Returns
            a list of tuple (ID, music)
        """
        def __score(v, feature):
            se_sum = sum([(v[k] - fea)**2 for k, fea in feature.items()])
            return math.sqrt(se_sum)
        return sorted(self.data.items(), key=lambda x: __score(x[1], feature))[:k]

    def next_music(self):
        """ obtain the next music
        Returns
            a formatted string of the next music
        """
        max_hr = 220 - self.v_age.get()
        target_hr = MODE_HRS[self.v_target_hr_level.get()]
        hr = target_hr * max_hr / 100.
        feature = self.feature_dist[target_hr]
        playlist = self.get_recommendation(feature, self.best_k)
        music_prob = {ID: random.random() for ID, music in playlist}
        for ID, prefer_score in self.user_prefer['music'].items():
            if ID not in music_prob:
                continue
            music_prob[ID] *= prefer_score
        music_prob.pop(self.cur_music_id, None)
        self.cur_music_id = self.get_max(music_prob)
        music = self.data[self.cur_music_id]
        return '%s \nGenre: %s | %dBPM' % (music['ID'], music['Genre'], music['BPM'])

    def get_max(self, items):
        """ get ID of music with the largest probability
        Args
            items: a list of music items (ID, probability)
        Returns
            Music ID
        """
        cand = None
        _max = -999999999
        for k, v in items.items():
            if v > _max:
                _max = v
                cand = k
        return cand


def gen_feature_distribution(data_file):
    """ display features per HR perc """
    df = pd.read_csv(data_file)
    feature_dist = {}
    labels = sorted(df[Y_COL].unique())
    continuous_features = X_COLS
    for label in labels:
        feature = {}
        df_hrp = df[df[Y_COL]==label]
        for fea in X_COLS:
            feature[fea] = df_hrp[fea].mean()
        feature_dist[label] = feature
    return feature_dist


if __name__ == '__main__':
    data_file = sys.argv[1]
    best_k = 9 #int(sys.argv[2])
    feature_dist = gen_feature_distribution(data_file)
    print('Distribution of 0~1 features: %s' % feature_dist)
    MusicRecommender(data_file, feature_dist, best_k)
