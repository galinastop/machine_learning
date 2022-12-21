import random
import numpy as np
import pandas as pd
from sklearn import svm
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score


def generate_random_points():
    x = []
    y = []
    target = []

    for i in range(int(size / 2)):
        # допустимое отклонение
        p = 2
        if random.randint(0, 1) == 1:
            p = 1.5

        # класс 0
        x.append(np.round(random.uniform(0, 4.5 + p), 1))
        y.append(np.round(random.uniform(0, 4.5 + p), 1))
        target.append(0)
        # класс 1
        x.append(np.round(random.uniform(5.5 - p, 10), 1))
        y.append(np.round(random.uniform(5.5 - p, 10), 1))
        target.append(1)

    df_x = pd.DataFrame(data=x)
    df_y = pd.DataFrame(data=y)
    df_target = pd.DataFrame(data=target)
    data_frame = pd.concat([df_x, df_y], ignore_index=True, axis=1)
    data_frame = pd.concat([data_frame, df_target], ignore_index=True, axis=1)

    data_frame.columns = ['x', 'y', 'target']
    return data_frame


def print_train_svm(ax):
    colors = classes_train
    colors = np.where(colors == 1, COLOR1, COLOR2)

    ax.scatter(features[:-test_size]['x'], features[:-test_size]['y'], c=colors)
    ax.contour(XX, YY, Z, colors='k', levels=[-1, 0, 1], alpha=0.5, linestyles=['--', '-', '--'])
    ax.scatter(model.support_vectors_[:, 0], model.support_vectors_[:, 1], s=100,
               linewidth=1,
               facecolors='none',
               edgecolors='k')


def print_train_data():
    _, ax = plt.subplots(figsize=(12, 12))
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    print_train_svm(ax)
    plt.show()


def print_train_with_test_data():
    _, ax = plt.subplots(figsize=(12, 12))
    print_train_svm(ax)
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    ax.scatter(features[size - test_size:]['x'], features[size - test_size:]['y'], color="red",
               marker='*', s=100)
    plt.show()


def print_predicted_test_data():
    _, ax = plt.subplots(figsize=(12, 12))
    print_train_svm(ax)
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    colors = predictions_poly
    colors = np.where(colors == 1, COLOR1, COLOR2)

    ax.scatter(features[size - test_size:]['x'], features[size - test_size:]['y'], c=colors,
               marker='*', s=100)
    plt.show()


if __name__ == '__main__':
    COLOR1 = "#7B4F4B"
    COLOR2 = "#A1C299"

    size = 100
    dataset = generate_random_points()
    features = dataset[['x', 'y']]
    label = dataset['target']

    test_size = int(np.round(size * 0.2, 0))

    points_train = features[:-test_size].values
    classes_train = label[:-test_size].values
    points_test = features[-test_size:].values
    classes_test = label[-test_size:].values

    model = svm.SVC(kernel='linear')
    model.fit(points_train, classes_train)

    xx = np.linspace(0, max(features['x']) + 1, len(points_train))
    yy = np.linspace(0, max(features['y']) + 1, len(classes_train))

    YY, XX = np.meshgrid(yy, xx)
    xy = np.vstack([XX.ravel(), YY.ravel()]).T

    Z = model.decision_function(xy).reshape(XX.shape)

    predictions_poly = model.predict(points_test)
    accuracy_poly = accuracy_score(classes_test, predictions_poly)
    print("Accurancy of test data: " + str(accuracy_poly))

    # Картиночки
    print_train_data()
    print_train_with_test_data()
    print_predicted_test_data()

    exit(1)
