import threading
import numpy as np
from scipy.spatial.distance import cosine


class MuseReader(threading.Thread):

    def __init__(self, window, path, msg_queue):
        threading.Thread.__init__(self)
        self.window = window
        self.path = path
        self.embeds = dict()
        self.msg_queue = msg_queue
        self.start()

    def run(self):
        with open(self.path, 'r') as _file:
            num_emb, dim = map(int, _file.readline().split())

            for _ in range(num_emb):
                if self.window.stop:
                    break
                line = _file.readline().split()
                key = ' '.join(line[:-dim])
                value = list(map(float, line[-dim:]))
                self.embeds[key] = np.array(value)

        self.msg_queue.put(self.embeds)


def load_embeddings(path_en, path_pt):
    file_en = open(path_en, 'r')
    file_pt = open(path_pt, 'r')

    emb_en = dict()
    emb_pt = dict()

    num_emb, dim = map(int, file_en.readline().split())
    file_pt.readline()

    for _ in range(num_emb):
        line_pt = file_pt.readline().split()
        key_pt = ' '.join(line_pt[:-dim])
        value_pt = list(map(float, line_pt[-dim:]))
        emb_pt[key_pt] = np.array(value_pt)

        line_en = file_en.readline().split()
        key_en = ' '.join(line_en[:-dim])
        value_en = list(map(float, line_en[-dim:]))
        emb_en[key_en] = np.array(value_en)

    file_en.close()
    file_pt.close()

    return emb_en, emb_pt


def closest_words(word, emb_en, emb_pt, words_to_ignore=None):
    if not words_to_ignore:
        words_to_ignore = list()
    try:
        u = emb_en[word]
    except KeyError:
        return ['***']
    else:
        words = np.array(list(emb_pt))
        similarities = np.array(
            [cosine(u, emb_pt[k]) if k not in words_to_ignore else float('Inf') for k in words])
        similarities_indices = similarities.argsort()[:5]
        return list(zip(words[similarities_indices],
                        similarities[similarities_indices]))
