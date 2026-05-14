from math import floor, sqrt


def pi(x: int, y: int) -> int:
    return (x + y) * (x + y + 1) // 2 + y

def unpi(z: int) -> tuple[int, int]:
    w = floor((sqrt(8 * z + 1) - 1) / 2)
    t = (w**2 + w) // 2

    y = z - t
    x = w - y

    return x, y

def encode_list(lst: list[int]) -> int:
    if len(lst) == 0:
        return 0
    if len(lst) == 1:
        return lst[0]
    return pi(lst[0], encode_list(lst[1:]))

def main():
    # Test pi
    assert pi(47, 32) == 3192, "pi(47, 32) ha de ser 3192"
    assert pi(3, 2) == 17,     "pi(3, 2) ha de ser 17"
    assert pi(1, 17) == 188,   "pi(1, 17) ha de ser 188"
    assert pi(0, 0) == 0,      "pi(0, 0) ha de ser 0"
    print("pi: OK")

    # Test unpi
    assert unpi(3192) == (47, 32), "unpi(3192) ha de ser (47, 32)"
    assert unpi(17) == (3, 2),     "unpi(17) ha de ser (3, 2)"
    assert unpi(188) == (1, 17),   "unpi(188) ha de ser (1, 17)"
    assert unpi(0) == (0, 0),      "unpi(0) ha de ser (0, 0)"
    print("unpi: OK")

    # Test pi/unpi inverses
    for x in range(10):
        for y in range(10):
            assert unpi(pi(x, y)) == (x, y), f"unpi(pi({x},{y})) ha de ser ({x},{y})"
    print("pi/unpi inverses: OK")

    # Test encode_list
    assert encode_list([1, 3, 2]) == 188, "encode_list([1,3,2]) ha de ser 188"
    assert encode_list([3, 2]) == 17,     "encode_list([3,2]) ha de ser 17"
    assert encode_list([5]) == 5,         "encode_list([5]) ha de ser 5"
    assert encode_list([]) == 0,          "encode_list([]) ha de ser 0"
    print("encode_list: OK")

if __name__ == '__main__':
    main()

