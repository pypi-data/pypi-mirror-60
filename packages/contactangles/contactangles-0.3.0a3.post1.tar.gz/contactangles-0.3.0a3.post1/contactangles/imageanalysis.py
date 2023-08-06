import skimage
from skimage import (feature, io)
from skimage.viewer import ImageViewer
from skimage.viewer import plugins
from skimage.viewer.widgets import Slider, ComboBox
from skimage.viewer.canvastools import RectangleTool

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

import numpy as np

import numba

import scipy as scipy
import scipy.optimize as opt
from scipy.spatial import distance
from scipy.integrate import solve_ivp
from scipy.optimize import dual_annealing, minimize

import sys

import argparse

import warnings

L = 'left'
R = 'right'
T = 'top'
B = 'bottom'


def positive_int(value: int) -> int:
    if int(value) <= 0:
        raise argparse.ArgumentTypeError(f'{value} is an invalid positive int'
                                         'value')
    return int(value)


def positive_float(value: float) -> float:
    if float(value) <= 0:
        raise argparse.ArgumentTypeError(f'{value} is an invalid positive'
                                         'float value')
    return float(value)


def get_crop(image):
    plt.ioff()
    print('Waiting for input, please crop the image as desired and hit enter')
    viewer = ImageViewer(image)
    rect_tool = RectangleTool(viewer, on_enter=viewer.closeEvent)
    viewer.show()

    bounds = np.array(rect_tool.extents)
    if (bounds[0] < 0 or bounds[1] > image.shape[1] or bounds[2] < 0
            or bounds[3] > image.shape[0]):
        print(f'Bounds = {bounds} and shape = {image.shape}')
        raise ValueError('Bounds outside image, make sure to select within')

    plt.ion()
    return np.array(np.round(bounds), dtype=int)


def calculate_angle(v1, v2):
    '''
    Compute the angle between two vectors of equal length

    :param v1: numpy array
    :param v2: numpy array
    :return: angle between the two vectors v1 and v2 in degrees
    '''
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    return np.arccos(np.dot(v1_u, v2_u)) * 360 / 2 / np.pi


def baseF(x, a):
    return np.dot(a, np.power(x, range(len(a))))


def crop_points(image, bounds, f=None):
    '''
    Return a cropped image with points only lying inside the bounds

    :param image: numpy array of [x,y] coordinates of detected edges
    :param bounds: list of [left, right, top, bottom] image bounds - because
                   of the way that images are read, bottom > top numerically
    :return: abbreviated numpy array of [x,y] coordinates that are within
             bounds
    '''

    if f is None:
        f = {i: lambda x, y: x for i in [L, R]}
        f[T] = lambda x, y: y
        f[B] = lambda x, y: y

        if bounds[2] > bounds[3]:
            warnings.warn('Check the order of the bounds, as bottom > top')

        if any([x < 0 for x in bounds]):
            warnings.warn('All bounds must be positive')

    new_im = np.array([[x,y] for x, y in image if (f[L](x, y) >= bounds[0] and
                                                   f[R](x, y) <= bounds[1] and
                                                   f[T](x, y) >= bounds[2] and
                                                   f[B](x, y) <= bounds[3])])

    return new_im


def fit_line(points, order=1):
    '''
    Returns the set of coefficients of the form y = Σ a[i]*x**i for i = 0 ..
    order using np.linalg
    '''
    X = np.ones((points.shape[0], order + 1))
    x = points[:, 0]
    for col in range(order + 1):
        X[:, col] = np.power(x, col)

    y = points[:, 1]
    a = np.linalg.lstsq(X, y, rcond=None)

    try:
        assert(len(a[0]) == order + 1)
    except AssertionError as e:
        print('There is something wrong with the baseline fitting procedure, '
              'the program cannot continue execution')
        raise(e)

    return a


def sigma_setter(image, σ=1, bounds=None):
    plt.ioff()
    # edges = feature.canny(image, sigma=σ)
    viewer = ImageViewer(image)
    if bounds is not None:
        viewer.ax.set_xlim(bounds[0:2])
        viewer.ax.set_ylim(bounds[-1:-3:-1])

    canny = CannyPlugin()
    viewer += canny
    out = viewer.show()[0][1]

    σ = out['sigma']
    low = out['low_threshold']
    high = out['high_threshold']

    print(f'Proceeding with sigma = {σ : 6.2f}')
    plt.ion()
    return σ, low, high


