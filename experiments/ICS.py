import numpy as np
   

def main():
    group_nos = np.array([
        1, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 22, 23,
        24, 25, 26, 27, 28, 29, 31, 32, 33, 35, 36, 37, 38, 40,
        43, 44, 46
        ])

    assert len(group_nos) == 34
    num_of_assignments = 5

    rng = np.random.default_rng()
    valid_permutations = [group_nos]

    while len(valid_permutations) < num_of_assignments:
        permutation = rng.permutation(group_nos)
        flag = True
        for valid_permutation in valid_permutations:
            if np.any(np.equal(permutation, valid_permutation)):
                flag = False

        if flag:
            valid_permutations.append(permutation)

    print(f"validation: {double_check_if_permutations_are_valid(valid_permutations)}")

    reshaped_valid_permutations = np.swapaxes(valid_permutations, 0, 1)
    print(reshaped_valid_permutations)

    """some extra checks"""
    unique, counts = np.unique(reshaped_valid_permutations, return_counts=True)
    countdict = dict(zip(unique, counts))
    for asignment_count in countdict.values():
        assert asignment_count == num_of_assignments

    assert np.max(reshaped_valid_permutations) == 46
    assert np.min(reshaped_valid_permutations) == 1


def double_check_if_permutations_are_valid(permutations):
    for permutation in permutations:
        for permutation2 in permutations:
            if np.all(permutation == permutation2):
                continue
            if np.any(np.equal(permutation, permutation2)):
                return False
    return True


if __name__ == '__main__':
    main()
