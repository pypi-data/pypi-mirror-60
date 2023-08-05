// BSD 3-Clause License
//
// Copyright (c) 2019, Doug Davis
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
//    contributors may be used to endorse or promote products derived from
//    this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define HMP_VISIBILITY __attribute__((visibility("default")))

// Python
#include <Python.h>

// NumPy
#include <numpy/arrayobject.h>

// OpenMP
#include <omp.h>

// C++ STL
#include <cstdlib>
#include <vector>

extern "C" {

static PyObject* f1dw(PyObject* self, PyObject* args);
static PyObject* v1dw(PyObject* self, PyObject* args);
static PyObject* omp_gmt(PyObject* self, PyObject* args);

static PyMethodDef module_methods[] = {
    {"_f1dw", f1dw, METH_VARARGS, ""},
    {"_v1dw", v1dw, METH_VARARGS, ""},
    {"_omp_get_max_threads", omp_gmt, METH_NOARGS, ""},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef moduledef = {PyModuleDef_HEAD_INIT,
                                       "_CPP",
                                       "Backend C++ module",
                                       -1,
                                       module_methods,
                                       NULL,
                                       NULL,
                                       0,
                                       NULL};

HMP_VISIBILITY PyObject* PyInit__CPP(void);
HMP_VISIBILITY PyObject* PyInit__CPP(void) {
  PyObject* m = PyModule_Create(&moduledef);
  import_array();
  return m;
}

}  // extern "C"

enum class Status {
  SUCCESS = 0,
  ERROR = 1,
};

template <typename T1, typename T2, typename T3>
inline T2 get_bin(T1 x, T2 nbins, T3 xmin, T3 xmax, T3 norm) {
  if (x < xmin) {
    return static_cast<T2>(0);
  }
  else if (x >= xmax) {
    return nbins - 1;
  }
  return static_cast<T2>((x - xmin) * norm * nbins);
}

template <typename T1, typename T2, typename T3>
inline T2 get_bin(T1 x, T2 nbins, T3 xmin, T3 norm) {
  return static_cast<T2>((x - xmin) * norm * nbins);
}

template <typename T1, typename T2>
inline T2 get_bin(T1 x, T2 nbins, const std::vector<double>& edges) {
  if (x < edges.front()) {
    return static_cast<T2>(0);
  }
  else if (x >= edges.back()) {
    return nbins - 1;
  }
  else {
    auto s = static_cast<T2>(std::distance(
        std::begin(edges), std::lower_bound(std::begin(edges), std::end(edges), x)));
    return s - 1;
  }
}

template <typename T1>
inline int get_bin(T1 x, const std::vector<double>& edges) {
  auto s = static_cast<int>(std::distance(
      std::begin(edges), std::lower_bound(std::begin(edges), std::end(edges), x)));
  return s - 1;
}

template <typename T1, typename T2>
inline void fixed_fill_include_flow(const T1* x, const T2* w, T2* counts, T2* vars,
                                    long nx, int nbins, double xmin, double xmax,
                                    double norm) {
  Py_BEGIN_ALLOW_THREADS;
#pragma omp parallel
  {
    std::vector<T2> counts_ot(nbins, 0.0);
    std::vector<T2> vars_ot(nbins, 0.0);
    int bin;
    T2 weight;
#pragma omp for nowait
    for (long i = 0; i < nx; ++i) {
      bin = get_bin(x[i], nbins, xmin, xmax, norm);
      weight = w[i];
      counts_ot[bin] += weight;
      vars_ot[bin] += weight * weight;
    }
#pragma omp critical
    for (int i = 0; i < nbins; ++i) {
      counts[i] += counts_ot[i];
      vars[i] += vars_ot[i];
    }
  }
  Py_END_ALLOW_THREADS;
}

template <typename T1, typename T2>
inline void fixed_fill_exclude_flow(const T1* x, const T2* w, T2* counts, T2* vars,
                                    long nx, int nbins, double xmin, double xmax,
                                    double norm) {
  Py_BEGIN_ALLOW_THREADS;
#pragma omp parallel
  {
    std::vector<T2> counts_ot(nbins, 0.0);
    std::vector<T2> vars_ot(nbins, 0.0);
    int bin;
    T2 weight;
#pragma omp for nowait
    for (long i = 0; i < nx; ++i) {
      if (x[i] < xmin) {
        continue;
      }
      else if (x[i] >= xmax) {
        continue;
      }
      else {
        bin = get_bin(x[i], nbins, xmin, norm);
        weight = w[i];
        counts_ot[bin] += weight;
        vars_ot[bin] += weight * weight;
      }
    }
#pragma omp critical
    for (int i = 0; i < nbins; ++i) {
      counts[i] += counts_ot[i];
      vars[i] += vars_ot[i];
    }
  }
  Py_END_ALLOW_THREADS;
}

template <typename T1, typename T2, typename T3>
inline void var_fill_include_flow(const T1* x, const T2* w, T2* counts, T2* vars,
                                  long nx, const std::vector<T3>& edges) {
  int nbins = static_cast<int>(edges.size()) - 1;
  Py_BEGIN_ALLOW_THREADS;
#pragma omp parallel
  {
    std::vector<T2> counts_ot(nbins, 0.0);
    std::vector<T2> vars_ot(nbins, 0.0);
    int bin;
    T2 weight;
#pragma omp for nowait
    for (long i = 0; i < nx; ++i) {
      bin = get_bin(x[i], nbins, edges);
      weight = w[i];
      counts_ot[bin] += weight;
      vars_ot[bin] += weight * weight;
    }
#pragma omp critical
    for (int i = 0; i < nbins; ++i) {
      counts[i] += counts_ot[i];
      vars[i] += vars_ot[i];
    }
  }
  Py_END_ALLOW_THREADS;
}

template <typename T1, typename T2, typename T3>
inline void var_fill_exclude_flow(const T1* x, const T2* w, T2* counts, T2* vars,
                                  long nx, const std::vector<T3>& edges) {
  int nbins = static_cast<int>(edges.size()) - 1;
  Py_BEGIN_ALLOW_THREADS;
#pragma omp parallel
  {
    std::vector<T2> counts_ot(nbins, 0.0);
    std::vector<T2> vars_ot(nbins, 0.0);
    int bin;
    T2 weight;
#pragma omp for nowait
    for (long i = 0; i < nx; ++i) {
      if (x[i] < edges.front()) {
        continue;
      }
      else if (x[i] >= edges.back()) {
        continue;
      }
      else {
        bin = get_bin(x[i], edges);
        weight = w[i];
        counts_ot[bin] += weight;
        vars_ot[bin] += weight * weight;
      }
    }
#pragma omp critical
    for (int i = 0; i < nbins; ++i) {
      counts[i] += counts_ot[i];
      vars[i] += vars_ot[i];
    }
  }
  Py_END_ALLOW_THREADS;
}

template <typename T>
inline void var_to_err(PyArrayObject* var, int nbins) {
  T* arr = (T*)PyArray_DATA(var);
  for (int i = 0; i < nbins; ++i) {
    arr[i] = sqrt(arr[i]);
  }
}

inline Status calc_err(PyArrayObject* var, int nbins) {
  if (PyArray_TYPE(var) == NPY_FLOAT64) {
    var_to_err<double>(var, nbins);
    return Status::SUCCESS;
  }
  if (PyArray_TYPE(var) == NPY_FLOAT32) {
    var_to_err<float>(var, nbins);
    return Status::SUCCESS;
  }
  return Status::ERROR;
}

#define FILL_CALL_FIXED(IS1, IS2, T1, T2, suffix)                                     \
  do {                                                                                \
    if (x_is_##IS1 && w_is_##IS2) {                                                   \
      fixed_fill_##suffix<T1, T2>((const T1*)PyArray_DATA(x),                         \
                                  (const T2*)PyArray_DATA(w), (T2*)PyArray_DATA(c),   \
                                  (T2*)PyArray_DATA(v), nx, nbins, xmin, xmax, norm); \
      return Status::SUCCESS;                                                         \
    }                                                                                 \
  } while (0)

