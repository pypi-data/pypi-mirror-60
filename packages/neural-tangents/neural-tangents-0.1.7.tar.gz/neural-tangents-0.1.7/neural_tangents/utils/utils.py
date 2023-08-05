# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""General-purpose internal utilities."""

from collections import namedtuple
import functools
import inspect
import types
from jax.lib import xla_bridge
import jax.numpy as np


def canonicalize_get(get):
  if get is None:
    return True, get

  if not get:
    # NOTE(schsam): It seems slightly nicer to not support the empty-tuple
    # case. Happy to add support later, if there's a use-case.
    raise ValueError('"get" must be non-empty.')

  get_is_not_tuple = isinstance(get, str)
  if get_is_not_tuple:
    get = (get,)

  get = tuple(s.lower() for s in get)
  if len(set(get)) < len(get):
    raise ValueError('All entries in "get" must be unique. Got {}'.format(get))
  return get_is_not_tuple, get


_KERNEL_NAMED_TUPLE_CACHE = {}


def named_tuple_factory(name, get):
  key = (name, get)
  if key in _KERNEL_NAMED_TUPLE_CACHE:
    return _KERNEL_NAMED_TUPLE_CACHE[key]
  else:
    _KERNEL_NAMED_TUPLE_CACHE[key] = namedtuple(name, get)
    return named_tuple_factory(name, get)


def _output_to_dict(output):
  if isinstance(output, dict):
    return output

  if hasattr(output, '_asdict'):
    return output._asdict()

  if isinstance(output, types.GeneratorType):
    return (_output_to_dict(out) for out in output)

  raise ValueError(type(output))


def wraps(f,
          assigned=functools.WRAPPER_ASSIGNMENTS,
          updated=functools.WRAPPER_UPDATES):
  def wrapper(g):
    @functools.wraps(f, assigned, updated)
    def h(*args, **kwargs):
      return g(*args, **kwargs)
    h.__signature__ = inspect.signature(f)
    return h
  return wrapper


def get_namedtuple(name):
  def getter_decorator(fn):
    try:
      argspec = inspect.getfullargspec(fn)
      get_index = argspec.args.index('get')
      defaults = argspec.defaults
    except:
      raise ValueError('`get_namedtuple` functions must have a `get` argument.')

    @wraps(fn)
    def getter_fn(*args, **kwargs):
      canonicalized_args = list(args)

      if 'get' in kwargs:
        get_is_not_tuple, get = canonicalize_get(kwargs['get'])
        kwargs['get'] = get
      elif get_index < len(args):
        get_is_not_tuple, get = canonicalize_get(args[get_index])
        canonicalized_args[get_index] = get
      elif defaults is None:
        raise ValueError(
            '`get_namedtuple` function must have a `get` argument provided or'
            'set by default.')
      else:
        get_is_not_tuple, get = canonicalize_get(defaults[get_index -
                                                          len(args)])

      fn_out = fn(*canonicalized_args, **kwargs)

      if get is None:
        if isinstance(fn_out, dict):
          ReturnType = named_tuple_factory(name, tuple(fn_out.keys()))
          fn_out = ReturnType(*fn_out.values())
        return fn_out

      fn_out = _output_to_dict(fn_out)

      if get_is_not_tuple:
        if isinstance(fn_out, types.GeneratorType):
          return (output[get[0]] for output in fn_out)
        else:
          return fn_out[get[0]]

      ReturnType = named_tuple_factory(name, get)
      if isinstance(fn_out, types.GeneratorType):
        return (ReturnType(*tuple(output[g] for g in get)) for output in fn_out)
      else:
        return ReturnType(*tuple(fn_out[g] for g in get))

    return getter_fn

  return getter_decorator


def x1_is_x2(x1, x2=None, eps=1e-12):
  if xla_bridge.get_backend().platform == 'tpu':
    eps = 1e-4
  if not isinstance(x1, np.ndarray):
    raise TypeError('`x1` must be an ndarray. A {} is found.'.format(type(x1)))
  if x2 is None:
    return True

  if x1 is x2:
    return True

  if x1.shape != x2.shape:
    return False

  return np.all(np.abs(x1 - x2) < eps)
