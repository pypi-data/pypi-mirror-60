from .Generaldistribution import Distribution
from math import sqrt, pi, factorial
import matplotlib
import matplotlib.pyplot as plt
import os
import pybility


class Binomial(Distribution):
    """ Binomial distribution class for calculating and 
    visualizing a Binomial distribution.
    
    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data (list of floats) a list of floats to be extracted from the data file
        n (int) number of independent experiments
        p (float) representing the probability of an event occurring
    """
    
    def __init__(self, p = 0.5, n = 25):


        self.p = p
        self.n = n

        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev()) 
    
    def calculate_mean(self):
        """Function to calculate the mean from p and n
        Args: 
            None
        Returns: 
            float: mean of the distribution
    
        """
        self.mean = self.n * self.p
        return self.mean

    
    def calculate_stdev(self, sample = True):
        """Function to calculate the standard deviation from p and n.
        Args: 
            None
        Returns: 
            float: standard deviation of the data set
    
        """
        self.stdev = sqrt(self.n * self.p * (1 - self.p))
        return self.stdev


    def replace_stats_with_data(self): 
        """Function to calculate p and n from the data set. The function updates the p and n variables of the object.
        Args: 
            None
        Returns: 
            float: the p value
            float: the n value
        """

        self.n = len(self.data)
        self.p = sum(self.data)/len(self.data)
        self.mean = self.calculate_mean()
        self.stdev = self.calculate_stdev()
        
        return self.p, self.n

    def plot_histogram(self, in_terminal = False):
        """Function to output a histogram of the instance variable data using 
        matplotlib pyplot library.
        Args:
            in_terminal (bool): whether or not to plot on-screen (default: False)
        Returns:
            None
        """
        #data = [ 0 if random.uniform(0,1) < p else 1 for x in range(n_samples) ] 
        if in_terminal:
            #plots on-screen in terminal
            matplotlib.use('module://drawilleplot')

        plt.bar(x = ['0', '1'], height = [(1 - self.p) * self.n, self.p * self.n])
        plt.title('Bar Chart of Data')
        plt.xlabel('outcome')
        plt.ylabel('count')

        plt.show()
        plt.close()


    def pdf(self, k):
        """Probability density function calculator for the binomial distribution.
        Args:
            k (float): point for calculating the probability density function
        Returns:
            float: probability density function output
        """

        pref = factorial(self.n) / ( factorial(k) * factorial(self.n - k) )
        return pref * self.p**k * (1 - self.p)**(self.n - k)


    def plot_histogram_pdf(self, in_terminal = False, n_samples = 50): 
        """Function to plot the pdf of the binomial distribution
        Args:
            in_terminal (bool): whether or not to plot on-screen (default: False)
            n_samples (int): number of data points (default: 50)
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
        """

        x = []; y = []

        for k in range(self.n+1):
            x.append(k)
            y.append(self.pdf(k))
        
        if in_terminal:
            #plots on-screen in terminal
            matplotlib.use('module://drawilleplot')

        # make the plots
        plt.bar(x, y)
        plt.title('Distribution of Outcomes')
        plt.ylabel('Probability')
        plt.xlabel('Outcome')

        plt.show()
        plt.close()

        return x, y

    
    def __add__(self, other):
        """Function to add together two Binomial distributions with equal p
        Args:
            other (Binomial): Binomial instance
        Returns:
            Binomial: Binomial distribution
        """
        
        try:
            assert self.p == other.p, 'p values are not equal'
        except AssertionError as error:
            raise

        n_sum = self.n + other.n
        binomial_sum = Binomial(self.p, n_sum) 
        binomial_sum.calculate_mean()
        binomial_sum.calculate_stdev()

        return binomial_sum
    

    def __repr__(self):
        """Function to output the characteristics of the Binomial instance
        
        Args:
            None
        
        Return:
            string: charcateristics of the Binomial object
            """
        return 'mean {}, standard deviation {}, p {}, n {}'.format(self.mean, self.stdev, self.p, self.n)