#define FILL_CALL_VAR(IS1, IS2, T1, T2, suffix)                                   \
  do {                                                                            \
    if (x_is_##IS1 && w_is_##IS2) {                                               \
      var_fill_##suffix<T1, T2>((const T1*)PyArray_DATA(x),                       \
                                (const T2*)PyArray_DATA(w), (T2*)PyArray_DATA(c), \
                                (T2*)PyArray_DATA(v), nx, edges);                 \
      return Status::SUCCESS;                                                     \
    }                                                                             \
  } while (0)

#define CHECK_TYPES                                   \
  bool x_is_float64 = PyArray_TYPE(x) == NPY_FLOAT64; \
  bool x_is_float32 = PyArray_TYPE(x) == NPY_FLOAT32; \
  bool x_is_uint32 = PyArray_TYPE(x) == NPY_UINT32;   \
  bool x_is_int32 = PyArray_TYPE(x) == NPY_INT32;     \
  bool x_is_uint64 = PyArray_TYPE(x) == NPY_UINT64;   \
  bool x_is_int64 = PyArray_TYPE(x) == NPY_INT64;     \
  bool w_is_float64 = PyArray_TYPE(w) == NPY_FLOAT64; \
  bool w_is_float32 = PyArray_TYPE(w) == NPY_FLOAT32

