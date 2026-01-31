array = [1, 2, 3, 45, 356, 569, 600, 705, 923]


def search(array: list[int], number: int) -> bool:
    first = 0
    last = len(array) - 1
    while first <= last:
        median = (first + last) // 2
        if array[median] == number:
            return True
        if array[median] < number:
            first = median + 1
        elif array[median] > number:
            last = median - 1
    return False


print(search(array, 45))
