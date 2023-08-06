#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:46:22 2020

@author: henrik
"""
import os
from tempfile import NamedTemporaryFile
from subprocess import call
from img2org.conversion import read_output_gnuplot

from abc import ABC, abstractmethod

class Solver(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
    
    def to_file(self, fname):
        with open(fname, 'w') as fout:
            fout.write(self.__str__())
            
class rk5(Solver):
    def __init__(self, tspan, maxstep=1, error=1e-3, printflag=1, n_print=100):
        self.tspan = tspan
        self.maxstep = maxstep
        self.error = error
        self.printflag = printflag
        self.n_print = n_print
        
    def __str__(self):
        s = f'RK5Adaptive\n'
        s += f'{self.tspan[0]} {self.tspan[1]}\n'
        s += f'{self.printflag} {self.n_print}\n'
        s += f'{self.maxstep} {self.error}'
        return s

class Model():
    def __init__(self, name, description=''):
        self.name = name
        self.description = description
        
        self.species = {}
        self.reactions = {}
        self.topologies = []
        self.neighbourhoods = []
        
    def add_species(self, spec):
        if isinstance(spec, str):
            spec = Species(spec)
        
        spec.index = self.n_variables
        self.species[spec.name] = spec

    def add_reaction(self, reaction):
        self.reactions[reaction.name] = reaction

    def add_topology(self, topology):
        self.topologies.append(topology)

    def add_neighbourhood(self, neighbourhood):
        self.neighbourhoods.append(neighbourhood)
        
    def clear_neighbourhood(self):
        self.neighbourhoods = []

    def clear_reactions(self):
        self.reactions = {}

    def clear_species(self):
        self.species = {}

    def clear_topologies(self):
        self.topologies = []
        
    def clear(self):
        self.species = {}
        self.reactions = {}
        self.topologies = []
        self.neighbourhoods = []
        
    @property
    def n_topologies(self):
        return len(self.topologies)

    @property
    def n_species(self):
        return len(self.species)

    @property
    def n_reactions(self):
        return len(self.reactions)

    @property
    def n_neighbourhoods(self):
        return len(self.neighbourhoods)
    
    @property
    def n_variables(self):
        return self.n_species + self.n_reactions + self.n_neighbourhoods + sum([t.n for t in self.topologies])
    
    def __str__(self):
        s = f'{self.description}\n'
        s += f'{self.name} {self.n_topologies} {self.n_species} {self.n_reactions} '
        s += f'{self.n_neighbourhoods}\n\n'
        s += '\n'.join([str(topo) for topo in self.topologies])
        s += '\n\n'
        s += '\n'.join([str(spec) for spec in self.species.values()])
        s += '\n\n'
        s += '\n'.join([str(reac) for reac in self.reactions.values()])
        s += '\n'.join([str(neigh) for neigh in self.neighbourhoods])
        return s

    def to_file(self, fname):
        with open(fname, 'w') as fout:
            fout.writelines(str(self))

class Topology():
    def __init__(self, name, n, active_geometry=False, active_topology=False):
        self.name = name
        self.n = n
        self.active_geometry = active_geometry
        self.active_topology = active_topology
    
    def __str__(self):
        s = f'{self.name} {self.n} {int(self.active_geometry)} {int(self.active_topology)}'
        return s

class Neighbourhood(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

class neighbourhood_from_file(Neighbourhood):
    def __init__(self, path):
        self.path = path
    
    def __str__(self):
        s = f'neighborhoodFromFileInitial 1 1\n'
        s += f'{self.path}'
        return s

class Species():
    def __init__(self, name):
        self.name = name
        self.index = None
        self.reactions = []
    
    def add_reaction(self, reaction):
        self.reactions.append(reaction)

    @property
    def n_reactions(self):
        return len(self.reactions)
    
    def __str__(self):
        s = f'{self.name} {self.index} {self.n_reactions}\n'
        s += '\n'.join([str(reaction) for reaction in self.reactions])
#        if self.n_reactions > 0:
        s += '\n'
        return s
    
class Reaction(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def __str__():
        pass
    
class creation_zero(Reaction):
    def __init__(self, rate):
        self.rate = rate
        
    def __str__(self):
        s = f'creationZero 1 0\n{self.rate}'
        return s
    
class degradation_one(Reaction):
    def __init__(self, rate):
        self.rate = rate
        
    def __str__(self):
        s = 'degradationOne 1 0\n{rate}'
        return s
    
class cell_cell_auxin_transport(Reaction):
    def __init__(self, rates, indices):
        assert(len(rates) == 4)
        assert(len(indices) == 3)
        self.rates = rates
        self.indices = indices
    
    def __str__(self):
        s =  f'cellCellAuxinTransport 4 2 1 2\n'
        s += f'{self.rates[0]}\n'
        s += f'{self.rates[1]}\n'
        s += f'{self.rates[2]}\n'
        s += f'{self.rates[3]}\n'

        s += f'{self.indices[0]}\n'
        s += f'{self.indices[1]}\n'
        s += f'{self.indices[2]}'
        
        return s

def run_organism(simulator, model, init, solver, output, final_path, current_time=0, current_print=0, verbose=False):
    with NamedTemporaryFile('w') as tmp_model, NamedTemporaryFile('w') as tmp_solver, NamedTemporaryFile('w') as FOUT, open(os.devnull, 'w') as FNULL:
        # Make new model file
        if not isinstance(model, str):
            tmp_model.write(str(model))
            tmp_model.flush()
            model_path = tmp_model.name
        else:
            model_path = model
            
        if not isinstance(solver, str):
            tmp_solver.write(str(solver))
            tmp_solver.flush()
            solver_path = tmp_solver.name
        else:
            solver_path = solver
    
        # Run Organism
        call([simulator,
              model_path,
              init,
              solver_path, 
              '-init_output', final_path,
              '-verbose', str(int(verbose))],
            stdout=FOUT, stderr=FNULL)
    
        # Append data
        data = read_output_gnuplot(FOUT.name)
        data[0] += current_print
        data[1] += current_time
        data.to_csv(output, mode='a', header=False, sep=' ', index=False)
    
def run_organism_convergence(simulator, model, init_path, solver, output, error=1e-5, end_time=None, verbose=False):
    if os.path.exists(output):
        open(output, 'w').close()
    
    tspan = solver.tspan
    n_print = solver.n_print
    current_time = 0
    current_print = 0
        
    fname = init_path
    final_path = os.path.splitext(output)[0] + '-end_state.init' #init_path[:-5] + '-end_state.init'
    while True and current_time < end_time:
        run_organism(simulator=simulator,
            model=model,
            init=fname,
            solver=solver,
            output=output,
            final_path=final_path,
            current_time=current_time,
            current_print=current_print)
        current_time += tspan[1] - tspan[0]
        current_print += n_print
    
        data = read_output_gnuplot(output)
    
        penultimate = data.loc[data[0] == data.max(0)[0] - n_print]
        ultimate = data.loc[data[0] == data.max(0)[0]]
    
        difference = abs(ultimate.loc[ultimate[11] == 1][9].mean() - penultimate.loc[penultimate[11] == 1][9].mean())
        fname = os.path.splitext(output)[0] + '-end_state.init'

        if verbose:
            print(current_time, difference)
        if difference < error:
            break
    