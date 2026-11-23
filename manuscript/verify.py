import json
from itertools import combinations, product
from pathlib import Path


VARIABLES = ('a', 'b', 'y0', 'y1', 'y2')
ZERO = {}
ONE = {(0,) * len(VARIABLES): 1}


def constant(value):
    return {(0,) * len(VARIABLES): value} if value else {}


def monomial(coefficient=1, **powers):
    return {tuple(powers.get(name, 0) for name in VARIABLES): coefficient}


def add(left, right):
    result = dict(left)
    for powers, coefficient in right.items():
        result[powers] = result.get(powers, 0) + coefficient
        if result[powers] == 0:
            del result[powers]
    return result


def multiply(left, right):
    result = {}
    for left_powers, left_coefficient in left.items():
        for right_powers, right_coefficient in right.items():
            powers = tuple(first + second for first, second in zip(left_powers, right_powers))
            result = add(result, {powers: left_coefficient * right_coefficient})
    return result


def matrix_multiply(left, right):
    result = []
    for row in range(3):
        output_row = []
        for column in range(3):
            entry = {}
            for middle in range(3):
                entry = add(entry, multiply(left[row][middle], right[middle][column]))
            output_row.append(entry)
        result.append(tuple(output_row))
    return tuple(result)


IDENTITY = tuple(tuple(ONE if row == column else ZERO for column in range(3)) for row in range(3))


def local(block, position):
    return tuple(tuple(block[row - position][column - position]
                       if position <= row <= position + 1 and position <= column <= position + 1
                       else ONE if row == column else ZERO
                       for column in range(3)) for row in range(3))


def relations(color_count):
    result = []
    for position in range(2):
        twin = ('s', position)
        result.append(('11', (twin, twin), ()))
        for color in range(color_count):
            virtual = ('r', position, color)
            result.append(('13', (virtual, virtual), ()))
    for color in range(color_count):
        left, right = ('r', 0, color), ('r', 1, color)
        result.append(('16', (left, right, left), (right, left, right)))
        result.append(('19', (left, right, ('s', 0)), (('s', 1), left, right)))
    for lower, upper in combinations(range(color_count), 2):
        first_lower, second_lower = ('r', 0, lower), ('r', 1, lower)
        first_upper, second_upper = ('r', 0, upper), ('r', 1, upper)
        result.append(('17', (first_lower, second_upper, first_upper),
                       (second_upper, first_upper, second_lower)))
        result.append(('18', (first_lower, second_lower, first_upper),
                       (second_upper, first_lower, second_lower)))
    return result


def matrix_word(word, images):
    result = IDENTITY
    for letter in word:
        result = matrix_multiply(result, images[letter])
    return result


def reduced(word):
    result = []
    for letter in word:
        if result and result[-1] == letter:
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def permutation_multiply(left, right):
    return tuple(left[right[index]] for index in range(4))


def permutation_word(word, images):
    result = tuple(range(4))
    for letter in word:
        result = permutation_multiply(result, images[letter])
    return result


def reduced_signed(word):
    result = []
    for letter in word:
        if result and result[-1] == -letter:
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def even_coordinates(word):
    assert len(word) % 2 == 0
    coordinates = []
    for index in range(0, len(word), 2):
        first, second = word[index:index + 2]
        if first:
            coordinates.append(-first)
        if second:
            coordinates.append(second)
    return reduced_signed(coordinates)


def color_kernel_controls(images):
    count = 0
    even_count = 0
    for length in range(9):
        for word in product(range(3), repeat=length):
            if any(left == right for left, right in zip(word, word[1:])):
                continue
            count += 1
            image = matrix_word(tuple(('r', 0, color) for color in word), images)
            if length % 2:
                assert image != IDENTITY
                assert image[0][0] == ZERO and image[1][1] == ZERO
                continue
            even_count += 1
            coordinates = even_coordinates(word)
            expanded = []
            for letter in coordinates:
                expanded.extend((0, letter) if letter > 0 else (-letter, 0))
            assert reduced(expanded) == word
            exponents = tuple(coordinates.count(color) - coordinates.count(-color)
                              for color in [1, 2])
            parameter_powers = {'y0': -sum(exponents), 'y1': exponents[0], 'y2': exponents[1]}
            inverse_powers = {name: -exponent for name, exponent in parameter_powers.items()}
            expected = ((monomial(**parameter_powers), ZERO, ZERO),
                        (ZERO, monomial(**inverse_powers), ZERO),
                        (ZERO, ZERO, ONE))
            assert image == expected
            assert (image == IDENTITY) == (exponents == (0, 0))
    assert count == 766 and even_count == 511
    return {'colors': 3, 'maximum_reduced_length': 8, 'reduced_words': count,
            'even_words': even_count, 'odd_words': count - even_count,
            'identity_condition': 'Even parity and zero exponent sums for independent Laurent variables'}


