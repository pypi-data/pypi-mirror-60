﻿import numpy as np
import scipy
import matplotlib.pyplot as plt
import sklearn.mixture as mixture

from atomap.sublattice import Sublattice
from atomap.atom_lattice import Atom_Lattice


def centered_distance_matrix(centre, det_image):
    """Makes a matrix the same size as det_image centre around a particular
    point.

    Parameters
    ----------
    centre : tuple
        x and y position of where the centre of the matrix should be.
    det_image : NumPy array
        Detector map as 2D array.

    Returns
    -------
    NumPy Array

    Example
    -------
    >>> import hyperspy.api as hs
    >>> import atomap.api as am
    >>> s = am.example_data.get_detector_image_signal()
    >>> centered_matrix = am.quant.centered_distance_matrix((256, 256), s.data)

    """
    # makes a matrix centred around 'centre' the same size as the det_image.
    x, y = np.meshgrid(range(det_image.shape[0]), range(det_image.shape[0]))
    return np.sqrt((x - (centre[1]) + 1)**2 + (y - (centre[0]))**2)


def _detector_threshold(det_image):
    """Using an input detector image. The function thresholds returning a
    binary image.

    Parameters
    ----------
    det_image : NumPy array
        Detector map as 2D array.

    Returns
    -------
    threshold_image : NumPy array
        Boolean image demonstrating the active region of the detector.

    Example
    -------
    >>> import atomap.api as am
    >>> s_det_image = am.example_data.get_detector_image_signal()
    >>> threshold_image = am.quant._detector_threshold(s_det_image.data)

    """
    det_min, det_max = np.min(det_image), np.max(det_image)
    threshold_image = (det_image - det_min) / (det_max - det_min)
    threshold_image = (threshold_image >= 0.25)
    return threshold_image


def _func(x, a, b, c):
    return a * (x**-b) + c


def _radial_profile(data, centre):
    """Creates a 1D profile from an image by integrating azimuthally around a
    central point.

    Parameters
    ----------
    data : NumPy array
    centre : tuple

    Return
    ------
    radial_profile : NumPy array

    Example
    -------
    >>> import atomap.api as am
    >>> s_det_image = am.example_data.get_detector_image_signal()
    >>> radial_profile = am.quant._radial_profile(s_det_image.data, (256, 256))

    """

    y, x = np.indices((data.shape))
    r = np.sqrt((x - centre[0])**2 + (y - centre[1])**2)
    r = r.astype(np.int)

    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr
    return radialprofile


class InteractiveFluxAnalyser:

    def __init__(self, profile, radius, flux_profile, limits=None):
        if limits is None:
            self.profile = profile[0]
            self.radius = radius
            self.flux_profile = flux_profile
            self.left = np.int(min(self.profile.get_xdata()))
            self.right = np.int(max(self.profile.get_xdata()))
            self.l_line = self.profile.axes.axvline(
                    self.left, color='firebrick', linestyle='--')
            self.r_line = self.profile.axes.axvline(
                    self.right, color='seagreen', linestyle='--')
            self.cid = self.profile.figure.canvas.mpl_connect(
                    'button_press_event', self.onclick)
            self.key = self.profile.figure.canvas.mpl_connect(
                    'key_press_event', self.onkey)
        else:
            self.left, self.right = limits
            self._set_coords()

    def __call__(self):
        self._set_coords()
        print('Final coordinates are: {}, {}!'.format(self.left, self.right))

    def _set_coords(self):
        self.coords = [self.left, self.right]

    def onclick(self, event):
        # print('click', vars(event))
        if event.inaxes != self.profile.axes:
            return
        if event.button == 1:  # Left mouse button
            left = np.int(event.xdata)
            if left < self.right:
                self.left = left
            self.l_line.set_xdata(self.left)
            self.profile.figure.canvas.draw_idle()
        elif event.button == 3:  # Right mouse button
            right = np.int(event.xdata)
            if right > self.left:
                self.right = right
            self.r_line.set_xdata(self.right)
            self.profile.figure.canvas.draw_idle()
        print('Coordinates selected', self.left, self.right)

    def onkey(self, event):
        if event.inaxes != self.profile.axes:
            return
        if event.key == 'enter':  # Enter key
            event.canvas.mpl_disconnect(self.cid)
            event.canvas.mpl_disconnect(self.key)
            self()


