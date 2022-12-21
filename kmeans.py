import random
import matplotlib.pyplot as plt
import numpy as np

colors = [
    "#61615A", "#BA0900", "#6B7900", "#00C2A0", "#FFAA92", "#FF90C9", "#B903AA", "#D16100",
    "#DDEFFF", "#000035", "#7B4F4B", "#A1C299", "#300018", "#0AA6D8", "#013349", "#00846F",
    "#372101", "#FFB500", "#C2FFED", "#A079BF", "#CC0744", "#C0B9B2", "#C2FF99", "#001E09",
    "#00489C", "#6F0062", "#0CBD66", "#EEC3FF", "#456D75", "#B77B68", "#7A87A1", "#788D66",
    "#885578", "#FAD09F", "#FF8A9A", "#D157A0", "#BEC459", "#456648", "#0086ED", "#886F4C"
]

ks = [0 for i in range(9)]


def generate_point(mean_x, mean_y, deviation_x, deviation_y):
    return random.uniform(mean_x, deviation_x), random.uniform(mean_y, deviation_y)


def print_points(points):
    x = [x for [x, y] in points]
    y = [y for [x, y] in points]

    plt.scatter(x, y, c='b')
    plt.show()


def dist(x1, y1, x2, y2):
    # растояние между 2мя точками
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def find_start_centroids(points, k, draw=False):
    x_center = np.mean([x for [x, y] in points])
    y_center = np.mean([y for [x, y] in points])

    ranges = []

    # start; генерация начальных центроидов
    for [x, y] in points:
        ranges.append(dist(x, y, x_center, y_center))

    # радиус равый расстоянию от середины всех точек до самой крайней
    R = max(ranges)

    x_centroids, y_centroids = [], []

    for i in range(0, k):
        x_centroids.append(R * np.cos(2 * np.pi * i / k) + x_center)
        y_centroids.append(R * np.sin(2 * np.pi * i / k) + y_center)

    if draw:
        x = [x for [x, y] in points]
        y = [y for [x, y] in points]

        plt.scatter(x, y, c='b')
        plt.scatter(x_centroids, y_centroids, color='r')
        plt.show()

    return x_centroids, y_centroids


def recalculate_centroids(points, cluster, k):
    x_c, y_c = [], []
    x_cc, y_cc = [0 for _ in range(k)], [0 for _ in range(k)]
    count = [0 for _ in range(k)]

    c = 0

    for [x, y] in points:
        p = cluster[c]
        x_cc[p] += x
        y_cc[p] += y
        count[p] += 1
        c += 1

    for i in range(k):
        if count[i] != 0:
            y_c.append(y_cc[i] / count[i])
            x_c.append(x_cc[i] / count[i])

    return x_c, y_c


def cluster(points, x_centroids, y_centroids, draw=False):
    clust = []
    k = len(x_centroids)

    for [x, y] in points:
        cluster_value = 0
        min_dist = dist(x, y, x_centroids[0], y_centroids[0])

        for i in range(1, k):
            distance = dist(x, y, x_centroids[i], y_centroids[i])
            if distance < min_dist:
                cluster_value = i
                min_dist = distance
        clust.append(cluster_value)

    # draw step
    if draw:
        for i in range(0, k):
            px, py = [], []
            for j in range(len(points)):
                if clust[j] == i:
                    px.append(points[j][0])
                    py.append(points[j][1])
            plt.scatter(px, py, color=colors[i], alpha=0.4)
        plt.scatter(x_centroids, y_centroids, color="black", marker='+')
        plt.show()

    new_x_centroids, new_y_centroids = recalculate_centroids(points, clust, k)

    if new_x_centroids != x_centroids or new_y_centroids != y_centroids:
        return cluster(points, new_x_centroids, new_y_centroids, draw)

    return clust, new_x_centroids, new_y_centroids


def common_distance(points, clust, x_c, y_c):
    distance = 0

    for i in range(len(x_c)):
        for j in range(0, len(points)):
            if clust[j] == i:
                distance += dist(x_c[i], y_c[i], points[j][0], points[j][1]) ** 2

    return distance


def find_optimal_k(points):
    min_k = 1
    min_lambda = float('inf')

    for cluster_counter in range(1, 10):

        x_c, y_c = find_start_centroids(points, cluster_counter)
        c, x_c, y_c = cluster(points, x_c, y_c)
        previous_num = common_distance(points, c, x_c, y_c)

        x_c, y_c = find_start_centroids(points, cluster_counter + 1)
        c, x_c, y_c = cluster(points, x_c, y_c)
        cur_num = common_distance(points, c, x_c, y_c)

        x_c, y_c = find_start_centroids(points, cluster_counter + 2)
        c, x_c, y_c = cluster(points, x_c, y_c)
        new_num = common_distance(points, c, x_c, y_c)

        d = abs(previous_num - cur_num)
        t = abs(cur_num - new_num)
        if d != 0 and t != 0:
            new_lambda = t / d

            if new_lambda < min_lambda:
                print(cluster_counter, " min: ", min_lambda)
                print(cluster_counter, " new: ", new_lambda)
                min_k = cluster_counter + 1
                min_lambda = new_lambda
        ks[cluster_counter - 1] = previous_num

    return min_k


if __name__ == '__main__':
    # Генерация исходных точек

    cluster_mean_x = 50
    cluster_mean_y = 50

    # стандартное отклонение центров
    cluster_deviation_x = 50
    cluster_deviation_y = 50
    # стандартное отклонение точек
    point_deviation_x = 5
    point_deviation_y = 5

    # количество кластеров
    number_of_clusters = 4
    # максимальное количество точек в кластере

    max_points_per_cluster = 100
    # минимальное количество точек в кластере
    min_points_per_cluster = 50

    cluster_centers = [generate_point(cluster_mean_x,
                                      cluster_mean_y,
                                      cluster_deviation_x,
                                      cluster_deviation_y)
                       for i in range(number_of_clusters)]

    # сгенерированные точки
    points = [generate_point(center_x,
                             center_y,
                             point_deviation_x,
                             point_deviation_y)
              for center_x, center_y in cluster_centers
              for i in range(random.randint(min_points_per_cluster, max_points_per_cluster))]

    # Вывод исходных точек
    print_points(points)

    k = find_optimal_k(points)
    plt.plot(range(1, len(ks) + 1), ks, c='b')
    plt.show()

    # # находим начальные центры
    x_c, y_c = find_start_centroids(points, k, True)
    #
    # # определям точки по кластерам
    clust = cluster(points, x_c, y_c, True)