def extract_edges(image, σ=1, low=None, high=None):
    '''
    Compute the detected edges using the canny algorithm

    :param image: numpy grayscale image
    :param σ: canny filter value to use
    :param check_σ: flag whether to visually check the edges that are detected
    :return: list of [x,y] coordinates for the detected edges
    '''
    edges = feature.canny(image, sigma=σ, low_threshold=low,
                          high_threshold=high)
    edges = np.array([[x, y] for y, row in enumerate(edges)
                      for x, val in enumerate(row) if val])
    return edges


def generate_droplet_width(crop, bounds=None, f=None):
    # Look for the greatest distance between points on the baseline
    # by calculating points that are in the circle within the linear
    # threshold

    if bounds is not None:
        just_inside = crop_points(crop, bounds, f=f)
    else:
        just_inside = crop

    limits = {L: np.amin(just_inside[:, 0]),
              R: np.amax(just_inside[:, 0])}
    return limits


def generate_vectors(linear_points, limits, ε, a, tolerance=None):

    if tolerance is None:
        tolerance = 8
    # Define baseline vector - slope will just be approximated from
    # FD at each side (i.e. limit[0] and limit[1])

    bv = {side: ([1, (baseF(pos + ε/2, a) - baseF(pos - ε/2, a)) / ε]) for
          side, pos in limits.items()}

    # Initialize paramater dictionaries
    b = {}
    m = {}

    # Initialize vector dictionary
    v = {}

    # Initialize vertical success dictionary
    vertical = {L: False, R: False}

    for side in [L, R]:
        # Get the values for this side of the drop
        fits, residual, rank, sing_vals = fit_line(linear_points[side])

        # Extract the parameters
        b[side], m[side] = fits

        # Do all the checks I can think of to make sure that fit succeeded
        if (rank != 1
                and np.prod(sing_vals) > linear_points[side].shape[0]
                and residual < tolerance):
            # Check to make sure the line isn't vertical
            v[side] = np.array([1, m[side]])
        else:
            # Okay, we've got a verticalish line, so swap x <--> y
            # and fit to c' = A' * θ'
            linear_points_prime = linear_points[side][:, ::-1]

            b[side], m[side] = fit_line(linear_points_prime)[0]

            v[side] = np.array([m[side], 1])

            vertical[side] = True

    # Reorient vectors to compute physically correct angles
    if v[L][1] > 0:
        v[L] = -v[L]
    if v[R][1] < 0:
        v[R] = -v[R]

    return v, b, m, bv, vertical


def output_text(time, φ, baseline_width, volume):
    print(f'At time {time : 6.3f}: \t'
          f' Contact angle left (deg): {ϕ[L] : 6.3f} \t'
          f' Contact angle right (deg): {ϕ[R] : 6.3f} \t'
          f' Contact angle average (deg): {(ϕ[L]+ϕ[R])/2 : 6.3f} \t'
          f' Baseline width (px): {baseline_width : 4.1f}')


def dist(param, points):
    '''
    Calculate the total distance from the calculated circle to the points

    :param param:  list of 3 elements with the center of a circle and its
                   radius
    :param points: list of (x, y) points that should be lying on the circle
    :return: the sum of squared errrors from the points on the circle with
             the provided parameters
    '''
    *z, r = param
    ar = [(np.linalg.norm(np.array(z) - np.array(point)) - r) ** 2
          for point in points]
    return np.sum(ar)


def fit_circle(points, width=None, start=False):
    if width is None:
        width = np.max(points[:, 0]) - np.min(points[:, 1])

    if start:
        # Try to fit a circle to the points that we have extracted,
        # only varying the radius about the center of all the points
        z = np.mean(points, axis=0)
        res = opt.minimize(lambda x: dist([*z, x], points),
                           width / 2)

        # Get the results
        res['x'] = np.array([*z, res['x'][0]])
    else:
        # Fit this new set of points, using the full set of parameters
        res = opt.minimize(lambda x: dist(x, points),
                           np.concatenate((np.mean(points, axis=0),
                                           [width / 4])))

    return res