def find_flux_limits(flux_pattern, conv_angle, limits=None):
    """Using an input flux_pattern to create a line profile. The user is then
    able to select the region of this profile which follows an exponential.

    Parameters
    ----------
    flux_pattern : NumPy array
    conv_angle : float
    limits : tuple, optional
        If this is not specified, the limits must be set interactively.
        Must have 2 values: (left limit, right limit), for example (103, 406).
        Default value is None, which gives opens a window to select the limits
        interactively.

    Returns
    -------
    profiler : object
        From the InteractiveFluxAnalyser class containing coordinates selected
        by the user.
    flux_profile : np.array
        1D array containing the values for the created flux_profile.

    """
    if (limits is not None) and (len(limits) != 2):
        raise ValueError(
                "limits must either be None to get an interactive window, "
                "or tuple with two values. Currently it is {0}".format(limits))
    elif (limits is not None) and (limits[0] > limits[1]):
        raise ValueError("limits[1] must be larger than limits[0], currently "
                         " limits is {0}".format(limits))
    # normalise flux image to be scaled 0-1.
    low_values_indices = flux_pattern < 0
    flux_pattern[low_values_indices] = 0
    flux_pattern = flux_pattern / np.max(flux_pattern)

    # convert 2D image into a 1D profile.
    centre = scipy.ndimage.measurements.center_of_mass(flux_pattern)
    flux_profile = _radial_profile(flux_pattern, centre[::-1])
    grad = np.gradient(flux_profile)
    # scale flux_profile relative to the bright field disc.
    x = np.array(range(flux_profile.shape[0]))
    radius = x * conv_angle / np.argmin(grad)

    # Plot the radial flux profile and allow the user to select the region for
    # power-law fitting.
    if limits is None:
        fig = plt.figure()
        fig.suptitle('Radial Flux Profile: select power-law region with left '
                     'and right mouse button.\n'
                     'Press the Enter key to confirm selection.',
                     fontsize=10)
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.plot(radius, flux_profile)
        ax1.set_title('Radial Profile')
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.set_title('Logarithmic Profile')
        profile = ax2.plot(radius, flux_profile)
        ax2.set_yscale('log')
        fig.subplots_adjust(hspace=0.3)
        fig.show()
    else:
        profile = None

    profiler = InteractiveFluxAnalyser(profile, radius, flux_profile,
                                       limits=limits)

    return(profiler, flux_profile)


def analyse_flux(coords, flux_profile, conv_angle):
    """Using and input flux profile and the coordinate range of where the
    profile behaves exponentially, the exponent is determined and an outer
    cut-off (important for experimentally determined flux_profile).

    Parameters
    ----------
    image : NumPy array
        Experimental image to be normalised.
    det_image : NumPy array
        Detector map as 2D array.
    flux_image : 'None' otherwise NumPy array
        Flux image is required for a flux weighted detector normalisation,
        if none is supplied the normal thresholding normalisation will
        be applied.

    Returns
    -------
    exponent : float
        The value of the exponent from the fitted exponential curve.
    outer_cutoff : float
        The outer limit of the flux profile beyond which no more electrons are
        seen. This is particularly important for experimental flux profiles
        and large detectors where not all of the detector is illuminated during
        a given experiment.

    """
    grad = np.gradient(flux_profile)
    x = np.array(range(flux_profile.shape[0]))
    radius = x * conv_angle / np.argmin(grad)
    lower = np.sum(radius < coords[0]) - 1
    upper = np.sum(radius < coords[1])
    xdata = radius[lower:upper]
    ydata = flux_profile[lower:upper]
    popt, pcov = scipy.optimize.curve_fit(_func, xdata, ydata, p0=([1, 1, 1]))
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(xdata, ydata, 'b-', label='data')
    ax1.plot(xdata, _func(xdata, *popt), 'r-', label='fit')
    ax1.set_yscale('log')
    ax1.legend()
    fig.suptitle('Resulting fitted profile, fontsize=10')

    outer_cutoff = radius[np.argmin(grad[upper:]) + upper]

    return(popt[1], outer_cutoff)


