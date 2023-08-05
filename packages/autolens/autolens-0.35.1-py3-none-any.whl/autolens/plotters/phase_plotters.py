import autofit as af
import autoarray as aa
from autolens.plot import ray_tracing_plots, hyper_plots, fit_imaging_plots, fit_interferometer_plots


def imaging_of_phase(
    imaging,
    mask,
    positions,
    kpc_per_arcsec,
    unit_label,
    plot_as_subplot,
    plot_image,
    plot_noise_map,
    plot_psf,
    plot_signal_to_noise_map,
    plot_absolute_signal_to_noise_map,
    plot_potential_chi_squared_map,
    visualize_path,
    subplot_path,
):

    output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
        path=visualize_path, folder_names=["imaging"]
    )

    if plot_as_subplot:

        aa.plot.imaging.subplot_imaging(
            imaging=imaging,
            mask=mask,
            positions=positions,
            unit_label=unit_label,
            unit_conversion_factor=kpc_per_arcsec,
            output_path=subplot_path,
            format="png",
        )

    aa.plot.imaging.individual(
        imaging=imaging,
        mask=mask,
        positions=positions,
        unit_label=unit_label,
        unit_conversion_factor=kpc_per_arcsec,
        plot_image=plot_image,
        plot_noise_map=plot_noise_map,
        plot_psf=plot_psf,
        plot_signal_to_noise_map=plot_signal_to_noise_map,
        plot_absolute_signal_to_noise_map=plot_absolute_signal_to_noise_map,
        plot_potential_chi_squared_map=plot_potential_chi_squared_map,
        output_path=output_path,
        format="png",
    )


def interferometer_of_phase(
    interferometer,
    unit_label,
    kpc_per_arcsec,
    plot_as_subplot,
    plot_visibilities,
    plot_uv_wavelengths,
    plot_primary_beam,
    visualize_path,
    subplot_path,
):

    output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
        path=visualize_path, folder_names=["interferometer"]
    )

    if plot_as_subplot:

        aa.plot.interferometer.subplot_interferometer(
            interferometer=interferometer,
            unit_conversion_factor=kpc_per_arcsec,
            output_path=subplot_path,
            format="png",
        )

    aa.plot.interferometer.individual(
        interferometer=interferometer,
        plot_visibilities=plot_visibilities,
        plot_u_wavelengths=plot_uv_wavelengths,
        plot_v_wavelengths=plot_uv_wavelengths,
        plot_primary_beam=plot_primary_beam,
        unit_label=unit_label,
        unit_conversion_factor=kpc_per_arcsec,
        output_path=output_path,
        format="png",
    )


def ray_tracing_of_phase(
    tracer,
    grid,
    during_analysis,
    mask,
    include_critical_curves,
    include_caustics,
    positions,
    plot_in_kpc,
    plot_as_subplot,
    plot_all_at_end_png,
    plot_all_at_end_fits,
    plot_image,
    plot_source_plane,
    plot_convergence,
    plot_potential,
    plot_deflections,
    visualize_path,
    subplot_path,
):
    output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
        path=visualize_path, folder_names=["ray_tracing"]
    )

    if plot_as_subplot:

        ray_tracing_plots.subplot_tracer(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include_critical_curves=include_critical_curves,
            include_caustics=include_caustics,
            positions=positions,
            plot_in_kpc=plot_in_kpc,
            output_path=subplot_path,
            format="png",
        )

    ray_tracing_plots.individual(
        tracer=tracer,
        grid=grid,
        mask=mask,
        include_critical_curves=include_critical_curves,
        include_caustics=include_caustics,
        positions=positions,
        plot_profile_image=plot_image,
        plot_source_plane=plot_source_plane,
        plot_convergence=plot_convergence,
        plot_potential=plot_potential,
        plot_deflections=plot_deflections,
        plot_in_kpc=plot_in_kpc,
        output_path=output_path,
        format="png",
    )

    if not during_analysis:

        if plot_all_at_end_png:

            ray_tracing_plots.individual(
                tracer=tracer,
                grid=grid,
                mask=mask,
                include_critical_curves=include_critical_curves,
                include_caustics=include_caustics,
                positions=positions,
                plot_profile_image=True,
                plot_source_plane=True,
                plot_convergence=True,
                plot_potential=True,
                plot_deflections=True,
                plot_in_kpc=plot_in_kpc,
                output_path=output_path,
                format="png",
            )

        if plot_all_at_end_fits:

            fits_path = af.path_util.make_and_return_path_from_path_and_folder_names(
                path=output_path, folder_names=["fits"]
            )

            ray_tracing_plots.individual(
                tracer=tracer,
                grid=grid,
                mask=mask,
                include_critical_curves=include_critical_curves,
                include_caustics=include_caustics,
                positions=positions,
                plot_profile_image=True,
                plot_source_plane=True,
                plot_convergence=True,
                plot_potential=True,
                plot_deflections=True,
                output_path=fits_path,
                output_format="fits",
            )


