import pickle
import os

def save_obj(obj, name):
    """
    This function save an object as a pickle.
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    """
    This function will load a pickle file
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def load_inverted_index(path):
    to_return = {}
    inverted_index = load_obj(os.path.join(path, "inverted_idx"))

    for key in inverted_index:
        to_return[key] = inverted_index[key][0]

    return to_return
