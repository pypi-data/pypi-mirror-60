# -*- coding: utf-8 -*-

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle
from importlib import import_module

from .logger import logger


PICKLE_PROTOCOL_VERSION = pickle.HIGHEST_PROTOCOL
loads = pickle.loads


def dumps(obj):
    return pickle.dumps(obj, PICKLE_PROTOCOL_VERSION)


def set_pickle_protocol_version(version):
    """Set pickle protocol version for serializing and deserializing tasks.
    The default version is pickle.HIGHEST_PROTOCOL.
    You can set it to a lower version for compatibility.

    Args:
        version (int): The pickle protocol version to be set.
    """
    global PICKLE_PROTOCOL_VERSION

    if version > pickle.HIGHEST_PROTOCOL:
        raise ValueError('Unsupported pickle protocol version for current Python runtime')
    PICKLE_PROTOCOL_VERSION = version


def get_pickle_protocol_version():
    """Get the current pickle protocol version.


    Returns:
        int: The current pickle protocol version.
    """
    return PICKLE_PROTOCOL_VERSION


class Task(object):
    """Task is the class of a task.

    Args:
        id (int or None): The task id.
        module_name (str): The module name of the task function.
        func_name (str): The function name of the task function.
        args (list or tuple): Variable length argument list of the task function.
            It should be picklable.
        kwargs (dict): Arbitrary keyword arguments of the task function.
            It should be picklable.
        timeout (int or float): The timeout in seconds of the task.
        prior (bool): A prior task will be inserted at the first position.
    """

    __slots__ = ['_id', '_module_name', '_func_name', '_args', '_kwargs', '_timeout', '_prior', '_data']

    def __init__(self, id, module_name, func_name, args=None, kwargs=None, timeout=None, prior=False):
        self._id = id
        self._module_name = module_name
        self._func_name = func_name
        self._args = () if args is None else args
        self._kwargs = {} if kwargs is None else kwargs
        self._timeout = timeout
        self._prior = prior
        self._data = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = val
        self._data = None

    @property
    def module_name(self):
        return self._module_name

    @property
    def func_name(self):
        return self._func_name

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def timeout(self):
        return self._timeout

    @property
    def prior(self):
        return self._prior

    @property
    def data(self):
        return self._data

    @classmethod
    def create(cls, func, args=None, kwargs=None, timeout=None, prior=False):
        """Create a task.

        Args:
            func (callable): The task function.
                It should be defined in module level (except the `__main__` module).
            args (list or tuple): Variable length argument list of the task function.
                It should be picklable.
            kwargs (dict): Arbitrary keyword arguments of the task function.
                It should be picklable.
            timeout (int or float): The timeout in seconds of the task.
            prior (bool): A prior task will be inserted at the first position.

        Returns:
            Task: The created task.
        """
        if timeout:
            timeout = timeout * 1000
        return cls(None, func.__module__, func.__name__, args, kwargs, timeout, prior)

    def serialize(self):
        """Serializes the task to a string.

        Returns:
            str: The serialized data.
        """
        if self._data is None:
            data = self._id, self._module_name, self._func_name, self._args, self._kwargs, self._timeout, self._prior

            i = 0
            if not self._prior:
                i -= 1
                if self._timeout is None:
                    i -= 1
                    if not self._kwargs:
                        i -= 1
                        if not self._args:
                            i -= 1
            if i < 0:
                data = data[:i]
            self._data = dumps(data)
        return self._data

    @classmethod
    def deserialize(cls, data):
        """Deserialize a task from a string.

        Args:
            data (str): The string to be deserialize.

        Returns:
            Task: The deserialized task.
        """
        task = cls(*loads(data))
        task._data = data
        return task

    def run(self):
        """Runs the task.

        Returns:
            Any: The result of the task function.
        """
        logger.debug('Running task %d.', self.id)
        module = import_module(self._module_name)
        func = getattr(module, self._func_name)
        return func(*self._args, **self._kwargs)
