#   Copyright 2019 1QBit
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import unittest

from pyscf import gto

from openqemist.electronic_structure_solvers import FCISolver, CCSDSolver
from openqemist.problem_decomposition import DMETProblemDecomposition
from openqemist.problem_decomposition.electron_localization import iao_localization, meta_lowdin_localization

H10_RING = """
        H      0.970820393250   0.000000000000   0.000000000000
        H      0.785410196625   0.570633909777   0.000000000000
        H      0.300000000000   0.923305061153   0.000000000000
        H     -0.300000000000   0.923305061153   0.000000000000
        H     -0.785410196625   0.570633909777   0.000000000000
        H     -0.970820393250   0.000000000000   0.000000000000
        H     -0.785410196625  -0.570633909777   0.000000000000
        H     -0.300000000000  -0.923305061153   0.000000000000
        H      0.300000000000  -0.923305061153   0.000000000000
        H      0.785410196625  -0.570633909777   0.000000000000
        """

H4_RING = """
        H   0.7071067811865476   0.0                 0.0
        H   0.0                  0.7071067811865476  0.0
        H  -1.0071067811865476   0.0                 0.0
        H   0.0                 -1.0071067811865476  0.0
        """

class DMETProblemDecompositionTest(unittest.TestCase):

    def test_incorrect_number_atoms(self):
        """Tests if the program raises the error when the number of
        fragment sites is not equal to the number of atoms in the molecule."""
        mol = gto.Mole()
        mol.atom = H10_RING
        mol.basis = "3-21g"
        mol.charge = 0
        mol.spin = 0
        mol.build()

        solver = DMETProblemDecomposition()
        solver.electron_localization_method = meta_lowdin_localization
        solver.electronic_structure_solver = FCISolver()
        # The molecule has more atoms than this.
        self.assertRaises(RuntimeError, solver.simulate, mol, [1,1,1,1])

    def test_incorrect_number_solvers(self):
        """Tests if the program raises the error when the number of
        fragment sites is not equal to the number of solvers."""
        mol = gto.Mole()
        mol.atom = H10_RING
        mol.basis = "3-21g"
        mol.charge = 0
        mol.spin = 0
        mol.build()

        solver = DMETProblemDecomposition()
        self.assertRaises(RuntimeError, solver.simulate, mol, [2,3,2,3], fragment_solvers = [FCISolver()])

    def test_h10ring_ml_fci_no_mf(self):
        """ Tests the result from DMET against a value from a reference
        implementation with meta-lowdin localization and FCI solution to
        fragments."""
        mol = gto.Mole()
        mol.atom = H10_RING
        mol.basis = "3-21g"
        mol.charge = 0
        mol.spin = 0
        mol.build()

        solver = DMETProblemDecomposition()
        solver.electron_localization_method = meta_lowdin_localization
        solver.electronic_structure_solver = FCISolver()
        energy = solver.simulate(mol, [1,1,1,1,1,1,1,1,1,1])

        self.assertAlmostEqual(energy, -4.498973024, places=4)

    def test_h4ring_iao_ccsd_no_mf_321g(self):
        """ Tests the result from DMET against a value from a reference
        implementation with IAO localization, 3-21g basis, and CCSD solution to
        fragments."""
        mol = gto.Mole()
        mol.atom = H4_RING
        mol.basis = "3-21g"
        mol.charge = 0
        mol.spin = 0
        mol.build()

        solver = DMETProblemDecomposition()
        solver.electron_localization_method = iao_localization
        solver.electronic_structure_solver = CCSDSolver()
        energy = solver.simulate(mol, [2,2])

        self.assertAlmostEqual(energy, -2.0290205366, places=6)

    def test_h4ring_ml_ccsd_no_mf_minao(self):
        """ Tests the result from DMET against a value from a reference
        implementation with meta-lowdin localization and CCSD solution to
        fragments."""
        mol = gto.Mole()
        mol.atom = H4_RING
        mol.basis = "minao"
        mol.charge = 0
        mol.spin = 0
        mol.build()

        solver = DMETProblemDecomposition()
        solver.electron_localization_method = meta_lowdin_localization
        solver.electronic_structure_solver = CCSDSolver()
        energy = solver.simulate(mol, [1,1,1,1])

        self.assertAlmostEqual(energy, -1.9916120594, places=6)

    def test_h4ring_ml_fci_no_mf_minao(self):
        """ Tests the result from DMET against a value from a reference
        implementation with meta-lowdin localization and FCI solution to
        fragments."""
        mol = gto.Mole()
        mol.atom = H4_RING
        mol.basis = "minao"
        mol.charge = 0
        mol.spin = 0
        mol.build()

        solver = DMETProblemDecomposition()
        solver.electron_localization_method = meta_lowdin_localization
        solver.electronic_structure_solver = FCISolver()
        energy = solver.simulate(mol, [1,1,1,1])

        self.assertAlmostEqual(energy, -1.9916120594, places=4)


    def test_solver_mix(self):
        """Tests that solving with multiple solvers works.

        With this simple system, we can assume that both CCSD and FCI can reach
        chemical accuracy."""
        mol = gto.Mole()
        mol.atom = H4_RING
        mol.basis = "3-21g"
        mol.charge = 0
        mol.spin = 0
        mol.build()

        solver = DMETProblemDecomposition()
        solver.electron_localization_method = iao_localization
        fci = FCISolver()
        ccsd = CCSDSolver()
        energy = solver.simulate(mol, [1,1,1,1], fragment_solvers=[fci, fci, ccsd, ccsd])

        self.assertAlmostEqual(energy, -2.0284, places=4)

if __name__ == "__main__":
    unittest.main()
