"""
core.py
written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""


# noinspection PyMethodParameters,PyMethodMayBeStatic,PyProtectedMember
class _Privatize:
    # Initialize instance of _Privatize
    def __init__(self, dtype=None):
        """
        """

        self.dtype = self._process_dtype(dtype)

    # TODO there might be something that already exists in numpy for this
    def _process_dtype(self, dtype):
        _dtype = dtype
        if isinstance(dtype, str):
            dtype = dtype.lower()
            if dtype == 'int':
                _dtype = int

        return _dtype

    def get_value(self, parent):
        return parent._value

    # TODO add check that variable doesn't exist when first writing to it
    def set_value(self, parent, value):
        # If self.dtype is set, check explicitly that the new value matches that type
        if self.dtype is not None and not isinstance(value, self.dtype):
            raise ValueError('must be %s' % self.dtype)

        # Set the new value
        parent._value = value


def privatize(dtype=None):
    """

    Parameters
    ----------
    dtype

    Returns
    -------

    """

    # Initialize _Privatize instance
    obj = _Privatize(dtype=dtype)

    # Return property
    return property(obj.get_value, obj.set_value)
