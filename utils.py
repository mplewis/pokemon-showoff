def unmulti(data):
    """
    Takes in a MultiDict and returns a normal Dict, removing any of the
    single-item list weirdness that comes with a MultiDict and replacing
    single item lists with the items alone.
    """
    new_dict = dict(data)
    for key in new_dict:
        if len(new_dict[key]) == 1:
            new_dict[key] = new_dict[key][0]
    return new_dict