def imaging_fit_of_phase(
    fit,
    during_analysis,
    plot_in_kpc,
    mask,
    positions,
    include_critical_curves,
    include_caustics,
    include_image_plane_pix,
    plot_all_at_end_png,
    plot_all_at_end_fits,
    plot_fit_as_subplot,
    plot_fit_subplots_of_plane_fits,
    plot_inversion_as_subplot,
    plot_image,
    plot_noise_map,
    plot_signal_to_noise_map,
    plot_model_image,
    plot_residual_map,
    plot_normalized_residual_map,
    plot_chi_squared_map,
    plot_inversion_reconstruction,
    plot_inversion_errors,
    plot_inversion_residual_map,
    plot_inversion_normalized_residual_map,
    plot_inversion_chi_squared_map,
    plot_inversion_regularization_weights,
    plot_inversion_interpolated_reconstruction,
    plot_inversion_interpolated_errors,
    plot_subtracted_images_of_planes,
    plot_model_images_of_planes,
    plot_plane_images_of_planes,
    visualize_path,
    subplot_path,
):

    output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
        path=visualize_path, folder_names=["fit"]
    )

    if plot_fit_as_subplot:

        fit_imaging_plots.subplot_fit_imaging(
            fit=fit,
            mask=mask,
            positions=positions,
            include_critical_curves=include_critical_curves,
            include_caustics=include_caustics,
            include_image_plane_pix=include_image_plane_pix,
            plot_in_kpc=plot_in_kpc,
            output_path=subplot_path,
            format="png",
        )

    if plot_fit_subplots_of_plane_fits:

        fit_imaging_plots.subplot_of_planes(
            fit=fit,
            mask=mask,
            positions=positions,
            include_critical_curves=include_critical_curves,
            include_caustics=include_caustics,
            include_image_plane_pix=include_image_plane_pix,
            plot_in_kpc=plot_in_kpc,
            output_path=subplot_path,
            format="png",
        )

    if plot_inversion_as_subplot and fit.inversion is not None:

        aa.plot.inversion.subplot_inversion(
            inversion=fit.inversion,
            mask=fit.mask,
            output_path=subplot_path,
            format="png",
        )

    fit_imaging_plots.individuals(
        fit=fit,
        mask=mask,
        positions=positions,
        include_critical_curves=include_critical_curves,
        include_caustics=include_caustics,
        include_image_plane_pix=include_image_plane_pix,
        plot_image=plot_image,
        plot_noise_map=plot_noise_map,
        plot_signal_to_noise_map=plot_signal_to_noise_map,
        plot_model_image=plot_model_image,
        plot_residual_map=plot_residual_map,
        plot_chi_squared_map=plot_chi_squared_map,
        plot_normalized_residual_map=plot_normalized_residual_map,
        plot_reconstruction=plot_inversion_reconstruction,
        plot_errors=plot_inversion_errors,
        plot_residual_map=plot_inversion_residual_map,
        plot_normalized_residual_map=plot_inversion_normalized_residual_map,
        plot_chi_squared_map=plot_inversion_chi_squared_map,
        plot_regularization_weight_map=plot_inversion_regularization_weights,
        plot_interpolated_reconstruction=plot_inversion_interpolated_reconstruction,
        plot_interpolated_errors=plot_inversion_interpolated_errors,
        plot_subtracted_images_of_planes=plot_subtracted_images_of_planes,
        plot_model_images_of_planes=plot_model_images_of_planes,
        plot_plane_images_of_planes=plot_plane_images_of_planes,
        plot_in_kpc=plot_in_kpc,
        output_path=output_path,
        format="png",
    )

    if not during_analysis:

        if plot_all_at_end_png:

            fit_imaging_plots.individuals(
                fit=fit,
                mask=mask,
                positions=positions,
                include_critical_curves=include_critical_curves,
                include_caustics=include_caustics,
                include_image_plane_pix=include_image_plane_pix,
                plot_image=True,
                plot_noise_map=True,
                plot_signal_to_noise_map=True,
                plot_model_image=True,
                plot_residual_map=True,
                plot_normalized_residual_map=True,
                plot_chi_squared_map=True,
                plot_reconstruction=True,
                plot_errors=True,
                plot_residual_map=True,
                plot_normalized_residual_map=True,
                plot_chi_squared_map=True,
                plot_regularization_weight_map=True,
                plot_interpolated_reconstruction=True,
                plot_interpolated_errors=True,
                plot_subtracted_images_of_planes=True,
                plot_model_images_of_planes=True,
                plot_plane_images_of_planes=True,
                plot_in_kpc=plot_in_kpc,
                output_path=output_path,
                format="png",
            )

        if plot_all_at_end_fits:

            fits_path = af.path_util.make_and_return_path_from_path_and_folder_names(
                path=output_path, folder_names=["fits"]
            )

            fit_imaging_plots.individuals(
                fit=fit,
                mask=mask,
                positions=positions,
                include_critical_curves=include_critical_curves,
                include_caustics=include_caustics,
                include_image_plane_pix=include_image_plane_pix,
                plot_image=True,
                plot_noise_map=True,
                plot_signal_to_noise_map=True,
                plot_model_image=True,
                plot_residual_map=True,
                plot_normalized_residual_map=True,
                plot_chi_squared_map=True,
                plot_reconstruction=True,
                plot_errors=True,
                plot_residual_map=True,
                plot_normalized_residual_map=True,
                plot_chi_squared_map=True,
                plot_regularization_weight_map=True,
                plot_interpolated_reconstruction=True,
                plot_interpolated_errors=True,
                plot_subtracted_images_of_planes=True,
                plot_model_images_of_planes=True,
                plot_plane_images_of_planes=True,
                output_path=fits_path,
                output_format="fits",
            )


