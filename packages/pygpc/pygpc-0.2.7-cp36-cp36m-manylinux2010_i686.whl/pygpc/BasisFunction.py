import scipy.special
import scipy.stats
import numpy as np
from .Grid import *
from .Quadrature import get_quadrature_jacobi_1d
from .Quadrature import get_quadrature_hermite_1d
from .Quadrature import get_quadrature_laguerre_1d


class BasisFunction(object):
    """
    Abstract class of basis functions.
    This base class provides basic properties and methods for the basis functions.
    It cannot be used directly, but inherits properties and methods to the specific basis function sub classes.
    """

    def __init__(self, p):
        """
        Constructor; initialized a Basis function class
        """
        self.p = p
        self.fun = None
        self.fun_der = None
        self.fun_norm = None

    def __call__(self, x, derivative=False):
        """
        Evaluates basis function for argument x

        Parameters
        ----------
        x : float or ndarray of float
            Argument for which the basis function is evaluated
        derivative : boolean, optional, default: False
            Returns derivative of basis function at argument x

        Returns
        -------
        y : float or ndarray of float
            Function value or derivative of basis function at argument x
        """

        if derivative:
            return self.fun_der(x)
        else:
            return self.fun(x)


class Jacobi(BasisFunction):
    """
    Jacobi basis function used in the orthogonal gPC to model beta distributed random variables.
    """

    def __init__(self, p):
        """
        Constructor; initialized a Jacobi basis function

        Parameters
        ----------
        p : dict
            Parameters of the Jacobi polynomial
            - p["i"] ... order
            - p["p"] ... first shape parameter
            - p["q"] ... second shape parameter
        """

        super(Jacobi, self).__init__(p)

        # determine polynomial normalization factor
        beta_norm = (scipy.special.gamma(self.p["q"]) * scipy.special.gamma(self.p["p"]) /
                     scipy.special.gamma(self.p["p"] + self.p["q"]) * 2.0 ** (self.p["p"] + self.p["q"] - 1)) ** (-1)

        jacobi_norm = 2 ** (self.p["p"] + self.p["q"] - 1) / (
                      (2.0 * self.p["i"] + self.p["p"] + self.p["q"] - 1)) * (
                      scipy.special.gamma(self.p["i"] + self.p["p"])) * (
                      scipy.special.gamma(self.p["i"] + self.p["q"])) / (
                              scipy.special.gamma(self.p["i"] + self.p["p"] + self.p["q"] - 1) *
                              scipy.special.factorial(self.p["i"]))

        # normalization factor of polynomial (to later normalize basis functions <psi^2> = int(psi^2*p)dx)
        self.fun_norm = jacobi_norm * beta_norm

        # define basis function
        self.fun = scipy.special.jacobi(self.p["i"],
                                        self.p["q"] - 1,  # beta-pdf: alpha=p /// jacobi-poly: alpha=q-1  !!!
                                        self.p["p"] - 1,  # beta-pdf: beta=q  /// jacobi-poly: beta=p-1   !!!
                                        monic=False) / np.sqrt(self.fun_norm)

        # derivative of polynomial
        self.fun_der = np.polyder(self.fun)

        # integral of fun and fun_der w.r.t. pdf (numerical integration with corresponding weights)
        knots, weights = get_quadrature_jacobi_1d(n=10 * self.p["i"], p=self.p["p"] - 1, q=self.p["q"] - 1)
        self.fun_int = np.dot(self.fun(knots), weights)
        self.fun_der_int = np.dot(self.fun_der(knots), weights)


class Hermite(BasisFunction):
    """
    Hermite basis function used in the orthogonal gPC to model normal distributed random variables.
    """

    def __init__(self, p):
        """
        Constructor; initializes a Hermite basis function

        Parameters
        ----------
        p : dict
            Parameters of the Hermite polynomial
            - p["i"] ... order
        """

        super(Hermite, self).__init__(p)

        # normalization factor of polynomial (to later normalize basis functions <psi^2> = int(psi^2*p)dx)
        self.fun_norm = np.float(scipy.special.factorial(p["i"]))

        # define basis function
        self.fun = scipy.special.hermitenorm(p["i"], monic=False) / np.sqrt(self.fun_norm)

        # derivative of polynomial
        self.fun_der = np.polyder(self.fun)

        # integral of fun and fun_der w.r.t. pdf (numerical integration with corresponding weights)
        if self.p["i"] == 0:
            self.fun_int = 1.0
            self.fun_der_int = 0.0
        else:
            knots, weights = get_quadrature_hermite_1d(n=10 * self.p["i"])
            self.fun_int = np.dot(self.fun(knots), weights)
            self.fun_der_int = np.dot(self.fun_der(knots), weights)


