cache_set = set()


def print_avoid_cache(msg):
    if cache_set.__contains__(msg):
        return
    print msg
    cache_set.add(msg)
