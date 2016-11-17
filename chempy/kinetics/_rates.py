# -*- coding: utf-8 -*-
"""
Non-public API (classes in this module may change without notice).

The purpose here is to define conventions, e.g. lower-case string
 'temperature' is used, opposed to e.g. 'T', 'Temperature', etc.
"""
from __future__ import (absolute_import, division, print_function)

import math

from ..util._expr import mk_Poly, mk_PiecewisePoly
from .rates import RateExpr, MassAction, Radiolytic


TPoly = mk_Poly('temperature')
RTPoly = mk_Poly('temperature', reciprocal=True)
ShiftedTPoly = create_Poly('T', shift='Tref')
ShiftedRTPoly = create_Poly('T', shift='Tref', reciprocal=True)


class TPoly(TPoly):
    argument_names = ('temperature_offset', Ellipsis)
    parameter_keys = TPoly.parameter_keys

    def __call__(self, variables, backend=math):
        return self.eval_poly(variables, backend)


TPiecewisePoly = mk_PiecewisePoly('temperature')
RTPiecewisePoly = mk_PiecewisePoly('temperature', reciprocal=True)



class _Log10XPolyMassAction(MassAction):
    skip_poly = 1  # kunit

    def rate_coeff(self, variables, backend=math):
        k_unit = self.arg(variables, 0)
        return 10**self.eval_poly(variables, backend)*k_unit


class Log10TPolyMassAction(TPoly, _Log10XPolyMassAction):
    argument_names = ('k_unit', 'temperature_offset', Ellipsis)
    parameter_keys = TPoly.parameter_keys
    skip_poly = 1  # kunit


class Log10RTPolyMassAction(RTPoly, _Log10XPolyMassAction):
    argument_names = ('k_unit', 'temperature_offset', Ellipsis)
    parameter_keys = RTPoly.parameter_keys
    skip_poly = 1  # kunit


class Log10PiecewiseRTPolyMassAction(RTPiecewisePoly, _Log10XPolyMassAction):
    argument_names = ('k_unit', Ellipsis)
    parameter_keys = RTPiecewisePoly.parameter_keys
    skip_poly = 1  # kunit


class TPolyInLog10MassAction(TPoly, MassAction):
    argument_names = ('T_unit', 'temperature_offset', Ellipsis)
    parameter_keys = TPoly.parameter_keys
    skip_poly = 1  # T_unit

    def rate_coeff(self, variables, backend=math):
        T_u = self.arg(variables, 0)  # T_unit
        new_vars = variables.copy()
        new_vars['temperature'] = backend.log10(variables['temperature'] / T_u)
        return self.eval_poly(new_vars, backend=backend)


class TPiecewise(RateExpr):
    parameter_keys = ('temperature',)

    def __call__(self, variables, backend=math):
        temperature, = self.all_params(variables, backend=backend)
        for lower, upper, expr in [self.args[i*3:i*3+3] for i in range(len(self.args)//3)]:
            if lower <= temperature <= upper:
                return expr(variables, backend=backend)
        else:
            raise ValueError("Outside all bounds: %s" % str(temperature))
