import re
import time
import numpy as np
import pickle 

class IDMap:
    def __init__(self):
        self.link_map = self.get_link_map()
        with open('data/dict.pkl', 'rb') as f:
            self.item_map = pickle.load(f)

    # TODO: could make this into a pre-made dictionary.. (is fast enough tho)
    def get_link_map(self):
        link_map = {}
        link_path = 'datasets/www_data/www_data/Movielens/kg/r_map.dat'

        # make dict of relationship vals
        with open(link_path) as f:
            for i, line in enumerate(f):
                link = re.search('/film.film.(.+?)>', line)
                link_map.update({i : link.group(1).replace('_', ' ').capitalize()})
        link_map.update({47 : 'Likes'}) # add likes relationship
        return link_map
    
    def convert(self, triplet):
        # subject 
        if triplet[0] in self.item_map:
            s = self.item_map[triplet[0]]
        else:
            s = 'Freebase ID: {}'.format(triplet[0])
        # relationship
        r = self.link_map[triplet[1]]
        # object
        if triplet[2] in self.item_map:
            o = self.item_map[triplet[2]]
        else:
            o = 'Freebase ID: {}'.format(triplet[2])

        print('<{} -- {} -- {}>'.format(s,r,o))
        
kg = np.load('data/kg.npy', allow_pickle=True)
rec = np.load('data/rec.npy', allow_pickle=True)
triplet_map = IDMap()

# both datasets are in identical format
for i in range(5):
    ind = np.random.randint(rec.shape[0])
    triplet_map.convert(rec[ind])

print()
for i in range(5):
    ind = np.random.randint(kg.shape[0])
    triplet_map.convert(kg[ind])

