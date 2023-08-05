import random
from functools import reduce
import math

from cereja.cj_types import Tuple, Any, Sequence, Number, Union, List, Optional
import logging

logger = logging.getLogger(__name__)


def is_iterable(obj: Any) -> bool:
    """
    Return whether an object is iterable or not.

    :param obj: Any object for check
    """
    try:
        iter(obj)
    except TypeError:
        return False
    return True


def is_sequence(obj: Any) -> bool:
    """
    Return whether an object a Sequence or not, exclude strings and empty obj.

    :param obj: Any object for check
    """
    if isinstance(obj, (str, dict)):
        return False

    return is_iterable(obj)


def is_numeric_sequence(obj: Sequence[Number]) -> bool:
    try:
        sum(flatten(obj))
    except (TypeError, ValueError):
        return False
    return True


def theta_angle(u: Tuple[float, float], v: Tuple[float, float]) -> float:
    """
    Calculates and returns theta angle between two vectors

    e.g usage:
    >>> u = (2,2)
    >>> v = (0, -2)
    >>> theta_angle(u, v)
    135.0
    """
    x1, y1 = u
    x2, y2 = v
    return math.degrees(math.acos((x1 * x2 + y1 * y2) / (math.sqrt(x1 ** 2 + y1 ** 2) * math.sqrt(x2 ** 2 + y2 ** 2))))


def prod(sequence: Sequence[Number]) -> Number:
    """
    Calculates the product of the values.

    This function is intended specifically for use with numeric values and may
    reject non-numeric types.

    :param sequence: Is a sequence of numbers.
    :return:
    """
    if not is_sequence(sequence):
        raise TypeError(f"Value of {sequence} is not valid. Please send a numeric list.")

    return reduce((lambda x, y: x * y), sequence)


def shape_is_ok(sequence: Union[Sequence[Any], Any], expected_shape: Tuple[int, ...]) -> bool:
    """
    Check the number of items the array has and compare it with the shape product
    """
    try:
        sequence_len = len(flatten(sequence))
    except ValueError as err:
        logger.info(f"Error when trying to compare shapes. {err}")
        return False
    return prod(expected_shape) == sequence_len


def get_shape(sequence: Sequence[Any]) -> Tuple[Union[int, None], ...]:
    """
    Responsible for analyzing the depth of a sequence

    :param sequence: Is sequence of values.
    :return: number of dimensions
    """
    if not sequence:
        return None,
    wkij = []
    while True:
        if is_sequence(sequence) and sequence:
            wkij.append(len(sequence))
            sequence = sequence[0]
            continue
        return tuple(wkij)


def get_shape_recursive(sequence: Sequence[Any], wki: Tuple[int, ...] = None) -> Tuple[int, ...]:
    """
    [!] Never use recursion in python if it is possible to exceed 997 calls [!]

    [!] Function for teaching purposes [!]

    :param sequence: Is sequence of values.
    :param wki: stores value for each dimension
    """
    if wki is None:
        wki = []
    if is_sequence(sequence):
        wki += [len(sequence)]
        return get_shape_recursive(sequence[0], wki)
    return tuple(wki)


def reshape(sequence: Sequence, shape):
    """
    [!] need development [!]

    :param sequence:
    :param shape:
    :return:
    """

    pass


def array_gen(shape: Tuple[int, ...], v: Union[Sequence[Any], Any] = None) -> List[Union[float, Any]]:
    """
    Generates array based on passed shape

    e.g:
    >>> array_gen(shape=(2, 2, 3))
    [[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]]

    >>>array_gen(shape=(1, 3, 2, 1, 1))
    [[[[[0.0]], [[0.0]]], [[[0.0]], [[0.0]]], [[[0.0]], [[0.0]]]]]

    >>> array_gen(shape=(2, 1, 1),v=['hail','pythonics!'])
    [[['hail']], [['pythonics!']]]

    >>> shape = (2, 1, 1)
    >>> array_gen(shape, v = flatten(array_randn(shape)))
    [[[0.43022826643029777]], [[0.5697717335697022]]]

    :param shape: it's the shape of array
    :param v: sequence or Any obj that allows insertion of values
    :return: Sequence -> List[Union[float, Any]]
    """

    is_seq = is_sequence(v)

    allow_reshape = shape_is_ok(v, shape) and is_seq

    if not is_seq:
        v = [v if v else 0.]

    for k in shape[::-1]:
        if allow_reshape:
            v = group_items_in_batches(v, k)
            continue
        v = [v * k]
    return v[0]


