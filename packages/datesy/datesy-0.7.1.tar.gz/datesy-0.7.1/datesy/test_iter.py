from collections import OrderedDict


class Row:
    def __init__(self, data):
        self.data = data
        self.keys = list(data.keys())

    def __iter__(self):
        print("-")
        return iter(self.keys)


if __name__ == "__main__":
    d = OrderedDict({"1": 1, "2": 2, "3": 3, "4": 4})
    r = Row(d)
    print(list(r)[3])
