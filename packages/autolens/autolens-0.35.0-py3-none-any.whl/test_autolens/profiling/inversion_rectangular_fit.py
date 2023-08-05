import time

from autolens.array import grids, mask as msk
from autolens.model.galaxy import galaxy as g
from autolens.model.profiles import mass_profiles as mp
from autolens.lens import lens_data as ld
from autolens.lens import ray_tracing
from autolens.lens.lens_fit import lens_imaging_fit
from autolens.model.inversion import pixelizations as pix
from autolens.model.inversion import regularization as reg
from autolens.model.inversion.util import inversion_util
from autolens.model.inversion.util import regularization_util

from test.simulation import simulation_util

import numpy as np

repeats = 10

print("Number of repeats = " + str(repeats))
print()

sub_size = 4
radius = 3.6
psf_shape = (11, 11)
pixelization_shape = (20, 20)

print("sub grid size = " + str(sub_size))
print("circular mask radius = " + str(radius) + "\n")
print("psf shape = " + str(psf_shape) + "\n")
print("pixelization shape = " + str(pixelization_shape) + "\n")

lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.0, 0.0), einstein_radius=1.6, axis_ratio=0.7, phi=45.0
    ),
)

pixelization = al.pix.Rectangular(shape=pixelization_shape)

source_galaxy = al.Galaxy(
    redshift=1.0,
    pixelization=pixelization,
    regularization=al.reg.Constant(coefficient=1.0),
)

for data_resolution in ["lsst", "euclid", "hst", "hst_up"]:  # , 'AO']:

    imaging_data = simulation_util.load_test_imaging_data(
        data_type="lens_mass__source_smooth",
        data_resolution=data_resolution,
        psf_shape=psf_shape,
    )
    mask = al.Mask.circular(
        shape=imaging_data.shape,
        pixel_scales=imaging_data.pixel_scale,
        radius=radius,
    )
    lens_data = al.LensData(imaging_data=imaging_data, mask=mask, sub_size=sub_size)

    print(
        "VoronoiMagnification Inversion fit run times for image type "
        + data_resolution
        + "\n"
    )
    print("Number of points = " + str(lens_data.grid.shape[0]) + "\n")

    start_overall = time.time()

    start = time.time()
    for i in range(repeats):
        tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])
        traced_source_plane_grid = tracer.traced_grids_of_planes_from_grid(
            grid=lens_data.grid
        )[-1]
    diff = time.time() - start
    print("Time to Setup Tracer = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        traced_source_plane_pixelization_grid = tracer.traced_pixelization_grids_of_planes_from_grid(
            grid=lens_data.grid
        )[
            -1
        ]

    diff = time.time() - start
    print("Time to Setup Pixelization Grid = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        relocated_grid = lens_data.grid.relocated_grid_from_grid(
            grid=traced_source_plane_grid
        )
    diff = time.time() - start
    print("Time to perform border relocation = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        rectangular_mapper = pixelization.mapper_from_grid_and_pixelization_grid(
            grid=traced_source_plane_grid,
            pixelization_grid=None,
            inversion_uses_border=True,
        )
    diff = time.time() - start
    print("Time to create mapper = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        mapping_matrix = rectangular_mapper.mapping_matrix
    diff = time.time() - start
    print("Time to compute mapping matrix = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        blurred_mapping_matrix = lens_data.convolver.convolve_mapping_matrix(
            mapping_matrix=mapping_matrix
        )
    diff = time.time() - start
    print("Time to compute blurred mapping matrix = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        data_vector = inversion_util.data_vector_from_blurred_mapping_matrix_and_data(
            blurred_mapping_matrix=blurred_mapping_matrix,
            image_1d=lens_data.image_1d,
            noise_map_1d=lens_data.noise_map_1d,
        )
    diff = time.time() - start
    print("Time to compute data vector = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        curvature_matrix = inversion_util.curvature_matrix_from_blurred_mapping_matrix(
            blurred_mapping_matrix=blurred_mapping_matrix,
            noise_map_1d=lens_data.noise_map_1d,
        )
    diff = time.time() - start
    print("Time to compute curvature matrix = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        regularization_matrix = regularization_util.constant_regularization_matrix_from_pixel_neighbors(
            coefficient=1.0,
            pixel_neighbors=rectangular_mapper.pixel_neighbors,
            pixel_neighbors_size=pixel_neighbors_size,
        )
    diff = time.time() - start
    print("Time to compute reguarization matrix = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        curvature_reg_matrix = np.add(curvature_matrix, regularization_matrix)
    diff = time.time() - start
    print("Time to compute curvature reguarization Matrix = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        solution_vector = np.linalg.solve(curvature_reg_matrix, data_vector)
    diff = time.time() - start
    print("Time to compute solution vector = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        inversion_util.reconstructed_data_vector_from_blurred_mapping_matrix_and_solution_vector(
            blurred_mapping_matrix=blurred_mapping_matrix,
            solution_vector=solution_vector,
        )
    diff = time.time() - start
    print("Time to compute reconstructed data vector = {}".format(diff / repeats))

    start = time.time()
    for i in range(repeats):
        lens_imaging_fit.LensInversionFit(lens_data=lens_data, tracer=tracer)
    diff = time.time() - start
    print("Time to perform complete fit = {}".format(diff / repeats))

    print()