def _flatten(sequence: list, max_recursion: int = -1):
    logger.warning(f"[!] {_flatten.__name__} still under development")
    if not isinstance(max_recursion, int):
        raise TypeError(f"Type {type(max_recursion)} is not valid for max_recursion. Please send integer.")

    if not is_sequence(sequence):
        # Need improve
        if max_recursion < 0:
            raise ValueError(f"Value {sequence} is'nt valid. Send Sequence.")
        return sequence

    if is_sequence(sequence) and max_recursion:
        return sum(map(_flatten, *(sequence, max_recursion - 1)), [])

    return [sequence]


def flatten(sequence: Sequence[Any], max_recursion: Optional[int] = -1) -> Union[List[Any], Any]:
    """
    Receives values, whether arrays of values, regardless of their shape and flatness

    :param sequence: Is sequence of values.
    :param max_recursion: allows you to control a recursion amount, for example if you send a
    sequence=[1,2, [[3]]] and max_recursion=1 your return will be [1, 2, [3]].
    :return: flattened array

    e.g usage:

    >>> sequence = [[1, 2, 3], [], [[2, [3], 4], 6]]
    >>> flatten(sequence)
    [1, 2, 3, 2, 3, 4, 6]
    >>> flatten(sequence, max_recursion=2)
    [1, 2, 3, 2, [3], 4, 6]
    """

    # TODO: Add version without recursion
    if not isinstance(max_recursion, int):
        raise TypeError(f"Type {type(max_recursion)} is not valid for max_recursion. Please send integer.")

    if not is_sequence(sequence):
        # Need improve
        if max_recursion < 0:
            raise ValueError(f"Value {sequence} is'nt valid. Send Sequence.")
        return sequence

    flattened = []
    for obj in sequence:
        if is_sequence(obj) and max_recursion:
            recursive_flattened = flatten(obj, max_recursion - 1)
            for i in recursive_flattened:
                flattened.append(i)
        else:
            flattened.append(obj)
    return flattened


def rand_uniform(_from: Number, to: Number):
    return _from + (to - _from) * random.random()


def rand_n(_from: Number = 0., to: Number = 1., n: int = 1) -> Union[float, List[float]]:
    """
    All values ​​are random and their sum is equal to 1 (default) or the value sent in parameter (to)

    :param _from: start in number
    :param to: stop in number
    :param n: n is length of array
    :return: Sequence of floats

    >>> array = rand_n(_from = 10, to=15, n = 3)
    [13.638625715965802, 1.3384682252134166, 0.022906058820781894]

    >>>sum(flatten(array))
    15
    """
    assert isinstance(n, int) is True, "ValueError: n: int is a integer value."
    assert _from < to, "please send a valid range. The first value must not be greater than the second"

    _to = to
    values = [rand_uniform(_from, to)]
    n = n - 1

    if not n:
        return values[0]  # if n was not sent

    while n:
        to = (_from - to) - values[-1]  # get last
        values.append(rand_uniform(_from, to))
        n -= 1

    # recover to value
    to = _to
    # ensures that the sum of all values ​​is equal to b
    values[-1] = to - sum(values[:-1])
    return values


def array_randn(shape: Tuple[int, ...], *args, **kwargs) -> List[Union[float, Any]]:
    """
    Responsible for creating matrix in the requested form. All values ​​are random and their sum is equal to 1 (
    default) or the value sent in parameter (to)

    :param shape: it's the shape of array
    :param args: Arguments that will be passed on to the auxiliary function rand_n:
                _from: Number = 0.,
                to: Number = 1.,
                n: int = 1
    :return: array with shape that you request

    e.g:

    >>> array = array_randn((1,2,3,4))
    [[[[0.2592981659911938, -0.12315716616964649, 0.82133729291841,
    -0.25879078816834644], [1.3629594254754838, -3.774314741021747, 5.274492839788345, -11.601343746754297],
    [3.604096666087614, -27.650903465459855, 19.296830893462964, -58.83686412036615]], [[69.41859240028415,
    -179.33687885859996, 361.42747499197384, -610.1513132786013], [1072.0398936663296, -894.6318240273097,
    1448.8891836211283, -4183.174313279926], [8139.152167926057, -12466.659181206918, 24595.19100297986,
    -17279.53844619006]]]]

    >>>sum(flatten(array))
    1.0

    >>> cj_randn = array_randn((4,4), _from = 0, to = 20)
    [[10.290409563999265, -10.551079712904698, 2.901380773471479, -27.545318358270105], [11.611327651418236,
    -29.461575728235626, 108.82486378444688, -72.92672196142121], [166.27689950355855, -400.36353360213354,
    575.2273799798464, -1362.4824677079241], [2689.652915457324, -4310.834087972777, 4834.662753875761,
    -2165.28314554616]]

    >>> sum(flatten(cj_randn))
    20.0

    """
    rand_n_values = rand_n(*args, n=prod(shape), **kwargs)
    return array_gen(shape=shape, v=rand_n_values)