def welded_controls():
    twin_block = ((ZERO, monomial(b=-1)), (monomial(b=1), ZERO))
    images = {('s', position): local(twin_block, position) for position in range(2)}
    for color in range(3):
        block = ((ZERO, monomial(**{f'y{color}': -1})),
                 (monomial(**{f'y{color}': 1}), ZERO))
        for position in range(2):
            images[('r', position, color)] = local(block, position)
    source_relations = relations(3)
    extra_relations = [('welded', (('r', 0, color), ('s', 1), ('s', 0)),
                        (('s', 1), ('s', 0), ('r', 1, color))) for color in range(3)]
    for label, left, right in source_relations + extra_relations:
        assert matrix_word(left, images) == matrix_word(right, images), label
        def project(word):
            return reduced(tuple(-1 if letter[0] == 's' else letter[2] for letter in word))
        assert project(left) == project(right), label
    first = (('s', 0), ('r', 0, 0))
    second = (('s', 0), ('r', 0, 1))
    word = first + second + first[::-1] + second[::-1]
    assert matrix_word(word, images) == IDENTITY
    projected = tuple(-1 if letter[0] == 's' else letter[2] for letter in word)
    for exponent in range(1, 21):
        assert reduced(projected * exponent) == (-1,) + (0, -1, 1) * (2 * exponent) + (-1,)
    return {'matrix_equalities_k3_n3': len(source_relations + extra_relations),
            'twin_block': 'R(b)', 'virtual_blocks': 'R(y_alpha)',
            'commutator': '[s1 rho_1^0,s1 rho_1^1]', 'commutator_matrix': 'I3',
            'reduced_power_exponents': [1, 20]}


def run():
    twin_block = ((monomial(-1, a=1), add(monomial(-1, a=2, b=-1), monomial(b=-1))),
                  (monomial(b=1), monomial(a=1)))
    images = {('s', position): local(twin_block, position) for position in range(2)}
    for color in range(3):
        block = ((ZERO, monomial(**{f'y{color}': -1})),
                 (monomial(**{f'y{color}': 1}), ZERO))
        for position in range(2):
            images[('r', position, color)] = local(block, position)
    source_relations = relations(3)
    for label, left, right in source_relations:
        assert matrix_word(left, images) == matrix_word(right, images), label
    for color_count in range(1, 9):
        for label, left, right in relations(color_count):
            left_colors = tuple(letter[2] for letter in left if letter[0] == 'r')
            right_colors = tuple(letter[2] for letter in right if letter[0] == 'r')
            assert reduced(left_colors) == reduced(right_colors), (color_count, label)
    generators = tuple(('r', 0, color) for color in range(3))
    first, second = generators[:2], (generators[0], generators[2])
    word = first + second + first[::-1] + second[::-1]
    assert matrix_word(word, images) == IDENTITY
    for color in [1, 2]:
        expected = ((monomial(y0=-1, **{f'y{color}': 1}), ZERO, ZERO),
                    (ZERO, monomial(y0=1, **{f'y{color}': -1}), ZERO),
                    (ZERO, ZERO, ONE))
        assert matrix_word((generators[0], generators[color]), images) == expected
    swaps = ((1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2))
    permutation_images = {('s', position): tuple(range(4)) for position in range(2)}
    permutation_images.update({('r', position, color): swaps[color]
                               for position in range(2) for color in range(3)})
    for label, left, right in source_relations:
        assert permutation_word(left, permutation_images) == permutation_word(right, permutation_images), label
    detected = permutation_word(word, permutation_images)
    assert detected == (2, 3, 0, 1)
    color_word = tuple(letter[2] for letter in word)
    for exponent in range(1, 21):
        expected = (0,) + (1, 0, 2) * (2 * exponent) + (0,)
        assert reduced(color_word * exponent) == expected
    ratio_diagonal = matrix_word(generators[:2], images)
    current = IDENTITY
    for exponent in range(1, 21):
        current = matrix_multiply(current, ratio_diagonal)
        assert current == ((monomial(y0=-exponent, y1=exponent), ZERO, ZERO),
                           (ZERO, monomial(y0=exponent, y1=-exponent), ZERO),
                           (ZERO, ZERO, ONE))
    result = {
        'status': 'pass',
        'arithmetic': 'Exact integer coefficients in Z[a,b^(-1),b,y0^(-1),y0,y1^(-1),y1,y2^(-1),y2]',
        'source': 'arXiv:2605.13090v1, Section 3 equations (11)-(19), Theorem 4.1(8)',
        'matrix_relations_k3_n3': len(source_relations),
        'far_relations': 'No instances of (12), (14), (15) for n=3',
        'quotient_relation_color_range': [1, 8],
        'permutation_relation_count': len(source_relations),
        'commutator_permutation': list(detected),
        'commutator_matrix': 'I3 as a Laurent-polynomial identity',
        'power_controls': list(range(1, 21)),
        'color_kernel_controls': color_kernel_controls(images),
        'welded_controls': welded_controls(),
        'proof_scope': 'Exact color-subgroup kernel, all-color statements, infinite order, subgroup restrictions, all eight families and welded consequences have written proofs in note.tex; the accompanying enumerations have the finite ranges specified above'
    }
    return result


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
