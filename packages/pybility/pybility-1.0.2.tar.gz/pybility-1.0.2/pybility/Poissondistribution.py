from .Generaldistribution import Distribution
from math import sqrt, pi, factorial, log, exp, e, gamma
import matplotlib
import matplotlib.pyplot as plt
import os
import warnings
import pybility


class Poisson(Distribution):
    """ Poisson distribution class for calculating and 
    visualizing a Poisson distribution
    
    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data (list of floats) a list of floats to be extracted from the data file
        l (float) representing the mean rate at which an event occurrs
    """


    def __init__(self, l = 1.6950):
        
        self.l = l

        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev())


    def calculate_mean(self):
        """ Function to calculate the mean from lambda (l)
        Args: 
            None
        Returns:
            float: mean of the Poisson distribution"""
        
        self.mean = self.l
        return self.mean


    def calculate_stdev(self, sample = True):
        """ Function to calculate the standard deviation
        from lambda (l) and update the class instance
        Args:
            None
        Returns:
            float: standard deviation of the Poisson distribution"""

        self.stdev = sqrt(self.l)
        return self.stdev


    def replace_stats_with_data(self):
        """Function to calculate l from the data set. The function updates the l variables of the object.
        Args: 
            None
        Returns: 
            float: the l value
        """
        
        self.l = sum(self.data)/len(self.data)
        self.calculate_mean()
        self.calculate_stdev()

        return self.l


    def plot_histogram(self):
        """Function to output a histogram of the instance variable data using
        matplotlib pyplot library.
        Args:
            None
        Returns:
            None
        """
        
        self.plot_histogram_pdf()

    def pdf(self, k):
        """Function to evaluate the probability density (mass) function at point k
        Args:
            k (float): point at which the probability density function is calculated
        Returns:
            float: value of pdf at k"""

        try:
            result = exp( k*log(self.l) - self.l - log(gamma(k+1)) )
        except OverflowError:
            result = float('inf')

        return result


    def plot_histogram_pdf(self, in_terminal = False, n_samples = 50):
        """Function to plot the normalized histogram of the data and a plot of the 
        probability density function along the same range
        Args:
            in_terminal (bool): whether or not to plot on-screen (default: False)
            n_samples (int): number of data points (default: 50)
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
        """

        if not self.data:
            src = os.path.join(os.path.dirname(pybility.__file__), 'data/data_poisson.txt')
            self.read_data_file(src)
            self.replace_stats_with_data()
            warnings.warn('Data not specified; using default data. Use read_data_file(path/to/file) to specify a file. \n', Warning, stacklevel=2)

        min_range = min(self.data)
        max_range = max(self.data)

        # calculates the interval between x values
        interval = 1.0 * (max_range - min_range) / n_samples

        x = []
        y = []

        # calculate the x values to visualize
        for i in range(n_samples):
            tmp = min_range + interval*i
            x.append(tmp)
            y.append(self.pdf(tmp))

        if in_terminal:
            #plots on-screen in terminal
            matplotlib.use('module://drawilleplot')

        # make the plots
        fig, axes = plt.subplots(2,sharex=True)
        fig.subplots_adjust(hspace=.5)
        axes[0].hist(self.data, density=True)
        axes[0].set_title('Normed Histogram of Data')
        axes[0].set_ylabel('Density')

        axes[1].plot(x, y)
        axes[1].set_title('Poisson Distribution for \n Sample Mean and Sample Standard Deviation')
        axes[0].set_ylabel('Density')
        plt.show()
        fig.clear()

        return x, y    
    
    
    def __add__(self, other):

        """Function to add together two Poisson distributions
        Args:
            other (Poisson): Poisson instance
        Returns:
            Poisson: Poisson distribution
        """

        l_sum = self.l + other.l
        poisson_sum = Poisson(l_sum)
        poisson_sum.calculate_mean()
        poisson_sum.calculate_stdev()

        return poisson_sum


    def __mul__(self, other):
        """Function to multiply togehter two independent Poisson distributions
        Args:
            other (Poisson): Poisson instance
        Returns:
            Poisson: Poisson distribution
        """
        l_prod = self.l * other.l

        return Poisson(l_prod)


    def __repr__(self):
        """Function to output the characteristics of the Poisson instance
        Args:
            None
        Return:
            string: charcateristics of the Poisson object
            """

        return 'mean {}, standard deviation {}, lambda {}'.format(self.mean, self.stdev, self.l)