def generate_circle_vectors(intersection):
    x_t, y_t = intersection
    # For contact angle, want interior angle, so look at vector in
    # negative x direction (this is our baseline)
    v1 = np.array([-1, 0])

    # Now get line tangent to circle at x_t, y_t
    if y_t != 0:
        slope = - x_t / y_t
        v2 = np.array([1, slope])
        v2 = v2 / np.linalg.norm(v2)
        if y_t < 0:
            # We want the interior angle, so when the line is
            # above the origin (into more negative y), look left
            v2 = -v2
    else:
        v2 = np.array([0, 1])

    return v1, v2


def find_intersection(baseline_coeffs, circ_params):
    *z, r = circ_params
    b, m = baseline_coeffs[0:2]
    # Now we need to actually get the points of intersection
    # and the angles from these fitted curves. Rather than brute force
    # numerical solution, use combinations of coordinate translations and
    # rotations to arrive at a horizontal line passing through a circle.
    # First step will be to translate the origin to the center-point
    # of our fitted circle
    # x = x - z[0], y = y - z[1]
    # Circle : x**2 + y**2 = r**2
    # Line : y = m * x + (m * z[0] + b - z[1])
    # Now we need to rotate clockwise about the origin by an angle q,
    # s.t. tan(q) = m
    # Our transformation is defined by the typical rotation matrix
    #   [x;y] = [ [ cos(q) , sin(q) ] ;
    #             [-sin(q) , cos(q) ] ] * [ x ; y ]
    # Circle : x**2 + y**2 = r**2
    # Line : y = (m*z[0] + b[0] - z[1])/sqrt(1 + m**2)
    # (no dependence on x - as expected)

    # With this simplified scenario, we can easily identify the points
    # (x,y) where the line y = B
    # intersects the circle x**2 + y**2 = r**2
    # In our transformed coordinates, only keeping the positive root,
    # this is:

    B = (m * z[0] + b - z[1]) / np.sqrt(1 + m**2)

    if B > r:
        raise ValueError("The circle and baseline do not appear to intersect")
    x_t = np.sqrt(r ** 2 - B ** 2)
    y_t = B

    # TODO:// replace the fixed linear baseline with linear
    # approximations near the intersection points

    return x_t, y_t


def parse_cmdline(argv=None):
    '''
    Extract command line arguments to impact program execution

    :param argv: List of strings that were passed at the command line
    :return: Namespace of arguments and their values
    '''

    parser = argparse.ArgumentParser(description='Calculate the contact '
                                     'angles '
                                     'from the provided image or '
                                     'video file')
    parser.add_argument('path', help='relative or absolute path to '
                                     'either image/video file to be '
                                     'analyzed, or a directory in which to '
                                     'analyze all video/image files',
                        default='./', nargs='?')
    parser.add_argument('-b', '--baselineThreshold', type=positive_int,
                        default=20,
                        help='Pixel width that determines where '
                             'baseline lies',
                        action='store', dest='baseline_threshold')
    parser.add_argument('-o', '--baselineOrder', type=positive_int, default=1,
                        help='The polynomial order that will be used in '
                             'baseline fitting',
                        action='store', dest='base_ord')
    parser.add_argument('-c', '--circleThreshold', type=positive_int,
                        default=5,
                        help='Number of pixels above the baseline at which '
                             'points are considered on the droplet',
                        action='store', dest='circ_thresh')
    parser.add_argument('-l', '--linearThreshold', type=positive_int,
                        default=10,
                        action='store', dest='lin_thresh',
                        help='The number of pixels inside the circle which '
                             'can be considered to be linear and should be '
                             'fit to obtain angles')
    parser.add_argument('-f', '--frequency', type=positive_float, default=1,
                        action='store', dest='frame_rate',
                        help='Frequency at which to analyze images from a '
                             'video')
    parser.add_argument('--sigma', type=float, default=1,
                        action='store', dest='σ',
                        help='Initial image filter used for edge detection')
    parser.add_argument('--checkFilter', action='store_true',
                        help='Set flag to check the provided filter value '
                             'or procede without any confirmation')
    parser.add_argument('-s', '--startSeconds', type=positive_float,
                        default=10,
                        action='store', dest='video_start_time',
                        help='Amount of time in which video should be burned '
                             'in before beginning analysis')
    parser.add_argument('--fitType', choices=['linear', 'circular',
                                              'bashforth-adams'],
                        default='linear', type=str, action='store',
                        dest='fit_type',
                        help='Type of fit to perform to identify the contact '
                             'angles')
    parser.add_argument('--tolerance', type=positive_float, dest='ε',
                        action='store', default=1e-2,
                        help='Finite difference tolerance')
    parser.add_argument('--maxIters', type=positive_int, dest='lim',
                        action='store', default=10,
                        help='Maximum number of circle fitting iterations')
    parser.add_argument('--verticalTolerance', type=positive_int,
                        dest='tolerance', action='store', default=8,
                        help='Pixel error for how bad the fit is before we '
                             'try fitting x = my + b')
    parser.add_argument('--blockAtEnd', action='store_true',
                        dest='block_at_end',
                        help='Flag to keep plots at the end of the script '
                             'open for user review')

    args = parser.parse_args(argv)

    return args