static Status fill_f1dw_include_flow(PyArrayObject* x, PyArrayObject* w,
                                     PyArrayObject* c, PyArrayObject* v, long nx,
                                     int nbins, double xmin, double xmax) {
  CHECK_TYPES;
  double norm = 1.0 / (xmax - xmin);
  FILL_CALL_FIXED(float32, float32, float, float, include_flow);
  FILL_CALL_FIXED(float64, float32, double, float, include_flow);
  FILL_CALL_FIXED(float32, float64, float, double, include_flow);
  FILL_CALL_FIXED(float64, float64, double, double, include_flow);
  FILL_CALL_FIXED(uint32, float32, unsigned int, float, include_flow);
  FILL_CALL_FIXED(int32, float32, int, float, include_flow);
  FILL_CALL_FIXED(uint32, float64, unsigned int, double, include_flow);
  FILL_CALL_FIXED(int32, float64, int, double, include_flow);
  FILL_CALL_FIXED(uint64, float32, unsigned long, float, include_flow);
  FILL_CALL_FIXED(int64, float32, long, float, include_flow);
  FILL_CALL_FIXED(uint64, float64, unsigned long, double, include_flow);
  FILL_CALL_FIXED(int64, float64, long, double, include_flow);
  return Status::ERROR;
}

static Status fill_f1dw_exclude_flow(PyArrayObject* x, PyArrayObject* w,
                                     PyArrayObject* c, PyArrayObject* v, long nx,
                                     int nbins, double xmin, double xmax) {
  CHECK_TYPES;
  double norm = 1.0 / (xmax - xmin);
  FILL_CALL_FIXED(float32, float32, float, float, exclude_flow);
  FILL_CALL_FIXED(float64, float32, double, float, exclude_flow);
  FILL_CALL_FIXED(float32, float64, float, double, exclude_flow);
  FILL_CALL_FIXED(float64, float64, double, double, exclude_flow);
  FILL_CALL_FIXED(uint32, float32, unsigned int, float, exclude_flow);
  FILL_CALL_FIXED(int32, float32, int, float, exclude_flow);
  FILL_CALL_FIXED(uint32, float64, unsigned int, double, exclude_flow);
  FILL_CALL_FIXED(int32, float64, int, double, exclude_flow);
  FILL_CALL_FIXED(uint64, float32, unsigned long, float, exclude_flow);
  FILL_CALL_FIXED(int64, float32, long, float, exclude_flow);
  FILL_CALL_FIXED(uint64, float64, unsigned long, double, exclude_flow);
  FILL_CALL_FIXED(int64, float64, long, double, exclude_flow);
  return Status::ERROR;
}

static Status fill_v1dw_include_flow(PyArrayObject* x, PyArrayObject* w,
                                     PyArrayObject* c, PyArrayObject* v, long nx,
                                     PyArrayObject* ed, int nedges) {
  const double* edges_arr = (const double*)PyArray_DATA(ed);
  std::vector<double> edges(edges_arr, edges_arr + nedges);
  CHECK_TYPES;
  FILL_CALL_VAR(float32, float32, float, float, include_flow);
  FILL_CALL_VAR(float64, float32, double, float, include_flow);
  FILL_CALL_VAR(float32, float64, float, double, include_flow);
  FILL_CALL_VAR(float64, float64, double, double, include_flow);
  FILL_CALL_VAR(uint32, float32, unsigned int, float, include_flow);
  FILL_CALL_VAR(int32, float32, int, float, include_flow);
  FILL_CALL_VAR(uint32, float64, unsigned int, double, include_flow);
  FILL_CALL_VAR(int32, float64, int, double, include_flow);
  FILL_CALL_VAR(uint64, float32, unsigned long, float, include_flow);
  FILL_CALL_VAR(int64, float32, long, float, include_flow);
  FILL_CALL_VAR(uint64, float64, unsigned long, double, include_flow);
  FILL_CALL_VAR(int64, float64, long, double, include_flow);
  return Status::ERROR;
}

