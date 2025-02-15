from cython.cimports.python cimport PyNumber_Check, PyTuple_Check

ctypedef double Coordinate  # Define the alias
ctypedef double Parameter  # Define the alias
ctypedef unsigned uint1 
ctypedef unsigned uint4 

cdef class Polynomial:

    cdef tuple _internal;

    def __cinit__(self, coefs = 0):
        """Flexible initialization with variable arguments"""
        if PyTuple_Check(coefs):
            self.__internal = coefs
        else:
            self._internal = (coefs,)  # Single element

    # cdef uint1 degree():
    #     uint1 deg = len(self._internal) - 1
    #     while (deg and _internal[degree]):
    #         deg -= 1
    #     return deg

    # cdef Coordinate eval(self, Parameter node) except *:
    #     Coordinate result = 0
    #     for i in range(self.degree()):
    #         result = result * node + _internal[i]
    #     return result

        