def sim_bashforth_adams(h, a=1, b=1):
    @numba.jit(nopython=True)
    def bashforth_adams(t, y, a, b):
        x, z = y
        t = t / 180 * np.pi
        dxdphi = b*x*np.cos(t) / (a**2 * b * x * z + 2 * x - b * np.sin(t))
        dzdphi = b*x*np.sin(t) / (a**2 * b * x * z + 2 * x - b * np.sin(t))
        return dxdphi, dzdphi

    height = lambda t, y, a, b: y[1] - h
    height.terminal = True
    sol_l = solve_ivp(bashforth_adams, (0, -180) , (1e-5, 0), args=(a, b, ),
                      method='BDF',
                      t_eval=np.linspace(0, -180, num=500), events=height)
    sol_r = solve_ivp(bashforth_adams, (0, 180) , (1e-5, 0), args=(a, b, ),
                      method='BDF',
                      t_eval=np.linspace(0, 180, num=500), events=height)

    angles = np.hstack((sol_l.t, sol_r.t[::-1])).T
    pred = np.vstack([np.hstack((sol_l.y[0],sol_r.y[0][::-1])),
                      np.hstack((sol_l.y[1],sol_r.y[1][::-1]))]).T

    return angles, pred

def fit_bashforth_adams(data, a=0.1, b=3):

    def calc_error(h, params):
        a, b = params

        _, pred = sim_bashforth_adams(h, a=a, b=b)

        dist = distance.cdist(data, pred)
        return np.linalg.norm(np.min(dist, axis=1))

    x_0 = (a, b)
    bounds = [[0,10], [0, 100]]

    h = np.max(data[:, 1])
    opt = minimize(lambda x: calc_error(h, x), x_0, method='Nelder-Mead',
                   options={'disp':False})
    return opt

class CannyPlugin(plugins.OverlayPlugin):

    name = 'Canny Filter'

    def __init__(self, *args, **kwargs):
        super().__init__(image_filter=feature.canny, **kwargs)
        self.sigma = 0
        self.low_threshold = 1
        self.high_threshold = 1

    def add_widget(self, widget):
        super().add_widget(widget)

        if widget.ptype == 'kwarg':
            def update(*widget_args):
                setattr(self, widget.name, widget.val)
                self.filter_image(*widget_args)

            widget.callback = update

    def attach(self, image_viewer):
        image = image_viewer.image
        imin, imax = skimage.dtype_limits(image, clip_negative=False)
        itype = 'float' if np.issubdtype(image.dtype, np.floating) else 'int'
        self.add_widget(Slider('sigma', 0, 2, update_on='release'))
        self.add_widget(Slider('low_threshold', imin, imax, value_type=itype,
                        update_on='release'))
        self.add_widget(Slider('high_threshold', imin, imax, value_type=itype,
                        update_on='release'))
        self.add_widget(ComboBox('color', self.color_names, ptype='plugin'))
        # Call parent method at end b/c it calls `filter_image`, which needs
        # the values specified by the widgets. Alternatively, move call to
        # parent method to beginning and add a call to `self.filter_image()`
        super(CannyPlugin,self).attach(image_viewer)

    def output(self):
        new = (super().output()[0], {'sigma': self.sigma,
                                     'low_threshold': self.low_threshold,
                                     'high_threshold': self.high_threshold})
        return new