class Laguerre(BasisFunction):
    """
    Laguerre basis function used in the orthogonal gPC to model gamma distributed random variables.
    It is defined in the gpc space from [0, inf]
    """

    def __init__(self, p):
        """
        Constructor; initializes a Laguerre basis function

        Parameters
        ----------
        p : dict
            Parameters of the Laguerre polynomial
            - p["i"] ... order
            - p["alpha"] ... shape parameter (alpha_poly = alpha_pdf - 1)
            - p["beta"] ... rate parameter (   )
        """

        super(Laguerre, self).__init__(p)

        # normalization factor of polynomial (to later normalize basis functions <psi^2> = int(psi^2*p)dx)
        # self.fun_norm = scipy.special.gamma(p["i"]+p["alpha"]+2
        #                                     ) / (scipy.special.factorial(p["i"]) * scipy.special.gamma(p["alpha"] + 2))

        self.fun_norm = (scipy.special.factorial(p["i"]+p["alpha"]) / scipy.special.factorial(p["i"])) / scipy.special.gamma(p["alpha"] + 1)

        # xmax = scipy.stats.gamma.ppf(0.99999999999, a=p["alpha"]+1, loc=0., scale=1.)
        # x = np.linspace(0, xmax, int(5e5))
        # poly = scipy.special.genlaguerre(n=p["i"], alpha=p["alpha"], monic=False)
        # y_pdf = scipy.stats.gamma.pdf(x, a=p["alpha"]+1, loc=0., scale=1.)
        # y_poly = poly(x) * poly(x)
        # y = y_pdf * y_poly
        # self.fun_norm = np.trapz(x=x, y=y)

        # define basis function
        self.fun = scipy.special.genlaguerre(p["i"], alpha=p["alpha"], monic=False) / np.sqrt(self.fun_norm)

        # derivative of polynomial
        self.fun_der = np.polyder(self.fun)

        # integral of fun and fun_der w.r.t. pdf (numerical integration with corresponding weights)
        if self.p["i"] == 0:
            self.fun_int = 1.0
            self.fun_der_int = 0.0
        else:
            knots, weights = get_quadrature_laguerre_1d(n=10 * self.p["i"], alpha=p["alpha"])
            self.fun_int = np.dot(self.fun(knots), weights)
            self.fun_der_int = np.dot(self.fun_der(knots), weights)


class StepUp(BasisFunction):
    """
    StepUp (from 0 to 1) basis function used in the non-orthogonal gPC.
    """

    def __init__(self, p):
        """
        Constructor; initializes a StepUp basis function

        Parameters
        ----------
        p : dict
            Parameters of the StepUp function
            - p["xs"] ... location of step
        """

        super(StepUp, self).__init__(p)

        # normalization factor of function (to later normalize basis functions <psi^2> = int(psi^2*p)dx)
        self.fun_norm = 1.0

        # define basis function
        self.fun = lambda x: 0.0 if x < p["xs"] else (0.5 if x == p["xs"] else 1.0)

        # derivative
        self.fun_der = lambda x: 0.0


class StepDown(BasisFunction):
    """
    StepDown (from 1 to 0) basis function used in the non-orthogonal gPC.
    """

    def __init__(self, p):
        """
        Constructor; initializes a StepDown basis function

        Parameters
        ----------
        p : dict
            Parameters of the StepDown function
            - p["xs"] ... location of step
        """

        super(StepDown, self).__init__(p)

        # normalization factor of function (to later normalize basis functions <psi^2> = int(psi^2*p)dx)
        self.fun_norm = 1.0

        # define basis function
        self.fun = lambda x: 1.0 if x < p["xs"] else (0.5 if x == p["xs"] else 0.0)

        # derivative
        self.fun_der = lambda x: 0.0


class Rect(BasisFunction):
    """
    Rectangular basis function used in the non-orthogonal gPC.
    """

    def __init__(self, p):
        """
        Constructor; initializes a Rect basis function

        Parameters
        ----------
        p : dict
            Parameters of the Rect function
            - p["x1"] ... location of positive flank (0 -> 1)
            - p["x2"] ... location of negative flank (1 -> 0)
        """

        super(Rect, self).__init__(p)

        # normalization factor of function (to later normalize basis functions <psi^2> = int(psi^2*p)dx)
        self.fun_norm = 1.0

        # define basis function
        self.fun = lambda x: 1.0 if p["x1"] < x < p["x2"] else (0.5 if x == p["x1"] or x == p["x2"] else 0.0)

        # derivative
        self.fun_der = lambda x: 0.0


class SigmoidUp(BasisFunction):
    """
    SigmoidUp (from 0 to 1) basis function used in the non-orthogonal gPC.
    """

    def __init__(self, p):
        """
        Constructor; initializes a SigmoidUp basis function

        Parameters
        ----------
        p : dict
            Parameters of the SigmoidUp function
            - p["xs"] ... location of turning point
            - p["r"] ... steepness
        """

        super(SigmoidUp, self).__init__(p)

        # normalization factor of function (to later normalize basis functions <psi^2> = int(psi^2*p)dx)
        self.fun_norm = 1.0

        # define basis function
        self.fun = lambda x: 1.0 / (1 + np.exp(-p["r"] * (x - p["xs"])))

        # derivative
        self.fun_der = lambda x: (p["r"] * np.exp(-p["r"] * (x - p["xs"]))) / (1 + np.exp(-p["r"] * (x - p["xs"])))**2


class SigmoidDown(BasisFunction):
    """
    SigmoidDown (from 0 to 1) basis function used in the non-orthogonal gPC.
    """

    def __init__(self, p):
        """
        Constructor; initializes a SigmoidDown basis function

        Parameters
        ----------
        p : dict
            Parameters of the SigmoidDown function
            - p["xs"] ... location of turning point
            - p["r"] ... steepness
        """

        super(SigmoidDown, self).__init__(p)

        # normalization factor of function (to later normalize basis functions <psi^2> = int(psi^2*p)dx)
        self.fun_norm = 1.0

        # define basis function
        self.fun = lambda x: 1.0 / (1 + np.exp(-p["r"] * (- x + p["xs"])))

        # derivative
        self.fun_der = lambda x: (- p["r"] * np.exp(-p["r"] * (- x + p["xs"]))) / (1 + np.exp(-p["r"] * (- x + p["xs"])))**2