def interferometer_fit_of_phase(
    fit,
    during_analysis,
    positions,
    mask,
    include_critical_curves,
    include_caustics,
    include_image_plane_pix,
    plot_in_kpc,
    plot_all_at_end_png,
    plot_all_at_end_fits,
    plot_fit_as_subplot,
    plot_inversion_as_subplot,
    plot_visibilities,
    plot_noise_map,
    plot_signal_to_noise_map,
    plot_model_visibilities,
    plot_residual_map,
    plot_normalized_residual_map,
    plot_chi_squared_map,
    plot_inversion_reconstruction,
    plot_inversion_errors,
    plot_inversion_residual_map,
    plot_inversion_normalized_residual_map,
    plot_inversion_chi_squared_map,
    plot_inversion_regularization_weights,
    plot_inversion_interpolated_reconstruction,
    plot_inversion_interpolated_errors,
    visualize_path,
    subplot_path,
):

    output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
        path=visualize_path, folder_names=["fit"]
    )

    if plot_fit_as_subplot:

        fit_interferometer_plots.subplot_fit_interferometer(
            fit=fit,
            plot_in_kpc=plot_in_kpc,
            output_path=subplot_path,
            format="png",
        )

        fit_interferometer_plots.subplot_fit_real_space(
            fit=fit,
            mask=mask,
            include_critical_curves=include_critical_curves,
            include_caustics=include_caustics,
            positions=positions,
            include_image_plane_pix=include_image_plane_pix,
            plot_in_kpc=plot_in_kpc,
            output_path=subplot_path,
            format="png",
        )

    # if plot_inversion_as_subplot and fit.inversion is not None:
    #
    #     aa.plot.inversion.subplot(
    #         inversion=fit.inversion,
    #         mask=fit.masked_interferometer.real_space_mask,
    #         positions=positions,
    #         output_path=subplot_path,
    #         format="png",
    #     )

    fit_interferometer_plots.individuals(
        fit=fit,
        plot_visibilities=plot_visibilities,
        plot_noise_map=plot_noise_map,
        plot_signal_to_noise_map=plot_signal_to_noise_map,
        plot_model_visibilities=plot_model_visibilities,
        plot_residual_map=plot_residual_map,
        plot_chi_squared_map=plot_chi_squared_map,
        plot_normalized_residual_map=plot_normalized_residual_map,
        plot_reconstruction=plot_inversion_reconstruction,
        plot_errors=plot_inversion_errors,
        # plot_inversion_residual_map=plot_inversion_residual_map,
        # plot_inversion_normalized_residual_map=plot_inversion_normalized_residual_map,
        # plot_inversion_chi_squared_map=plot_inversion_chi_squared_map,
        plot_regularization_weight_map=plot_inversion_regularization_weights,
        plot_interpolated_reconstruction=plot_inversion_interpolated_reconstruction,
        plot_interpolated_errors=plot_inversion_interpolated_errors,
        plot_in_kpc=plot_in_kpc,
        output_path=output_path,
        format="png",
    )

    if not during_analysis:

        if plot_all_at_end_png:

            fit_interferometer_plots.individuals(
                fit=fit,
                plot_visibilities=True,
                plot_noise_map=True,
                plot_signal_to_noise_map=True,
                plot_model_visibilities=True,
                plot_residual_map=True,
                plot_normalized_residual_map=True,
                plot_chi_squared_map=True,
                plot_reconstruction=True,
                plot_errors=True,
                # plot_inversion_residual_map=True,
                # plot_inversion_normalized_residual_map=True,
                # plot_inversion_chi_squared_map=True,
                plot_regularization_weight_map=True,
                plot_interpolated_reconstruction=True,
                plot_interpolated_errors=True,
                plot_in_kpc=plot_in_kpc,
                output_path=output_path,
                format="png",
            )

        if plot_all_at_end_fits:

            fits_path = af.path_util.make_and_return_path_from_path_and_folder_names(
                path=output_path, folder_names=["fits"]
            )

            fit_interferometer_plots.individuals(
                fit=fit,
                plot_visibilities=True,
                plot_noise_map=True,
                plot_signal_to_noise_map=True,
                plot_model_visibilities=True,
                plot_residual_map=True,
                plot_normalized_residual_map=True,
                plot_chi_squared_map=True,
                plot_reconstruction=True,
                plot_errors=True,
                # plot_inversion_residual_map=True,
                # plot_inversion_normalized_residual_map=True,
                # plot_inversion_chi_squared_map=True,
                plot_regularization_weight_map=True,
                plot_interpolated_reconstruction=True,
                plot_interpolated_errors=True,
                output_path=fits_path,
                output_format="fits",
            )


def plot_hyper_images_for_phase(
    hyper_model_image,
    hyper_galaxy_image_path_dict,
    mask,
    kpc_per_arcsec,
    unit_label,
    plot_hyper_model_image,
    plot_hyper_galaxy_images,
    visualize_path,
):

    output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
        path=visualize_path, folder_names=["hyper_galaxies"]
    )

    if plot_hyper_model_image:

        hyper_plots.hyper_model_image(
            hyper_model_image=hyper_model_image,
            mask=mask,
            kpc_per_arcsec=kpc_per_arcsec,
            unit_label=unit_label,
            output_path=output_path,
            format="png",
        )

    if plot_hyper_galaxy_images:

        hyper_plots.subplot_hyper_galaxy_images(
            hyper_galaxy_image_path_dict=hyper_galaxy_image_path_dict,
            mask=mask,
            kpc_per_arcsec=kpc_per_arcsec,
            unit_label=unit_label,
            output_path=output_path,
            format="png",
        )