def detector_normalisation(
        image, det_image, inner_angle, outer_angle=None, flux_expo=None):
    """Using an input detector image and flux exponent (if provided) a detector
    normalisation is carried out on the experimental image.

    Parameters
    ----------
    image : NumPy array
        Experimental image to be normalised.
    det_image : NumPy array
        Detector map as 2D array.
    inner_angle: float
        The experimentally measured inner collection angle of the detector.
    outer_angle: None, otherwise float
        The measured experimental detector collection angle. If left as
        None the outer limit of the detector active region will be used.
    flux_expo: None, otherwise float
        flux_expo is required to carry out flux_weighted detector
        normalisation procedure. For more details see:
        Martinez et al. Ultramicroscopy 2015, 159, 46–58.

    Returns
    -------
    normalised_image : NumPy array
        The experimental image after detector normalisation such that,
        all intensities are a fraction of the incident beam.

    """
    # thresholding the image to get a rough estimate of the active area and
    # the non-active area.
    det_image = det_image.data
    threshold_image = _detector_threshold(det_image)
    # find a value for the average background intensity.
    background = (1 - threshold_image) * det_image
    vacuum_intensity = background[background.nonzero()].mean()
    # create an image where all background is set to zero.
    active_layer = threshold_image * det_image

    # find the centre of the detector.
    # N.B. Currently this method will not work if the detector doesn't
    # fill at least half the image.t

    m = centered_distance_matrix(
            (det_image.shape[0] / 2, det_image.shape[1] / 2), det_image)
    centre_image = np.multiply((m < 512), (1 - threshold_image))
    centre = scipy.ndimage.measurements.center_of_mass(centre_image)

    # Using the centre of the detector and sensitivity profile can be made.
    # The maximum gradient of this profile is the inner collection angle
    # of the detector.
    detector_sensitivity = _radial_profile(det_image, centre[::-1])
    grad = np.gradient(detector_sensitivity)
    ratio = inner_angle / np.argmax(grad)

    # Create a centre matrix around where the detector centre is found to be.
    d = centered_distance_matrix(centre, det_image)

    if outer_angle is not None:
        # This limits the detector average value to only the region being,
        # illuminated by the beam.
        active_layer = np.multiply(active_layer, ((d * ratio) < outer_angle))
        threshold_image = np.multiply(
            threshold_image, ((d * ratio) < outer_angle))

    if flux_expo is None:
        # If no flux exponent is provided the detector sensitivity is simply
        # the average value of the active region.
        detector_intensity = active_layer[active_layer.nonzero()].mean()

    else:
        # Begin flux weighting detector method based on:
        # Martinez et al. Ultramicroscopy 2015, 159, 46–58.

        if flux_expo < 0:
            flux_expo = 0 - flux_expo

        # 1. Create a 2D flux profile from the exponent value given.
        flux = _func(d, 1, flux_expo, 0)
        # 2. Multiply 2D flux by the threshold image so that only angles within
        # active and illuminated area of the detector are considered.
        flux = np.multiply(flux, threshold_image)
        # 3. Normalise the 2D flux so that the mean intensity in the new flux
        # region is 1.
        flux = flux / flux[flux.nonzero()].mean()
        # 4. Multiply this 2D flux by the active layer of the detector.
        new_det = np.multiply(active_layer, flux)

        detector_intensity = new_det[new_det.nonzero()].mean()

    normalised_image = (image.data - vacuum_intensity) / \
        (detector_intensity - vacuum_intensity)

    return image._deepcopy_with_new_data(normalised_image, copy_variance=True)


def get_statistical_quant_criteria(sublattices, max_atom_nums):
    """Plot the criteria of the Gaussian Mixture Model fitting in order to
    determine the number of different atomimc column intensities. It will try
    fitting between 1 and tot_atom_nums number of Gaussians.

    Parameters
    ----------
    sublattice : list
        List of Sublattice objects.
    max_atom_nums : int
        Maximum number of Gaussians to fit, i.e. max number of atoms in one
        column.

    Returns
    -------
    models : list
        List of GaussianMixture models.

    Example
    -------
    >>> import numpy as np
    >>> import atomap.api as am
    >>> s = am.dummy_data.get_atom_counting_signal()
    >>> atom_positions = am.get_atom_positions(s, 8, threshold_rel=0.1)
    >>> sublattice = am.Sublattice(atom_positions, s)
    >>> sublattice.construct_zone_axes()
    >>> sublattice.refine_atom_positions_using_2d_gaussian(sublattice.image)
    >>> models = am.quant.get_statistical_quant_criteria([sublattice], 10)

    """
    # Get array of intensities of Gaussians of each atom
    intensities = []
    for sublattice in sublattices:
        intensities.append([2 * np.pi * atom.amplitude_gaussian * atom.sigma_x
                            * atom.sigma_y for atom in sublattice.atom_list])
    int_array = np.asarray(intensities)
    int_array = int_array.reshape(-1, 1)

    # Fit Gaussian Mixture models with components from 1 to tot_atom_nums
    N = np.arange(1, max_atom_nums)
    models = [None for i in range(len(N))]

    for i in range(len(N)):
        models[i] = mixture.GaussianMixture(N[i], covariance_type='tied').fit(
                int_array)

    # compute the AIC and the BIC
    AIC = [m.aic(int_array) for m in models]
    BIC = [m.bic(int_array) for m in models]

    # plot 2: AIC and BIC
    fig = plt.figure()
    plt.plot(N, AIC, '-k', label='AIC')
    plt.plot(N, BIC, '--k', label='BIC')
    plt.xlabel('Number of components')
    plt.ylabel('Information criterion')
    plt.legend(loc=2)
    fig.show()

    return(models)


