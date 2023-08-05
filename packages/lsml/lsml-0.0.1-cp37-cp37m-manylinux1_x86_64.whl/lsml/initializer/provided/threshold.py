from scipy.ndimage import gaussian_filter
from skimage.filters.thresholding import threshold_otsu

from lsml.initializer.initializer_base import (
    InitializerBase)


class ThresholdInitializer(InitializerBase):
    """ Computes the Otsu threshold on the a Gaussian-smoothed image, and
    creates the boolean initialization using that threshold
    """

    def __init__(self, sigma):
        """ Initialize a threshold initializer instance

        Parameters
        ----------
        sigma: float
            The sigma value used for Gaussian smoothing. A value of zero
            implies no Gaussian filtering will be used.

        """
        if sigma < 0:
            raise ValueError("sigma ({}) was negative".format(sigma))
        self.sigma = sigma

    def initialize(self, img, dx, seed):

        if self.sigma == 0:
            blur = img.copy()
        else:
            blur = gaussian_filter(img, self.sigma)

        threshold_value = threshold_otsu(blur)

        init_mask = blur >= threshold_value

        return init_mask
