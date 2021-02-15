def to_lst(my_string):
    temp = my_string.split("|")
    return [temp[i: i+8] for i in range(0, 64, 8)]


def to_str(my_list):
    return "".join([a + "|" for b in my_list for a in b])
