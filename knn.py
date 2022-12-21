import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets


class Dataset:

    def __init__(self, data, base_size: int, normalize=True):
        # original
        self.data = data

        self.desc = data.DESCR
        self.dataset = data.data

        self.mins, self.maxs = self.mins_maxs(self.dataset)

        # normalized
        if normalize:
            self.dataset = self.normalize(data.data.view())

        self.target = data.target
        self.target_names = data.target_names
        self.target_count = len(self.target_names)
        self.feature_names = data.feature_names

        if base_size > len(self.dataset):
            raise AssertionError(f'study size: {base_size} can\'t be more than actual size: {len(self.dataset)}')

        self.base_data, self.test_data = self.divide_dataset(base_size)
        self.base_size = len(self.base_data)
        self.test_size = len(self.dataset) - self.base_size
        self.k = self.find_k()

    def info(self):
        # printing optimal K based on base data's size
        print(f'\nOptimal K: {self.k}\n'
              f'Common data (items count: {len(self.dataset)}: ) ')

        # printing input normalized data
        print(f'{self.feature_names}, target, name')

        for i, item in enumerate(self.dataset):
            target = self.target[i]
            target_name = self.target_names[target]
            print(f'{item}, {target}, {target_name}')

        # printing base normalized data
        print(f'Study data (items count: {len(self.base_data)}): ')
        print(f'{self.feature_names}, target, name')

        for i, item in enumerate(self.base_data):
            target = item[-1]
            target_name = self.target_names[target]
            print(f'{item}, {target_name}')

        # printing test normalized data
        print(f'Test data (items count: {len(self.test_data)}): ')
        print(f'{self.feature_names}, target, name')

        for i, item in enumerate(self.test_data):
            target = item[-1]
            target_name = self.target_names[target]
            print(f'{item}, {target_name}')

    def divide_dataset(self, should_study):
        base_data, test_data = [], []
        items_per_target = np.floor(should_study / self.target_count).astype(int)
        items_per_target_in_ds = np.floor(len(self.dataset) / self.target_count).astype(int)

        for i in range(self.target_count):
            start = items_per_target_in_ds * i
            end = items_per_target_in_ds * (i + 1)

            for c, j in enumerate(range(start, end)):
                item = list(self.dataset[j])
                item.append(self.target[j])
                if c <= items_per_target:
                    base_data.append(item)
                else:
                    test_data.append(item)

        return base_data, test_data

    def mins_maxs(self, dataset):
        mins, maxs = [i for i in dataset[0]], [i for i in dataset[0]]
        # [[5.31, 4.2, 3.0, 0.2], ...]
        # from 0 to 3
        for i in range(len(dataset[0])):
            # from 0 to dataset's len
            for j in range(len(dataset)):
                cur = dataset[j][i]
                if cur < mins[i]:
                    mins[i] = cur
                elif cur > maxs[i]:
                    maxs[i] = cur

        return mins, maxs

    def __normalize(self, row):
        for i in range(len(row)):
            row[i] = "{:.3f}".format((row[i] - self.mins[i]) / (self.maxs[i] - self.mins[i]))

        return row

    def normalize(self, dataset):
        # fill with default value

        for row in range(len(dataset)):
            dataset[row] = self.__normalize(dataset[row])

        return dataset

    def find_k(self):
        acc = 0
        k = np.floor(np.sqrt(len(self.base_data)) / 2).astype(int)

        for c in range(k, np.floor(np.sqrt(len(self.base_data)) * 2).astype(int)):
            total = 0
            for i, item in enumerate(self.test_data):
                # set k
                self.k = c
                target_class, target_name = self.knn(item[0: -1])
                if target_class == item[-1]:
                    total += 1
            total /= len(self.test_data)
            print(f'k: {c}, acc: {total}')
            if total > acc:
                k = c
                acc = total

        print(f'found optimal k: {k}')
        return k

    # param item: ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    #
    # return: target class, target name
    def knn(self, item, noralized=True):

        if not noralized:
            item = self.__normalize(item)

        from_ = np.array((tuple(item)))
        distances = []

        for i in self.base_data:
            to_ = np.array((tuple(i[0:-1])))
            # евклидово расстояние для n-мерного пространства
            distance = np.sqrt(np.sum(np.square(from_ - to_)))
            distances.append([distance, i[-1]])

        targets = np.zeros(self.target_count)
        distances.sort(key=lambda x: x[0])

        for dis in distances[0: int(self.k)]:
            targets[dis[1]] += 1

        max = 0
        target = targets[0]
        for i, t in enumerate(targets):
            if t > max:
                max = t
                target = i

        return target, self.target_names[target]


class Drawer:
    colors = [
        "#000000", "#BA0900", "#6B7900", "#00C2A0", "#FFAA92", "#FF90C9", "#B903AA", "#D16100",
        "#DDEFFF", "#000035", "#7B4F4B", "#A1C299", "#300018", "#0AA6D8", "#013349", "#00846F",
        "#372101", "#FFB500", "#C2FFED", "#A079BF", "#CC0744", "#C0B9B2", "#C2FF99", "#001E09",
        "#00489C", "#6F0062", "#0CBD66", "#EEC3FF", "#456D75", "#B77B68", "#7A87A1", "#788D66",
        "#885578", "#FAD09F", "#FF8A9A", "#D157A0", "#BEC459", "#456648", "#0086ED", "#886F4C"
    ]

    def __init__(self, dataset: Dataset, x=8, y=6):
        self.x = x
        self.y = y
        self.dataset = dataset
        self.plot = plt

    def draw(self):
        target_classes = [element[-1] for element in self.dataset.base_data]
        target_colors = [self.colors[i] for i in target_classes]

        for i in range(len(self.dataset.base_data[0][:-1])):
            for j in range(i + 1, len(self.dataset.base_data[0][:-1])):
                feature_one = [element[i] for element in self.dataset.base_data]
                feature_two = [element[j] for element in self.dataset.base_data]

                self.plot.scatter(feature_one, feature_two, c=target_colors)
                self.plot.xlabel(self.dataset.feature_names[i])
                self.plot.ylabel(self.dataset.feature_names[j])
                self.plot.show()


if __name__ == '__main__':
    # dataset obj
    iris = Dataset(datasets.load_iris(), base_size=100)

    # print info
    iris.info()

    # get test dataset
    test_dataset = iris.test_data

    # draw before normalization
    Drawer(Dataset(datasets.load_iris(), base_size=100, normalize=False)).draw()

    # draw after normalization
    Drawer(iris).draw()

    # test each element
    for i, item in enumerate(test_dataset):
        target_class, target_name = iris.knn(item[0: -1])
        print(f'input {i}: {item[0: -1]} \n'
              f'expected class: {item[-1]}, actual class: {target_class} - {target_name}')

    # test from console
    in_ = None
    while not in_ == [-1, -1, -1, -1]:
        in_ = [float(i) for i in input(
            "enter ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']: ").split(" ")]
        print(f'result class: {iris.knn(np.array(in_), False)[1]}')
