"""
    biclustlib: A Python library of biclustering algorithms and evaluation measures.
    Copyright (C) 2017  Victor Alexandre Padilha

    This file is part of biclustlib.

    biclustlib is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    biclustlib is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from ._base import BaseExecutableWrapper
from ...models import Bicluster, Biclustering
from os.path import dirname, join

import numpy as np
import re
import os

class QualitativeBiclustering(ExecutableWrapper):
    """QUalitative BIClustering (QUBIC)

    This class is a simple wrapper for the executable obtained after compiling the C code
    provided by the original authors of this algorithm (available in http://csbl.bmb.uga.edu/~maqin/bicluster/).
    The binaries contained in this package were compiled for the x86_64 architecture.

    Reference
    ---------
    Li, G., Ma, Q., Tang, H., Paterson, A. H., and Xu, Y. (2009). QUBIC: a qualitative biclustering algorithm
    for analyses of gene expression data. Nucleic acids research, 37(15), e101-e101.

    Parameters
    ----------
    num_biclusters : int, default: 10
        Number of biclusters to be found.

    ranks : int, default: 1
        ...

    quant : float, default: 0.06
        ...

    consistency : float, default: 0.95
        ...

    max_overlap_level : float, default: 1.0
        ...

    tmp_dir : str, default: '.bbc_tmp'
        Temporary directory to save the outputs generated by BBC's executable.
    """

    def __init__(self, num_biclusters=10, ranks=1, quant=0.06, consistency=0.95, max_overlap_level=1.0, tmp_dir='.qubic_tmp'):
        module_dir = dirname(__file__)

        exec_comm = join(module_dir, 'bin', 'qubic') + \
                    ' -i {_data_filename}' + \
                    ' -q {quant}' + \
                    ' -r {ranks}' + \
                    ' -f {max_overlap_level}' + \
                    ' -c {consistency}' + \
                    ' -o {num_biclusters}'

        super().__init__(exec_comm, tmp_dir=tmp_dir)

        self.num_biclusters = num_biclusters
        self.ranks = ranks
        self.quant = quant
        self.consistency = consistency
        self.max_overlap_level = max_overlap_level

        self._output_filename = 'data.txt.blocks'

    def _parse_output(self):
        biclusters = []

        if os.path.exists(self._output_filename):
            with open(self._output_filename, 'r') as f:
                content = f.read()
                bc_strings = re.split('BC[0-9]+', content)[1:]
                biclusters.extend(self._parse_bicluster(b) for b in bc_strings)

        return Biclustering(biclusters)

    def _parse_bicluster(self, string):
        after_genes = re.split('Genes \[[0-9]+\]:', string).pop()
        genes, after_conds = re.split('Conds \[[0-9]+\]:', after_genes)
        genes = genes.split()
        conds = after_conds.split('\n')[0].split()
        return Bicluster(self._convert(genes), self._convert(conds))

    def _convert(self, str_array):
        return np.array([int(a.split('_').pop()) for a in str_array])

    def _validate_parameters(self):
        if self.num_biclusters <= 0:
            raise ValueError("num_biclusters must be > 0, got {}".format(self.num_biclusters))

        if self.ranks <= 0:
            raise ValueError("ranks must be > 0, got {}".format(self.ranks))

        if self.quant <= 0.0 or self.quant >= 1.0:
            raise ValueError("quant must be > 0.0 and < 1.0, got {}".format(self.quant))

        if self.consistency <= 0.0 or self.consistency > 1.0:
            raise ValueError("consistency must be > 0.0 and <= 1.0, got {}".format(self.consistency))

        if self.max_overlap_level <= 0.0 or self.max_overlap_level > 1.0:
            raise ValueError("max_overlap_level must be > 0.0 and <= 1.0, got {}".format(self.max_overlap_level))