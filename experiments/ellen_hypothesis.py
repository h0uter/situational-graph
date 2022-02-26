class Robot:
    x_pos = 0


def list_diff(list_a):
    list_a = [5, 5, 5]
    return list_a


def main1():
    robbie = Robot()

    print(f"Robbie's x_pos is {robbie.x_pos}")
    local_var = robbie.x_pos
    print(f"local_var is {local_var}")
    local_var += 1
    print(f"local_var is {local_var}")
    print(f"Robbie's x_pos is {robbie.x_pos}")


def list_func_experiment():
    my_list = [1, 2, 3]

    some_other_list = list_diff(my_list)

    print(f"my_list is {my_list}")
    print(f"some_other_list is {some_other_list}")


def reassign(list_a):
    list_a = [0, 1]


def append(list_a):
    list_a.append(1)


def web_experiment():
    list_a = [0]
    reassign(list_a)
    print(list_a)
    append(list_a)
    print(list_a)


def other_exp():
    listA = [0]
    listB = listA
    listB.append(1)
    print(listA)


if __name__ == "__main__":
    # main()
    # list_func_experiment()
    # web_experiment()
    other_exp()