def group_items_in_batches(items: List[Any], items_per_batch: int = 0, fill: Any = None) -> List[List[Any]]:
    """
    Responsible for grouping items in batch taking into account the quantity of items per batch

    e.g.
    >>> group_items_in_batches(items=[1,2,3,4], items_per_batch=3)
    [[1, 2, 3], [4]]
    >>> group_items_in_batches(items=[1,2,3,4], items_per_batch=3, fill=0)
    [[1, 2, 3], [4, 0, 0]]

    :param items: list of any values
    :param items_per_batch: number of items per batch
    :param fill: fill examples when items is not divisible by items_per_batch, default is None
    :return:
    """
    items_length = len(items)
    if not isinstance(items_per_batch, int):
        raise TypeError(f"Value for items_per_batch is not valid. Please send integer.")
    if items_per_batch < 0 or items_per_batch > len(items):
        raise ValueError(f"Value for items_per_batch is not valid. I need a number integer between 0 and {len(items)}")
    if items_per_batch == 0:
        return items

    if fill is not None:
        missing = items_per_batch - items_length % items_per_batch
        items += missing * [fill]

    batches = []

    for i in range(0, items_length, items_per_batch):
        batch = [group for group in items[i:i + items_per_batch]]
        batches.append(batch)
    return batches


def remove_duplicate_items(items: Optional[list]) -> Any:
    """
    remove duplicate items in an item list or duplicate items list of list

    e.g usage:
    >>> remove_duplicate_items([1,2,1,2,1])
    [1, 2]
    >>> remove_duplicate_items(['hi', 'hi', 'ih'])
    ['hi', 'ih']

    >>> remove_duplicate_items([['hi'], ['hi'], ['ih']])
    [['hi'], ['ih']]
    >>> remove_duplicate_items([[1,2,1,2,1], [1,2,1,2,1], [1,2,1,2,3]])
    [[1, 2, 1, 2, 1], [1, 2, 1, 2, 3]]
    """
    # TODO: improve function
    if not is_iterable(items) or isinstance(items, str):
        raise TypeError("Send iterable except string.")

    try:
        return list(dict.fromkeys(items))
    except TypeError:
        return sorted([list(item) for item in set(tuple(x) for x in items)], key=items.index)


class ConvertDictError(Exception): pass


class Freq:
    """
    [!] It's still under development [!]

    >>> freq = Freq([1,2,3,3,4,5,6,7,6,7,12,31,123,5,3])
    {3: 3, 5: 2, 6: 2, 7: 2, 1: 1, 2: 1, 4: 1, 12: 1, 31: 1, 123: 1}

    >>> freq.add_item(3)
    {3: 4, 5: 3, 6: 2, 7: 2, 1: 1, 2: 1, 4: 1, 12: 1, 31: 1, 123: 1}

    >>> freq.most_freq(4)
    {3: 3, 5: 2, 6: 2, 7: 2}

    >>> freq.least_freq(1)
    {123: 1}

    >>> freq_str = Freq('My car is red I like red color'.split())
    {'red': 2, 'My': 1, 'car': 1, 'is': 1, 'I': 1, 'like': 1, 'color': 1}
    """

    def __init__(self, data: list):

        logger.warning("[!] class still under development")

        if not is_iterable(data):
            raise ValueError("The data you entered is not valid! Please give me iterable data.")

        self.data = data
        self.freq = self._freq(len(self.data))

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return self.freq.__repr__()

    def _freq(self, max_items: int = None):
        try:
            max_items = max_items or len(self.data)
            values = {item: self.data.count(item) for item in self.data}
            max_items = len(self.data) if max_items > len(self.data) else max_items
            freq = {item: values[item] for i, item in enumerate(sorted(values, key=values.get, reverse=True)) if
                    i < max_items}
        except Exception as err:
            raise ConvertDictError("Cannot convert data to dictionary")
        return freq

    def _verify_query(self, **kwargs):
        max_items = kwargs.get('max_items')
        if max_items:
            if not isinstance(max_items, int):
                raise TypeError(f"Value {max_items} isn't valid. Please give me integer.")

            assert max_items < len(
                self), "Not possible, because the maximum value taked is greater than the number of items."

    def _get_dict_from_keys(self, keys: list):
        return {item: self.freq[item] for item in keys}

    def item(self, item):
        return self.freq[item]

    def most_freq(self, max_items: int):
        self._verify_query(max_items=max_items)
        most = list(self.freq)[:max_items]
        return self._get_dict_from_keys(most)

    def least_freq(self, max_items: int):
        self._verify_query(max_items=max_items)
        less = list(self.freq)[-max_items:]
        return self._get_dict_from_keys(less)

    def add_item(self, item):
        self.data.append(item)
        self.freq = self._freq()

    def remove_item(self, item):
        self.data.remove(item)
        self.freq = self._freq()

    def items(self):
        return self.freq.items()


if __name__ == "__main__":
    pass
