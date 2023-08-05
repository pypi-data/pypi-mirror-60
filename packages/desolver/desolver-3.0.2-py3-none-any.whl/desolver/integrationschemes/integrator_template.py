"""
The MIT License (MIT)

Copyright (c) 2019 Microno95, Ekin Ozturk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from .. import backend as D

def named_integrator(name, alt_names=tuple(), order=1.0):
    def wrap(f):
        f.__name__ = str(name)
        f.__alt_names__ = alt_names
        f.__order__ = order
        if hasattr(f, "final_state"):
            f.__adaptive__ = D.shape(f.final_state)[0] == 2
        else:
            f.__adaptive__ = False
        return f
    return wrap

class IntegratorTemplate:
    def __init__(self):
        raise NotImplementedError("Do not initialise this class directly!")

    def forward(self):
        raise NotImplementedError("Do not use this class directly! How did you initialise it??")

    __call__ = forward

    def update_timestep(self, diff, initial_time, timestep, tol=0.9):
        err_estimate = D.max(D.abs(diff))
        relerr = self.atol + self.rtol * err_estimate
        if err_estimate != 0:
            corr = timestep * tol * (relerr / err_estimate) ** (1.0 / self.num_stages)
            if corr != 0:
                timestep = corr
        if err_estimate > relerr:
            return timestep, True
        else:
            return timestep, False
    
    @classmethod
    def __str__(cls):
        return cls.__name__
    
    def __repr__(self):
        if D.backend() == 'torch':
            return "<{}({},{},{},{})>".format(self.__class__.__name__, self.dim, self.dtype, self.rtol, self.atol)
        else:
            return "<{}({},{},{},{},{})>".format(self.__class__.__name__, self.dim, self.dtype, self.rtol, self.atol, self.device)

class ExplicitIntegrator(IntegratorTemplate):
    tableau = None
    final_state = None
    __symplectic__ = False

    def __init__(self, sys_dim, dtype=None, rtol=None, atol=None, device=None):
        if dtype is None:
            self.tableau     = D.array(self.tableau)
            self.final_state = D.array(self.final_state)
        else:
            self.tableau     = D.to_type(self.tableau, dtype)
            self.final_state = D.to_type(self.final_state, dtype)
            
        self.dim        = sys_dim
        self.rtol       = rtol
        self.atol       = atol
        self.adaptive   = D.shape(self.final_state)[0] == 2
        self.num_stages = D.shape(self.tableau)[0]
        self.aux        = D.zeros((self.num_stages, *self.dim))
        if D.backend() == 'torch':
            self.aux         = self.aux.to(device)
            self.tableau     = self.tableau.to(device)
            self.final_state = self.final_state.to(device)
            
    def forward(self, rhs, initial_time, initial_state, constants, timestep):
        if self.tableau is None:
            raise NotImplementedError("In order to use the fixed step integrator, subclass this class and populate the butcher tableau")
        else:
            aux = self.aux

            for stage in range(self.num_stages):
                current_state = initial_state    + D.einsum("n,n...->...", self.tableau[stage, 1:], aux)
                aux[stage]    = rhs(initial_time + self.tableau[stage, 0]*timestep, current_state, **constants) * timestep
                
            dState = D.einsum("n,n...->...", self.final_state[0, 1:], aux)
            dTime  = timestep
            
            if self.adaptive:
                diff = dState - D.einsum("n,n...->...", self.final_state[1, 1:], aux)
                timestep, redo_step = self.update_timestep(diff, initial_time, timestep)
                if redo_step:
                    timestep, (dTime, dState) = self(rhs, initial_time, initial_state, constants, timestep)
            
            return timestep, (dTime, dState)

    __call__ = forward

class SymplecticIntegrator(IntegratorTemplate):
    tableau = None
    __symplectic__ = True

    def __init__(self, sys_dim, dtype=None, staggered_mask=None, rtol=None, atol=None, device=None):
        if staggered_mask is None:
            staggered_mask      = D.arange(sys_dim[0]//2, sys_dim[0], dtype=D.int64)
            self.staggered_mask = D.zeros(sys_dim, dtype=D.bool)
            self.staggered_mask[staggered_mask] = 1
        else:
            self.staggered_mask = D.to_type(staggered_mask, D.bool)
            
        if dtype is None:
            self.tableau     = D.array(self.tableau)
        else:
            self.tableau     = D.to_type(self.tableau, dtype)

        self.dim        = sys_dim
        self.rtol       = rtol
        self.atol       = atol
        self.adaptive   = False
        self.num_stages = D.shape(self.tableau)[0]
        self.msk  = self.staggered_mask
        self.nmsk = D.logical_not(self.staggered_mask)
        if D.backend() == 'torch':
            self.tableau     = self.tableau.to(device)
            self.msk  = self.msk.to(self.tableau)
            self.nmsk = self.nmsk.to(self.tableau)

    def forward(self, rhs, initial_time, initial_state, constants, timestep):
        if self.tableau is None:
            raise NotImplementedError("In order to use the fixed step integrator, subclass this class and populate the butcher tableau")
        else:
            msk  = self.msk
            nmsk = self.nmsk

            current_time  = D.copy(initial_time)
            current_state = D.copy(initial_state)
            dState        = D.zeros_like(current_state)

            for stage in range(self.num_stages):
                aux          = rhs(current_time, initial_state + dState, **constants) * timestep
                current_time = current_time + timestep * self.tableau[stage, 0]
                dState      += aux * self.tableau[stage, 1] * msk + aux * self.tableau[stage, 2] * nmsk
                
            dTime = timestep
            
            return timestep, (dTime, dState)

    __call__ = forward
