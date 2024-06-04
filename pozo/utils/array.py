import numpy as np
import pandas as pd
import polars as pl
import math
import pint
import hashlib
import pozo
from pozo.drawable import Drawable
from .language import _, _d
from .docs import doc


@doc(
    _d("""summarize_array has one parameter, this return dictionary with info about
 start, stop, step, size and sample_rate_consistent from the depth intervals""")
)
def summarize_array(depth):
    if not is_array(depth):
        raise ValueError(_("You must use for depth a list, tuple or an numpy array"))
    try:
        if False in isfinite(depth):
            raise ValueError(
                _("You mustn't use float('inf'), -float('inf') and/or float('nan')")
            )
    except TypeError:
        if isfinite(depth).eq(False).any():
            raise ValueError(
                _("You mustn't use float('inf'), -float('inf') and/or float('nan')")
            )

    starts = []
    stops = []
    steps = []
    sample_rate_consistent_list = []
    sample = (
        depth.iloc[1] - depth.iloc[0] if hasattr(depth, "iloc") else depth[1] - depth[0]
    )

    for i in range(len(depth) - 1):
        if hasattr(depth, "iloc"):
            if depth.iloc[i] == depth.iloc[-1]:
                break
        elif depth[i] == depth[-1]:
            break

        start = depth.iloc[i] if hasattr(depth, "iloc") else depth[i]
        stop = depth.iloc[i + 1] if hasattr(depth, "iloc") else depth[i + 1]
        sample_rate_consistent = is_close(sample, stop - start, rel_tol=0.0001)
        step = stop - start if sample_rate_consistent else None
        if step == 0:
            step = 0.0001

        starts.append(start)
        stops.append(stop)
        steps.append(step)
        sample_rate_consistent_list.append(sample_rate_consistent)

    is_none = np.vectorize(lambda x: x is None)

    interval = {
        "start": np.array(starts),
        "stop": np.array(stops),
        "step": np.array(steps) if not is_none(np.array(steps)).any() else None,
        "sample_rate_consistent": False not in sample_rate_consistent_list,
    }

    return interval


@doc(
    _d("""is_close has 4 parameters, this return a boolean value that verify the cosistent
 from the depth data""")
)
def is_close(a, b, **kwargs):
    rel_tol = kwargs.pop("rel_tol", 1e-9)
    abs_tol = kwargs.pop("abs_tol", 0)
    return math.isclose(a=a, b=b, rel_tol=rel_tol, abs_tol=abs_tol)


@doc(_d("""hash_array has one parameter, this return a hash from the depth data"""))
def hash_array(depth):
    if hasattr(depth, "tobytes"):
        return hashlib.md5(str((depth.tobytes())).encode()).hexdigest()
    elif is_array(depth):
        depth_array = np.array(depth)
        return hashlib.md5(str((depth_array.tobytes())).encode()).hexdigest()
    else:
        raise ValueError(_("You must use for depth a list, tuple or an numpy array"))


@doc(
    _d("""is_array use the input data to verify if is pint data or other type that has
 __len__ and return a boolean. Be careful with this, it will return true for Pozo objects.
 Taken by the principal __ini__.py """)
)
def is_array(value):
    if isinstance(
        value, (pozo.Track, pozo.Trace, pozo.Axis, pozo.Graph, Drawable, pozo.Note)
    ):
        raise ValueError(_("You mustn't use pozo objects for this function"))

    if isinstance(value, str):
        return False
    if isinstance(value, pint.Quantity):
        return is_array(value.magnitude)
    return hasattr(value, "__len__")


@doc(
    _d("""verify_array_len use three inputs to verify the lenght in the data
 Taken by the principal __ini__.py""")
)
def verify_array_len(constant, data):
    if is_array(constant) and len(constant) != len(data):
        return False
    return True


@doc(
    _d("""check_numpy verify if numpy is at the global scope, so this function try to
 import it, but if you do not have this installed, raise an import error""")
)
def check_numpy():
    if "np" not in (globals(), locals()):
        try:
            globals()["np"] = __import__("numpy")
        except ImportError:
            raise ImportError(
                _("Please install numpy. It must be installed like: pip install numpy")
            )


@doc(
    _d("""check_pandas verify if pandas is at the global scope, so this function try to
 import it, but if you do not have this installed, raise an import error""")
)
def check_pandas():
    if "pd" not in (globals(), locals()):
        try:
            globals()["pd"] = __import__("pandas")
        except ImportError:
            raise ImportError(
                _(
                    "Please install pandas. It must be installed like: pip install pandas"
                )
            )


@doc(
    _d("""check_polars verify if polars is at the global scope, so this function try to
 import it, but if you do not have this installed, raise an import error""")
)
def check_polars():
    if "pl" not in (globals(), locals()):
        try:
            globals()["pl"] = __import__("polars")
        except ImportError:
            raise ImportError(
                _(
                    "Please install polars. It must be installed like: pip install polars"
                )
            )


@doc(
    _d("""check_xarray verify if xarray is at the global scope, so this function try to
 import it, but if you do not have this installed, raise an import error""")
)
def check_xarray():
    if "xr" not in (globals(), locals()):
        try:
            globals()["xr"] = __import__("xarray")
        except ImportError:
            raise ImportError(
                _(
                    "Please install xarray. It must be installed like: pip install xarray"
                )
            )


