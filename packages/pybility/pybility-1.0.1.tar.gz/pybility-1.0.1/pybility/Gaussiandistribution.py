from math import pi, sqrt, exp
import matplotlib
import matplotlib.pyplot as plt
from .Generaldistribution import Distribution
import os
import warnings
import pybility
from random import gauss


class Gaussian(Distribution):
    """ Gaussian distribution class for calculating and 
    visualizing a Gaussian distribution.
    
    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data (list of floats) a list of floats extracted from the data file
            
    """
    def __init__(self, mu=0, sigma=1):
        
        Distribution.__init__(self, mu, sigma)
        
    
    def calculate_mean(self):
        """Function to calculate the mean of the data set.
        Args: 
            None
        Returns: 
            float: mean of the data set
        """
                    
        avg = 1.0 * sum(self.data) / len(self.data)
        self.mean = avg
        
        return self.mean


    def calculate_stdev(self, sample=True):
        """Function to calculate the standard deviation of the data set.
        Args: 
            sample (bool): whether the data represents a sample or population
        Returns:
            float: standard deviation of the data set
        """

        if sample:
            n = len(self.data) - 1
        else:
            n = len(self.data)

        mean = self.calculate_mean()
        sigma = sum( [ (x - mean)**2 for x in self.data ] )
        sigma = sqrt(sigma / n)
            
        self.stdev = sigma
        return sigma


    def plot_histogram(self, in_terminal = False, synthesize_data = False, n_samples = 50):
        """Function to output a histogram of the instance variable data using 
        matplotlib pyplot library.
        Args:
            in_terminal (bool): whether or not to plot on-screen (default: False)
            synthesize_data (bool): whether or not to randomly sample the Gaussian distribution, generate and store the data (default: False)
            n_samples (int): number of data points (default: 50)
        Returns:
            None
        """
        
        if synthesize_data:
            self.data = [ gauss(self.mean, self.stdev) for x in range(n_samples) ]

        if not self.data:
            src = os.path.join(os.path.dirname(pybility.__file__), 'data/data.txt')
            self.read_data_file(src)
            self.calculate_mean()
            self.calculate_stdev()
            warnings.warn('Data not specified; using default data. Use read_data_file(path/to/file) to specify a file. \n', Warning, stacklevel=2)
    
        if in_terminal:
            #plots on-screen in terminal
            matplotlib.use('module://drawilleplot')

        plt.hist(self.data)
        plt.title('Histogram of Data')
        plt.xlabel('data')
        plt.ylabel('count')
        plt.show()
        plt.close()


    def pdf(self, x):
        """Probability density function calculator for the gaussian distribution.
        Args:
            x (float): point for calculating the probability density function
        Returns:
            float: probability density function output
        """
        
        return (1.0 / (self.stdev * sqrt(2*pi))) * exp(-0.5*((x - self.mean) / self.stdev) ** 2)
        

    def plot_histogram_pdf(self, in_terminal = False, synthesize_data = False, n_samples = 50):
        """Function to plot the normalized histogram of the data and a plot of the 
        probability density function along the same range
        
        Args:
            in_terminal (bool): whether or not to plot on-screen (default: False)
            synthesize_data (bool): whether or not to randomly sample the Gaussian distribution, generate and store the data (default: False)
            n_samples (int): number of data points (default: 50)
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
            
        """
        
        mu = self.mean
        sigma = self.stdev
        
        if synthesize_data:
            self.data = [ gauss(self.mean, self.stdev) for x in range(n_samples) ]
        
        if not self.data:
            src = os.path.join(os.path.dirname(pybility.__file__), 'data/data.txt')
            self.read_data_file(src)
            self.calculate_mean()
            self.calculate_stdev()
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
        axes[1].set_title('Normal Distribution for \n Sample Mean and Sample Standard Deviation')
        axes[0].set_ylabel('Density')
        plt.show()
        fig.clear()

        return x, y
    

    def __add__(self, other):
        """Function to add together two Gaussian distributions
        Args:
            other (Gaussian): Gaussian instance
        Returns:
            Gaussian: Gaussian distribution
        """

        result_mean = self.mean + other.mean
        result_stdev = sqrt(self.stdev**2 + other.stdev**2)
        result = Gaussian(result_mean, result_stdev)

        return result


    def __mul__(self, other):
        """Function to multiply togehter two independent Guassian distributions
        Args:
            other (Gaussian): Gaussian instance
        Returns:
            Gaussian: Gaussian distribution
        """
        
        result_mean = self.mean * other.mean
        result_stdev = sqrt( (self.stdev**2 + self.mean**2) * (other.stdev**2 + other.mean**2) - self.mean**2 * other.mean**2 )
        result = Gaussian(result_mean, result_stdev)
        
        return result


    def __repr__(self):
        """Function to output the characteristics of the Gaussian instance
        Args:
            None
        Returns:
            string: characteristics of the Gaussian
        """
        
        return "mean {}, standard deviation {}".format(self.mean, self.stdev)
