def get_pair(lst):
    query = lst.items.extra(select={'random': 'RANDOM()'}).order_by('random')
    return tuple(query[:2])

def create_nonce(pair):
    return 'HERE_IS_MY_NONCE'

def check_nonce(nonce, pair):
    return nonce == 'HERE_IS_MY_NONCE'

