# Генетический алгоритм
# Диофантовые уравнения
import random

import numpy as np


# Класс для описания диофантового уравнения
class DiofantEquation:

    def __init__(self, arg_count, debug=False):
        self.debug = debug
        self.arg_count = arg_count
        self.coefs_min = 1
        self.coefs_max = 20
        self.arg_min = 1
        self.arg_max = 100
        self.coefs, self.result = self.__generate()

    def __generate(self):
        coefs = np.random.randint(1, self.coefs_max, size=self.arg_count)
        args = np.random.randint(1, self.arg_max, size=self.arg_count)
        if self.debug:
            print(f'generated coeficents: {coefs}')
            print(f'generated arguments: {args}')

        result = 0
        for i in range(coefs.size):
            result += coefs[i] * args[i]

        return coefs, result

    # |(ax + by + cz) - result|
    def calculate(self, args):
        if len(args) != self.arg_count:
            raise AssertionError(len(self.arg_count), len(args))

        result = -1 * self.result
        for i in range(self.arg_count):
            result += args[i] * self.coefs[i]

        return np.abs(result)

    def print(self):
        print('Diofant Equation:')
        chr_i = 97
        chr_j = 0
        for i, c in enumerate(self.coefs):
            print(f'{c}{chr(chr_i)}{chr_j if chr_j != 0 else ""}', end='')
            if chr_i + 1 == 97 + 26:
                chr_j += 1
                chr_i = 97
            else:
                chr_i += 1
            if i != self.coefs.size - 1:
                print(' + ', end='')
        print(f' = {self.result}')


# Класс описывающий популяцию с методами над ней
class Population:

    def __init__(self, pop_size, gen_size, min, max):
        self.pop_size = pop_size
        self.gen_size = gen_size
        self.min = min
        self.max = max
        self.evolution = 0
        self.chomosomes = self.__generate_chromosomes()

    # метод генерации случайной старотовой популяции хромосом
    def __generate_chromosomes(self):
        chomosomes = []
        for p in range(self.pop_size):
            chromosome = Chromosome(list(np.random.randint(self.min, self.max, self.gen_size)))
            chomosomes.append(chromosome)

        return chomosomes

    # метод нахождения интервалов для выборки хромосом
    @staticmethod
    def __find_suitability(coefs):
        suitability = []
        coefs_sum = 0
        for i in range(len(coefs)):
            coefs[i] = 1 / coefs[i]
            coefs_sum += coefs[i]
        for coef in coefs:
            suitability.append(coef / coefs_sum)
        for i in range(1, len(suitability)):
            suitability[i] += suitability[i - 1]

        return suitability

    def print(self):
        print("-----------------")
        for i, c in enumerate(self.chomosomes):
            print(f'Chromosome: {i}, gens: {c.gens}')

    @staticmethod
    def __get_parent(suitability, exclude=-1):
        while True:
            r = random.uniform(0, 1)
            left = 0
            for i, s in enumerate(suitability):
                if left <= r < s:
                    if i != exclude:
                        return i
                left = s

    # метод эволюции хромосом
    def evolute(self, coefs, debug):
        suitability = self.__find_suitability(coefs)
        new_chromosomes = []
        for _ in range(self.pop_size):
            parent_1 = self.__get_parent(suitability)
            parent_2 = self.__get_parent(suitability, parent_1)
            new_chromosomes.append(Chromosome.merge(self.chomosomes[parent_1], self.chomosomes[parent_2]))

        self.evolution += 1
        if debug:
            print(f'Evolution number: {self.evolution}')
            self.print()
        self.chomosomes = new_chromosomes

    # метод мутации, меняет случайный ген
    def mutate(self):
        for i in range(self.pop_size):
            j = random.randint(0, self.gen_size - 1)
            gen = random.randint(self.min, self.max - 1)
            self.chomosomes[i].gens[j] = gen


# Класс описывающий хромосому
class Chromosome:

    def __init__(self, gens):
        self.gens = gens

    # метод создания новых хромосом на основе родительской
    @staticmethod
    def merge(parent_1, parent_2):
        if len(parent_1.gens) != len(parent_2.gens):
            # количество генов различается
            raise AssertionError(len(parent_1.gens), len(parent_2.gens))
        # получаем точку разделения
        crossover = random.randint(1, len(parent_2.gens) - 1)
        new_gens = []
        for i in range(len(parent_1.gens)):
            if i < crossover:
                new_gens.append(parent_1.gens[i])
            else:
                new_gens.append(parent_2.gens[i])

        return Chromosome(new_gens)


# класс решающий линейные диофантовые уравнения
class GeneticDiofant:

    @staticmethod
    def find(diofant: DiofantEquation, iterations=100, pop_size=10, debug=False):
        gen_size = diofant.arg_count
        # генерируем начальную популяцию хромосом
        population = Population(pop_size, gen_size, diofant.arg_min, np.ceil(diofant.result / diofant.arg_count))

        if debug:
            print("Initial population")
            population.print()

        for i in range(iterations):
            coefs = []
            if population.evolution % 5 == 0:
                population.mutate()
                if debug:
                    print("After mutation")
                    population.print()
            for chromosome in population.chomosomes:
                coef = diofant.calculate(chromosome.gens)
                coefs.append(coef)
                if coef == 0:
                    print(f'Total evolution count: {population.evolution}')
                    return chromosome.gens
            population.evolute(coefs, debug)
        return []


if __name__ == '__main__':
    equation = DiofantEquation(10, debug=True)
    equation.print()

    answer = GeneticDiofant.find(equation, iterations=100000)
    print(f'Chromosome: {answer}')
