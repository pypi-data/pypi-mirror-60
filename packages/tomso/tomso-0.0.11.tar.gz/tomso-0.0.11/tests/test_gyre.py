from tomso import gyre
import numpy as np
import unittest

tmpfile = 'data/tmpfile'


class TestGYREFunctions(unittest.TestCase):

    def test_load_summary(self):
        header, data = gyre.load_summary('data/gyre.summ')
        self.assertAlmostEqual(header['M_star'], 1.989e33)
        self.assertAlmostEqual(header['R_star'], 6.959906258e10)
        for i, row in enumerate(data):
            self.assertEqual(row['l'], 1)
            self.assertEqual(row['n_pg'], i+19)

        header, data = gyre.load_summary('data/gyre_noheader.summ')
        for i, row in enumerate(data):
            self.assertEqual(row['l'], 0)
            self.assertEqual(row['n_pg'], i+8)

    def test_load_mode(self):
        for i in range(3):
            header, data = gyre.load_mode('data/gyre.mode_%i' % (i+1))
            self.assertEqual(header['n_pg'], i+19)
            self.assertEqual(header['l'], 1)
            self.assertEqual(header['Imomega'], 0.0)
            self.assertEqual(header['Imfreq'], 0.0)
            for row in data:
                self.assertEqual(row['Imxi_r'], 0.0)
                self.assertEqual(row['Imxi_h'], 0.0)

    def test_load_gyre(self):
        header, data = gyre.load_gyre('data/mesa.gyre')
        self.assertEqual(header['n'], 601)
        self.assertAlmostEqual(header['M'], 1.9882053999999999E+33)
        self.assertAlmostEqual(header['R'], 6.2045507132959908E+10)
        self.assertAlmostEqual(header['L'], 3.3408563666602257E+33)
        self.assertEqual(header['version'], 101)

        m = gyre.load_gyre('data/mesa.gyre', return_object=True)
        self.assertEqual(len(m.data), 601)
        self.assertAlmostEqual(m.M, 1.9882053999999999E+33)
        self.assertAlmostEqual(m.R, 6.2045507132959908E+10)
        self.assertAlmostEqual(m.L, 3.3408563666602257E+33)
        self.assertEqual(m.version, 101)

    def test_load_spb_mesa_versions(self):
        filenames = ['data/spb.mesa.78677cc', 'data/spb.mesa.813eed2',
                     'data/spb.mesa.adc6989']
        for filename in filenames:
            header1, data1 = gyre.load_gyre(filename)
            gyre.save_gyre(tmpfile, header1, data1)
            header2, data2 = gyre.load_gyre(tmpfile)
            self.assertEqual(header1, header2)
            for row1, row2 in zip(data1, data2):
                self.assertEqual(row1, row2)

            m1 = gyre.load_gyre('data/mesa.gyre', return_object=True)
            m1.to_file(tmpfile)
            m2 = gyre.load_gyre(tmpfile, return_object=True)
            self.assertEqual(m1.header, m2.header)
            for row1, row2 in zip(m1.data, m2.data):
                self.assertEqual(row1, row2)

            self.assertTrue(np.allclose(m1.r, m2.x*m2.R))
            self.assertTrue(np.allclose(m1.cs2, m2.Gamma_1*m2.P/m2.rho))
            self.assertTrue(np.allclose(m1.AA[1:], m2.N2[1:]*m2.r[1:]/m2.g[1:]))

    def test_save_gyre(self):
        header1, data1 = gyre.load_gyre('data/mesa.gyre')
        gyre.save_gyre(tmpfile, header1, data1)
        header2, data2 = gyre.load_gyre(tmpfile)
        self.assertEqual(header1, header2)
        for row1, row2 in zip(data1, data2):
            self.assertEqual(row1, row2)

        m1 = gyre.load_gyre('data/mesa.gyre', return_object=True)
        m1.to_file(tmpfile)
        m2 = gyre.load_gyre(tmpfile, return_object=True)
        self.assertEqual(m1.header, m2.header)
        for row1, row2 in zip(m1.data, m2.data):
            self.assertEqual(row1, row2)

        self.assertTrue(np.allclose(m1.r, m2.x*m2.R))
        self.assertTrue(np.allclose(m1.cs2, m2.Gamma_1*m2.P/m2.rho))
        self.assertTrue(np.allclose(m1.AA[1:], m2.N2[1:]*m2.r[1:]/m2.g[1:]))


if __name__ == '__main__':
    unittest.main()