static Status fill_v1dw_exclude_flow(PyArrayObject* x, PyArrayObject* w,
                                     PyArrayObject* c, PyArrayObject* v, long nx,
                                     PyArrayObject* ed, int nedges) {
  const double* edges_arr = (const double*)PyArray_DATA(ed);
  std::vector<double> edges(edges_arr, edges_arr + nedges);
  CHECK_TYPES;
  FILL_CALL_VAR(float32, float32, float, float, exclude_flow);
  FILL_CALL_VAR(float64, float32, double, float, exclude_flow);
  FILL_CALL_VAR(float32, float64, float, double, exclude_flow);
  FILL_CALL_VAR(float64, float64, double, double, exclude_flow);
  FILL_CALL_VAR(uint32, float32, unsigned int, float, exclude_flow);
  FILL_CALL_VAR(int32, float32, int, float, exclude_flow);
  FILL_CALL_VAR(uint32, float64, unsigned int, double, exclude_flow);
  FILL_CALL_VAR(int32, float64, int, double, exclude_flow);
  FILL_CALL_VAR(uint64, float32, unsigned long, float, exclude_flow);
  FILL_CALL_VAR(int64, float32, long, float, exclude_flow);
  FILL_CALL_VAR(uint64, float64, unsigned long, double, exclude_flow);
  FILL_CALL_VAR(int64, float64, long, double, exclude_flow);
  return Status::ERROR;
}

static PyObject* f1dw(PyObject* Py_UNUSED(self), PyObject* args) {
  long nx, nw;
  int nbins;
  int flow, as_err;
  double xmin, xmax;
  PyObject *x_obj, *w_obj, *counts_obj, *vars_obj;
  PyArrayObject *x_array, *w_array, *counts_array, *vars_array;
  npy_intp dims[1];

  if (!PyArg_ParseTuple(args, "OOiddpp", &x_obj, &w_obj, &nbins, &xmin, &xmax, &flow,
                        &as_err)) {
    PyErr_SetString(PyExc_TypeError, "Error parsing function input");
    return NULL;
  }

  x_array = (PyArrayObject*)PyArray_FROM_OF(x_obj, NPY_ARRAY_IN_ARRAY);
  w_array = (PyArrayObject*)PyArray_FROM_OF(w_obj, NPY_ARRAY_IN_ARRAY);

  if (x_array == NULL || w_array == NULL) {
    PyErr_SetString(PyExc_TypeError, "Could not read input data or weights as array");
    Py_XDECREF(x_array);
    Py_XDECREF(w_array);
    return NULL;
  }

  nx = (long)PyArray_DIM(x_array, 0);
  nw = (long)PyArray_DIM(w_array, 0);
  if (nx != nw) {
    PyErr_SetString(PyExc_ValueError, "data and weights must have equal length");
    Py_DECREF(x_array);
    Py_DECREF(w_array);
    return NULL;
  }

  dims[0] = nbins;
  counts_obj = PyArray_ZEROS(1, dims, PyArray_TYPE(w_array), 0);
  vars_obj = PyArray_ZEROS(1, dims, PyArray_TYPE(w_array), 0);

  if (counts_obj == NULL || vars_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Could not build output");
    Py_DECREF(x_array);
    Py_DECREF(w_array);
    Py_XDECREF(counts_obj);
    Py_XDECREF(vars_obj);
    return NULL;
  }

  counts_array = (PyArrayObject*)counts_obj;
  vars_array = (PyArrayObject*)vars_obj;

  Status fill_result = Status::ERROR;
  if (flow) {
    fill_result = fill_f1dw_include_flow(x_array, w_array, counts_array, vars_array, nx,
                                         nbins, xmin, xmax);
  }
  else {
    fill_result = fill_f1dw_exclude_flow(x_array, w_array, counts_array, vars_array, nx,
                                         nbins, xmin, xmax);
  }
  if (fill_result != Status::SUCCESS) {
    PyErr_SetString(PyExc_TypeError, "dtype of input arrays unsupported");
    Py_DECREF(x_array);
    Py_DECREF(w_array);
    Py_DECREF(counts_obj);
    Py_DECREF(vars_obj);
    return NULL;
  }

  if (as_err) {
    if (calc_err(vars_array, nbins) != Status::SUCCESS) {
      PyErr_SetString(PyExc_TypeError, "dtype of input arrays unsupported");
      Py_DECREF(x_array);
      Py_DECREF(w_array);
      Py_DECREF(counts_obj);
      Py_DECREF(vars_obj);
      return NULL;
    }
  }

  Py_DECREF(x_array);
  Py_DECREF(w_array);

  return Py_BuildValue("OO", counts_obj, vars_obj);
}