def _plot_fitted_hist(intensities, model, rgb, sort_indices, bins=50):
    """Plot the atomic column intensity histogram with the best Gaussian
    mixture model superimposed.

    Parameters
    ----------
    intensities : 1D NumPy Array
        Intensities of 2D Gaussians fitted to each atomic column.
    model : GuassianMixture model object
        The chosen model.
    rgb : list
        List of discrete values from a Matplotlib colormap.
    sort_indices : list
    bins : int

    """
    x = np.linspace(0, intensities.max()*1.2, 1000)
    x = x.reshape(-1, 1)
    logprob = model.score_samples(x)
    responsibilities = model.predict_proba(x)
    pdf = np.exp(logprob)
    pdf_individual = responsibilities * pdf[:, np.newaxis]

    fig = plt.figure()
    plt.hist(intensities, bins, density=True, alpha=0.4)
    plt.plot(x, pdf, '-k')
    for j, i in enumerate(sort_indices.ravel()):
        plt.plot(x, pdf_individual[:, i], color=rgb[0][j])
    plt.xlabel('$x$')
    plt.ylabel('$p(x)$')
    fig.show()


def statistical_quant(image, sublattice, model, num_atoms, plot=True):
    """Use the statistical quantification technique to estimate the number of
    atoms within each atomic column in an ADF-STEM image.

    Reference: Van Aert et al. Phys Rev B 87, (2013).

    Parameters
    ----------
    image : Hyperspy Signal object or array-like
    sublattice : Sublattice object
    model : GaussianMixture model object
    num_atoms : int
        Number of atoms in longest atomic column as determined using the
        plot_statistical_quant_criteria() function.
    plot : bool, default True

    Returns
    -------
    atom_lattice : Atomap Atom_Lattice
        Each sublattice contains columns of the same number of atoms.

    Example
    -------
    >>> import numpy as np
    >>> import atomap.api as am
    >>> s = am.dummy_data.get_atom_counting_signal()
    >>> atom_positions = am.get_atom_positions(s, 8, threshold_rel=0.1)
    >>> sublattice = am.Sublattice(atom_positions, s)
    >>> sublattice.construct_zone_axes()
    >>> sublattice.refine_atom_positions_using_2d_gaussian()
    >>> models = am.quant.get_statistical_quant_criteria([sublattice], 10)
    >>> sub_lattices = am.quant.statistical_quant(s, sublattice,
    ...                                           models[3], 4, plot=False)
    """
    # Get array of intensities of Gaussians of each atom
    intensities = [2*np.pi*atom.amplitude_gaussian*atom.sigma_x*atom.sigma_y
                   for atom in sublattice.atom_list]
    int_array = np.asarray(intensities)
    int_array = int_array.reshape(-1, 1)

    # model = mixture.GaussianMixture(num_atoms,covariance_type='tied').
    # fit(int_array)

    sort_indices = model.means_.argsort(axis=0)

    labels = model.predict(int_array)

    dic = {}
    for i in range(num_atoms):
        dic[int(sort_indices[i])] = i

    sorted_labels = np.copy(labels)
    for k, v in dic.items():
        sorted_labels[labels == k] = v

    from matplotlib import cm
    x = np.linspace(0.0, 1.0, num_atoms)
    rgb = cm.get_cmap('viridis')(x)[np.newaxis, :, :3].tolist()

    sub_lattices = {}
    sublattice_list = []
    atom_positions = sublattice.atom_positions
    for num in sort_indices.ravel():
        sub_lattices[num] = Sublattice(
                atom_positions[np.where(sorted_labels == num)],
                image=np.array(image.data), color=rgb[0][num])

    for i in range(num_atoms):
        sublattice_list.append(sub_lattices[i])

    atom_lattice = Atom_Lattice(image=np.array(image.data), name='quant',
                                sublattice_list=sublattice_list)

    if plot:
        atom_lattice.plot()
        _plot_fitted_hist(int_array, model, rgb, sort_indices)

    return(atom_lattice)