@doc(_d("""min use 1 parameter to find the min value"""))
def min(data):
    if hasattr(data, "nan_min"):
        return data.nan_min()
    elif hasattr(data, "min"):
        try:
            return data.min(skipna=True)
        except TypeError:
            check_numpy()
            return np.nanmin(data)
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.nanmin(data)
        except TypeError:
            raise TypeError(
                _(
                    "Pozo does not support this object for this function. Please try with list, tuple, numpy array, pandas Series or polars Series"
                )
            )


@doc(_d("""min use 1 parameter to find the max value"""))
def max(data):
    if hasattr(data, "nan_max"):
        return data.nan_max()
    elif hasattr(data, "max"):
        try:
            return data.max(skipna=True)
        except TypeError:
            check_numpy()
            return np.nanmax(data)
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.nanmax(data)
        except TypeError:
            raise TypeError(
                _(
                    "Pozo does not support this object for this function. Please try with list, tuple, numpy array, pandas Series or polars Series"
                )
            )


@doc(_d("""abs use 1 parameter to calculate the absolute value"""))
def abs(data):
    if hasattr(data, "abs"):
        return data.abs()
    elif hasattr(data, "coords"): #xarray
        return np.fabs(data)
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.absolute(data)
        except ValueError:
            raise ValueError(
                _(
                    "Pozo does not support this object for this function. Please try with list, tuple, numpy array, pandas Series or polars Series"
                )
            )


@doc(
    _d("""isfinite use 1 parameter to return boolean value, this verify if the
       data has finite value""")
)
def isfinite(data):
    if hasattr(data, "is_finite"):
        return data.is_finite()
    elif hasattr(data, "isin"):
        return ~data.isin([np.inf, -np.inf, float("nan")])
    elif hasattr(data, "coords"): #xarray
        return np.isfinite(data.values)
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.isfinite(data)
        except ValueError:
            raise ValueError(
                _(
                    "Pozo does not support this object for this function. Please try with list, tuple, numpy array, pandas Series or polars Series"
                )
            )


@doc(
    _d("""isnan use 1 parameter to return boolean value, this verify if the
       data has NaN value""")
)
def isnan(data):
    if hasattr(data, "coords"): #xarray
        return data.isnull()
    elif hasattr(data, "isnull"):
        return data.isnull().any()
    elif hasattr(data, "is_null"):
        return data.is_null()
    elif hasattr(data, "null_count"):
        return data.null_count() > 0
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.isnan(data)
        except ValueError:
            raise ValueError(
                _(
                    "Pozo does not support this object for this function. Please try with list, tuple, numpy array, pandas Series or polars Series"
                )
            )


@doc(
    _d(
        """count_nonzero use 1 parameter to return how many numbers are greater than 0"""
    )
)
def count_nonzero(data):
    if hasattr(data, "coords"): #xarray
        return np.count_nonzero(data.values)
    elif hasattr(data, "isnull"):
        return np.count_nonzero(data.to_numpy())
    elif hasattr(data, "is_null"):
        print(np.count_nonzero(data.to_numpy()))
        return np.count_nonzero(data.to_numpy()) #EN DESARROLLO
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.count_nonzero(data)
        except ValueError:
            raise ValueError(
                _(
                    "Pozo does not support this object for this function. Please try with list, tuple, numpy array, pandas Series or polars Series"
                )
            )


def nanquantile(data, q, axis=None):
    if hasattr(data, "coords"): #xarray
        return np.nanquantile(data.values, q=q)
    elif hasattr(data, "isnull"):
        return data.quantile(q)
    elif hasattr(data, "is_null"):
        return data.quantile(q, interpolation="linear")
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.nanquantile(data, q=q, axis=axis)
        except ValueError:
            raise ValueError(
                _(
                    "Pozo does not support this object for this function. Please try with list, tuple, numpy array, pandas Series or polars Series"
                )
            )


def round(data, decimals=0):
    if hasattr(data, "coords"): #xarray
        return data.values.round(decimals=decimals)
    elif hasattr(data, "round"): #series and array
        return data.round(decimals=decimals)
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return data.round(decimals=decimals)
        except ValueError:
            raise ValueError(
                _(
                    "Pozo does not support this object for this function. Please try with list, tuple, numpy array, pandas Series or polars Series"
                )
            )


@doc(
    _d(
        """append use 2 parameters, this return one object with the original data and the arg that you want to add"""
    )
)
def append(data, arg):
    arg_obj = isinstance(arg, (list, tuple, int, float))
    if hasattr(data, "coords"): #xarray
        check_numpy()
        if arg_obj or arg.dtype != data.dtype:
            arg = np.array(arg, dtype=data.dtype)
        return np.append(data.values, arg)
    elif hasattr(data, "concat"):
        check_pandas()
        if arg_obj or arg.dtype != data.dtype:
            arg = np.array(arg, dtype=data.to_numpy().dtype)
        return pd.concat([data, pd.Series(arg)], ignore_index=True)
    elif hasattr(data, "is_null"):
        check_polars()
        if arg_obj or arg.dtype != data.dtype:
            arg = np.array(arg, dtype=data.to_numpy().dtype)
        return data.append(pl.Series(arg))
    else:
        check_numpy()
        if isinstance(data, (list, tuple, int, float)):
            data = np.array(data)
        if arg_obj or arg.dtype != data.dtype:
            arg = np.array(arg, dtype=data.dtype)
        try:
            return np.append(data, arg)
        except ValueError:
            raise ValueError(
                _(
                    "Pozo does not support this object for this function. Please try with list, tuple, numpy array, pandas Series or polars Series"
                )
            )
