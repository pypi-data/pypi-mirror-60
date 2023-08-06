from functools import partial
from typing import Any, List, Mapping, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.ndimage import label
from skimage.feature import peak_local_max
from skimage.measure import regionprops
from sympy import Line, Point
from tqdm import tqdm

from starfish.core.config import StarfishConfig
from starfish.core.imagestack.imagestack import ImageStack
from starfish.core.spots.FindSpots import spot_finding_utils
from starfish.core.types import (
    Axes,
    Features,
    Number,
    PerImageSliceSpotResults,
    SpotAttributes,
    SpotFindingResults
)
from ._base import FindSpotsAlgorithm


class LocalMaxPeakFinder(FindSpotsAlgorithm):
    """
    2-dimensional local-max peak finder that wraps skimage.feature.peak_local_max

    Parameters
    ----------
    min_distance : int
        Minimum number of pixels separating peaks in a region of 2 * min_distance + 1
        (i.e. peaks are separated by at least min_distance). To find the maximum number of
        peaks, use min_distance=1.
    stringency : int
    min_obj_area : int
    max_obj_area : int
    threshold : Optional[Number]
    measurement_type : str, {'max', 'mean'}
        default 'max' calculates the maximum intensity inside the object
    min_num_spots_detected : int
        When fewer than this number of spots are detected, spot searching for higher threshold
        values. (default = 3)
    is_volume : bool
        Not supported. For 3d peak detection please use TrackpyLocalMaxPeakFinder.
        (default=False)
    verbose : bool
        If True, report the percentage completed during processing
        (default = False)

    Notes
    -----
    http://scikit-image.org/docs/dev/api/skimage.feature.html#skimage.feature.peak_local_max
    """

    def __init__(
        self, min_distance: int, stringency: int, min_obj_area: int, max_obj_area: int,
        threshold: Optional[Number]=None, measurement_type: str='max',
        min_num_spots_detected: int=3, is_volume: bool=False, verbose: bool=True
    ) -> None:

        self.min_distance = min_distance
        self.stringency = stringency
        self.min_obj_area = min_obj_area
        self.max_obj_area = max_obj_area
        self.threshold = threshold
        self.min_num_spots_detected = min_num_spots_detected

        self.measurement_function = self._get_measurement_function(measurement_type)

        self.is_volume = is_volume
        self.verbose = verbose

    def _compute_num_spots_per_threshold(self, img: np.ndarray) -> Tuple[np.ndarray, List[int]]:
        """Computes the number of detected spots for each threshold

        Parameters
        ----------
        img : np.ndarray
            The image in which to count spots

        Returns
        -------
        np.ndarray :
            thresholds
        List[int] :
            spot counts
        """

        # thresholds to search over
        thresholds = np.linspace(img.min(), img.max(), num=100)

        # number of spots detected at each threshold
        spot_counts = []

        # where we stop our threshold search
        stop_threshold = None

        if self.verbose and StarfishConfig().verbose:
            threshold_iter = tqdm(thresholds)
            print('Determining optimal threshold ...')
        else:
            threshold_iter = thresholds

        for stop_index, threshold in enumerate(threshold_iter):
            spots = peak_local_max(
                img,
                min_distance=self.min_distance,
                threshold_abs=threshold,
                exclude_border=False,
                indices=True,
                num_peaks=np.inf,
                footprint=None,
                labels=None
            )

            # stop spot finding when the number of detected spots falls below min_num_spots_detected
            if len(spots) <= self.min_num_spots_detected:
                stop_threshold = threshold
                if self.verbose:
                    print(f'Stopping early at threshold={threshold}. Number of spots fell below: '
                          f'{self.min_num_spots_detected}')
                break
            else:
                spot_counts.append(len(spots))

        if stop_threshold is None:
            stop_threshold = thresholds.max()

        if len(thresholds > 1):
            thresholds = thresholds[:stop_index]
            spot_counts = spot_counts[:stop_index]

        return thresholds, spot_counts

    def _select_optimal_threshold(self, thresholds: np.ndarray, spot_counts: List[int]) -> float:
        # calculate the gradient of the number of spots
        grad = np.gradient(spot_counts)
        optimal_threshold_index = np.argmin(grad)

        # only consider thresholds > than optimal threshold
        thresholds = thresholds[optimal_threshold_index:]
        grad = grad[optimal_threshold_index:]

        # if all else fails, return 0.
        selected_thr = 0

        if len(thresholds) > 1:

            distances = []

            # create a line whose end points are the threshold and and corresponding gradient value
            # for spot_counts corresponding to the threshold
            start_point = Point(thresholds[0], grad[0])
            end_point = Point(thresholds[-1], grad[-1])
            line = Line(start_point, end_point)

            # calculate the distance between all points and the line
            for k in range(len(thresholds)):
                p = Point(thresholds[k], grad[k])
                dst = line.distance(p)
                distances.append(dst.evalf())

            # remove the end points
            thresholds = thresholds[1:-1]
            distances = distances[1:-1]

            # select the threshold that has the maximum distance from the line
            # if stringency is passed, select a threshold that is n steps higher, where n is the
            # value of stringency
            if distances:
                thr_idx = np.argmax(np.array(distances))

                if thr_idx + self.stringency < len(thresholds):
                    selected_thr = thresholds[thr_idx + self.stringency]
                else:
                    selected_thr = thresholds[thr_idx]

        return selected_thr

    def _compute_threshold(
            self, img: np.ndarray) -> Tuple[float, Optional[np.ndarray], Optional[List[int]]]:
        """Finds spots on a number of thresholds then selects and returns the optimal threshold

        Parameters
        ----------
        img: np.ndarray
            data array in which spots should be detected and over which to compute different
            intensity thresholds

        Returns
        -------
        np.ndarray :
            The intensity threshold
        """
        img = np.asarray(img)
        thresholds, spot_counts = self._compute_num_spots_per_threshold(img)
        if len(spot_counts) == 0:
            # this only happens when we never find more spots than `self.min_num_spots_detected`
            return img.min(), None, None
        return self._select_optimal_threshold(thresholds, spot_counts), thresholds, spot_counts

    def image_to_spots(
            self, data_image: np.ndarray
    ) -> PerImageSliceSpotResults:
        """measure attributes of spots detected by binarizing the image using the selected threshold

        Parameters
        ----------
        data_image : np.ndarray
            image containing spots to be detected

        Returns
        -------
        PerImageSpotResults :
            includes a SpotAttributes DataFrame of metadata containing the coordinates, intensity
            and radius of each spot, as well as any extra information collected during spot finding.
        """

        optimal_threshold, thresholds, spot_counts = self._compute_threshold(data_image)

        data_image = np.asarray(data_image)

        # identify each spot's size by binarizing and calculating regionprops
        masked_image = data_image[:, :] > optimal_threshold
        labels = label(masked_image)[0]
        spot_props = regionprops(np.squeeze(labels))

        # mask spots whose areas are too small or too large
        for spot_prop in spot_props:
            if spot_prop.area < self.min_obj_area or spot_prop.area > self.max_obj_area:
                masked_image[0, spot_prop.coords[:, 0], spot_prop.coords[:, 1]] = 0

        # store re-calculated regionprops and labels based on the area-masked image
        labels = label(masked_image)[0]

        if self.verbose:
            print('computing final spots ...')

        spot_coords = peak_local_max(
            data_image,
            min_distance=self.min_distance,
            threshold_abs=optimal_threshold,
            exclude_border=False,
            indices=True,
            num_peaks=np.inf,
            footprint=None,
            labels=labels
        )

        res = {Axes.X.value: spot_coords[:, 2],
               Axes.Y.value: spot_coords[:, 1],
               Axes.ZPLANE.value: spot_coords[:, 0],
               Features.SPOT_RADIUS: 1,
               Features.SPOT_ID: np.arange(spot_coords.shape[0]),
               Features.INTENSITY: data_image[spot_coords[:, 0],
                                              spot_coords[:, 1],
                                              spot_coords[:, 2]],
               }
        extras: Mapping[str, Any] = {
            "threshold": optimal_threshold,
            "thresholds": thresholds,
            "spot_counts": spot_counts
        }

        return PerImageSliceSpotResults(spot_attrs=SpotAttributes(pd.DataFrame(res)), extras=extras)

    def run(
            self,
            image_stack: ImageStack,
            reference_image: Optional[ImageStack] = None,
            n_processes: Optional[int] = None,
            *args,
            **kwargs
    ) -> SpotFindingResults:
        """
        Find spots in the given ImageStack using a gaussian blob finding algorithm.
        If a reference image is provided the spots will be detected there then measured
        across all rounds and channels in the corresponding ImageStack. If a reference_image
        is not provided spots will be detected _independently_ in each channel. This assumes
        a non-multiplex imaging experiment, as only one (ch, round) will be measured for each spot.

        Parameters
        ----------
        image_stack : ImageStack
            ImageStack where we find the spots in.
        reference_image : Optional[ImageStack]
            (Optional) a reference image. If provided, spots will be found in this image, and then
            the locations that correspond to these spots will be measured across each channel.
        n_processes : Optional[int] = None,
            Number of processes to devote to spot finding.
        """
        spot_finding_method = partial(self.image_to_spots, *args, **kwargs)
        if reference_image:
            data_image = reference_image._squeezed_numpy(*{Axes.ROUND, Axes.CH})
            reference_spots = spot_finding_method(data_image)
            results = spot_finding_utils.measure_intensities_at_spot_locations_across_imagestack(
                data_image=image_stack,
                reference_spots=reference_spots,
                measurement_function=self.measurement_function)
        else:
            spot_attributes_list = image_stack.transform(
                func=spot_finding_method,
                group_by={Axes.ROUND, Axes.CH},
                n_processes=n_processes
            )
            results = SpotFindingResults(imagestack_coords=image_stack.xarray.coords,
                                         log=image_stack.log,
                                         spot_attributes_list=spot_attributes_list)
        return results
