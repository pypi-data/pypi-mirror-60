import numpy as np
from ctypes import c_double
# tons of thanks to
# https://stackoverflow.com/questions/31282764/when-subclassing-a-numpy-ndarray-how-can-i-modify-getitem-properly
# and https://docs.scipy.org/doc/numpy/user/basics.subclassing.html


class TsArray(np.ndarray):
    def __new__(cls, data, time=None):
        obj = np.asarray(data).view(cls)
        obj.time = np.asarray(time, dtype=c_double)  # TODO: make time dtype flexible?
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.time = getattr(obj, 'time', None)
        try:
            self.time = self.time[obj._new_time_index]
        except:
            pass

    def copy(self, **kwargs):
        #self._new_time_index = slice(None, None, None)
        new_array = super(TsArray, self).copy(**kwargs)
        new_array = TsArray(new_array, time=self.time.copy())
        return new_array

    def __getitem__(self, item):
        try:
            if isinstance(item, (slice, int)):
                self._new_time_index = item
            else:
                self._new_time_index = item[0]
        except:
            pass
        return super(TsArray, self).__getitem__(item)


def atleast_nd(x, n):
    # https://stackoverflow.com/a/43871605
    return np.array(x, ndmin=n, subok=True, copy=False)


def stack(tup):
    """Stack TsArrays in sequence vertically (rowwise).

    This also preserves and stacks the time attribute of the TsArray inputs.
    """
    times = np.concatenate([np.atleast_1d(x.time) for x in tup if x is not None], axis=0)
    not_none = [t for t in tup if t is not None]
    max_dims = max([len(t.shape) for t in not_none])
    return TsArray(np.concatenate([atleast_nd(t, max_dims) for t in not_none], axis=0),
                   time=times)
