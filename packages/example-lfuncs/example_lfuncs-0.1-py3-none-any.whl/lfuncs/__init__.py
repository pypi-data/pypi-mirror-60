def find_startswith_in_list(prefix, list1):
    return list(filter(lambda e: e.startswith(prefix), list1))

def find_endswith_in_list(suffix, list1):
    return list(filter(lambda e: e.endswith(suffix), list1))

def split_lists(olist, prefix):
    list1 = []
    list2 = []
    for e in olist:
        if e.startswith(prefix):
            list1.append(e)
        else:
            list2.append(e)

    return list1, list2

def joke():
    print('A foo walks into a bar, takes a look around and says "Hello World!"')
