# Any changes to the distributions library should be reinstalled with
#  pip install --upgrade .

# For running unit tests, use
# /usr/bin/python -m unittest test

import unittest

from pybility import Gaussian
from pybility import Binomial
from pybility import Poisson

class TestGaussianClass(unittest.TestCase):
    def setUp(self):
        self.gaussian = Gaussian(25, 2)
        self.gaussian.read_data_file('../data/data.txt')

    def test_initialization(self): 
        self.assertEqual(self.gaussian.mean, 25, 'incorrect mean')
        self.assertEqual(self.gaussian.stdev, 2, 'incorrect standard deviation')

    def test_readdata(self):
        self.assertEqual(self.gaussian.data,\
         [1, 3, 99, 100, 120, 32, 330, 23, 76, 44, 31], 'data not read in correctly')

    def test_meancalculation(self):
        self.assertEqual(self.gaussian.calculate_mean(),\
         sum(self.gaussian.data) / float(len(self.gaussian.data)), 'calculated mean not as expected')

    def test_stdevcalculation(self):
        self.assertEqual(round(self.gaussian.calculate_stdev(), 2), 92.87, 'sample standard deviation incorrect')
        self.assertEqual(round(self.gaussian.calculate_stdev(0), 2), 88.55, 'population standard deviation incorrect')

    def test_pdf(self):
        self.assertEqual(round(self.gaussian.pdf(25), 5), 0.19947,\
         'pdf function does not give expected result') 
        self.gaussian.calculate_mean()
        self.gaussian.calculate_stdev()
        self.assertEqual(round(self.gaussian.pdf(75), 5), 0.00429,\
        'pdf function after calculating mean and stdev does not give expected result')      

    def test_add(self):
        gaussian_one = Gaussian(25, 3)
        gaussian_two = Gaussian(30, 4)
        gaussian_sum = gaussian_one + gaussian_two
        
        self.assertEqual(gaussian_sum.mean, 55)
        self.assertEqual(gaussian_sum.stdev, 5)
    
    def test_mul(self):
        gaussian_one = Gaussian(25, 3)
        gaussian_two = Gaussian(30, 4)
        gaussian_prd = gaussian_one * gaussian_two

        self.assertEqual(gaussian_prd.mean, 750)
        self.assertEqual(round(gaussian_prd.stdev,2), 135.07)

class TestBinomialClass(unittest.TestCase):
    def setUp(self):
        self.binomial = Binomial(0.4, 20)
        self.binomial.read_data_file('../data/data_binomial.txt')

    def test_initialization(self):
        self.assertEqual(self.binomial.p, 0.4, 'p value incorrect')
        self.assertEqual(self.binomial.n, 20, 'n value incorrect')

    def test_readdata(self):
        self.assertEqual(self.binomial.data,\
         [0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0], 'data not read in correctly')
    
    def test_calculatemean(self):
        mean = self.binomial.calculate_mean()
        self.assertEqual(mean, 8)
    
    def test_calculatestdev(self):
        stdev = self.binomial.calculate_stdev()
        self.assertEqual(round(stdev,2), 2.19)
        
    def test_replace_stats_with_data(self):
        p, n = self.binomial.replace_stats_with_data()
        self.assertEqual(round(p,3), .615)
        self.assertEqual(n, 13)
        
    def test_pdf(self):
        self.assertEqual(round(self.binomial.pdf(5), 5), 0.07465)
        self.assertEqual(round(self.binomial.pdf(3), 5), 0.01235)
    
        self.binomial.replace_stats_with_data()
        self.assertEqual(round(self.binomial.pdf(5), 5), 0.05439)
        self.assertEqual(round(self.binomial.pdf(3), 5), 0.00472)

    def test_add(self):
        binomial_one = Binomial(.4, 20)
        binomial_two = Binomial(.4, 60)
        binomial_sum = binomial_one + binomial_two
        
        self.assertEqual(binomial_sum.p, .4)
        self.assertEqual(binomial_sum.n, 80)
    
class TestPoissonClass(unittest.TestCase):
    def setUp(self):
        self.poisson = Poisson(14)
        self.poisson.read_data_file('../data/data_poisson.txt')

    def test_initialization(self):
        self.assertEqual(self.poisson.l, 14, 'l value incorrect')

    def test_readdata(self):
        self.assertEqual(self.poisson.data,\
         [0.0778, 0.4381, 0.5152, 0.5764, 0.7552, 0.8960, 1.0155, 1.7508, 2.4764, 2.4933, 2.5978, 2.7680, 3.4559, 3.9147], 'data not read in correctly')

    def test_calculatemean(self):
        mean = self.poisson.calculate_mean()
        self.assertEqual(mean, 14)

    def test_replace_stats_with_data(self):
        l = self.poisson.replace_stats_with_data()
        self.assertEqual(round(l,5), 1.69508)

    def test_pdf(self):
        self.assertEqual(round(self.poisson.pdf(10), 5), 0.06628)
        self.assertEqual(round(self.poisson.pdf(5), 5), 0.00373)

        self.poisson.replace_stats_with_data()
        self.assertEqual(round(self.poisson.pdf(1), 5), 0.31119)
        self.assertEqual(round(self.poisson.pdf(5), 5), 0.02141)

    def test_add(self):
        poisson_one = Poisson(20)
        poisson_two = Poisson(16)
        poisson_sum = poisson_one + poisson_two

        self.assertEqual(poisson_sum.l, 36)


if __name__ == '__main__':
    unittest.main()