static PyObject* v1dw(PyObject* Py_UNUSED(self), PyObject* args) {
  long nx, nw;
  int ne;
  int flow, as_err;
  PyObject *x_obj, *w_obj, *e_obj, *counts_obj, *vars_obj;
  PyArrayObject *x_array, *w_array, *e_array, *counts_array, *vars_array;
  npy_intp dims[1];

  if (!PyArg_ParseTuple(args, "OOOpp", &x_obj, &w_obj, &e_obj, &flow, &as_err)) {
    PyErr_SetString(PyExc_TypeError, "Error parsing function input");
    return NULL;
  }

  x_array = (PyArrayObject*)PyArray_FROM_OF(x_obj, NPY_ARRAY_IN_ARRAY);
  w_array = (PyArrayObject*)PyArray_FROM_OF(w_obj, NPY_ARRAY_IN_ARRAY);
  e_array = (PyArrayObject*)PyArray_FROM_OTF(e_obj, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);

  if (x_array == NULL || w_array == NULL || e_array == NULL) {
    PyErr_SetString(PyExc_TypeError, "Could not read input data or weights as array");
    Py_XDECREF(x_array);
    Py_XDECREF(w_array);
    Py_XDECREF(e_array);
    return NULL;
  }

  nx = (long)PyArray_DIM(x_array, 0);
  nw = (long)PyArray_DIM(w_array, 0);
  ne = (int)PyArray_DIM(e_array, 0);
  if (nx != nw) {
    PyErr_SetString(PyExc_ValueError, "data and weights must have equal length");
    Py_DECREF(x_array);
    Py_DECREF(w_array);
    return NULL;
  }

  dims[0] = ne - 1;
  counts_obj = PyArray_ZEROS(1, dims, PyArray_TYPE(w_array), 0);
  vars_obj = PyArray_ZEROS(1, dims, PyArray_TYPE(w_array), 0);

  if (counts_obj == NULL || vars_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Could not build output");
    Py_DECREF(x_array);
    Py_DECREF(w_array);
    Py_DECREF(e_array);
    Py_XDECREF(counts_obj);
    Py_XDECREF(vars_obj);
    return NULL;
  }

  counts_array = (PyArrayObject*)counts_obj;
  vars_array = (PyArrayObject*)vars_obj;

  Status fill_result = Status::ERROR;
  if (flow) {
    fill_result = fill_v1dw_include_flow(x_array, w_array, counts_array, vars_array, nx,
                                         e_array, ne);
  }
  else {
    fill_result = fill_v1dw_exclude_flow(x_array, w_array, counts_array, vars_array, nx,
                                         e_array, ne);
  }
  if (fill_result != Status::SUCCESS) {
    PyErr_SetString(PyExc_TypeError, "dtype of input arrays unsupported");
    Py_DECREF(x_array);
    Py_DECREF(w_array);
    Py_DECREF(e_array);
    Py_DECREF(counts_obj);
    Py_DECREF(vars_obj);
    return NULL;
  }

  if (as_err) {
    if (calc_err(vars_array, ne - 1) != Status::SUCCESS) {
      PyErr_SetString(PyExc_TypeError, "dtype of input arrays unsupported");
      Py_DECREF(x_array);
      Py_DECREF(w_array);
      Py_DECREF(e_array);
      Py_DECREF(counts_obj);
      Py_DECREF(vars_obj);
      return NULL;
    }
  }

  Py_DECREF(x_array);
  Py_DECREF(w_array);
  Py_DECREF(e_array);

  return Py_BuildValue("OO", counts_obj, vars_obj);
}

static PyObject* omp_gmt(PyObject* Py_UNUSED(self), PyObject* Py_UNUSED(args)) {
  long nthreads = omp_get_max_threads();
  return PyLong_FromLong(nthreads);
}
