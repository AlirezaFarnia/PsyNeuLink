#!/usr/bin/python3

import ctypes
import PsyNeuLink.llvm as pnlvm
import numpy as np
import copy

ITERATIONS=100
DIM_X=1000
DIM_Y=2000

matrix = np.random.rand(DIM_X, DIM_Y)
vector = np.random.rand(DIM_X)
llvm_res = np.random.rand(DIM_Y)

ct_vec = vector.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
ct_mat = matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
x, y = matrix.shape

# The original builtin mxv function
binf = pnlvm.LLVMBinaryFunction.get('__pnl_builtin_vxm')
orig_res = copy.deepcopy(llvm_res)
ct_res = orig_res.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

cfunc_type = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double))

binf.c_func(ct_vec, ct_mat, x, y, ct_res)

# Rebuild and try again
pnlvm.llvm_build()

rebuild_res = copy.deepcopy(llvm_res)
ct_res = rebuild_res.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


binf.c_func(ct_vec, ct_mat, x, y, ct_res)

# Get a new pointer
binf2 = pnlvm.LLVMBinaryFunction.get('__pnl_builtin_vxm')
new_res = copy.deepcopy(llvm_res)
ct_res = new_res.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

binf.c_func(ct_vec, ct_mat, x, y, ct_res)

callable_res = copy.deepcopy(llvm_res)
ct_res = callable_res.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

binf(ct_vec, ct_mat, x, y, ct_res)

if np.array_equal(orig_res, rebuild_res) and np.array_equal(rebuild_res, new_res) and np.array_equal(new_res, callable_res):
    print("TEST PASSED")
else:
    print("TEST FAILED")
