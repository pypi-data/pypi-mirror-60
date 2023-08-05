import numpy as np
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import slugify
import os

register_matplotlib_converters()

def plot_positions_multiple_devices(
    df,
    room_corners,
    **kwargs
):
    for (device_id, device_serial_number, entity_type, person_short_name, material_name), group_df in df.fillna('NA').groupby([
        'device_id',
        'device_serial_number',
        'entity_type',
        'person_short_name',
        'material_name'
    ]):
        entity_name = material_name
        if entity_type == 'Person':
            entity_name = person_short_name
        plot_positions(
            df=group_df,
            entity_name=entity_name,
            room_corners=room_corners,
            device_serial_number=device_serial_number,
            **kwargs
        )

def plot_positions_topdown_multiple_devices(
    df,
    room_corners,
    **kwargs
):
    for (device_id, device_serial_number, entity_type, person_short_name, material_name), group_df in df.fillna('NA').groupby([
        'device_id',
        'device_serial_number',
        'entity_type',
        'person_short_name',
        'material_name'
    ]):
        entity_name = material_name
        if entity_type == 'Person':
            entity_name = person_short_name
        plot_positions_topdown(
            df=group_df,
            entity_name=entity_name,
            room_corners=room_corners,
            device_serial_number=device_serial_number,
            **kwargs
        )

def plot_positions(
    df,
    entity_name,
    device_serial_number,
    room_corners,
    marker = '.',
    alpha = 1.0,
    colormap_name = 'hot_r',
    quality_lims = [0, 10000],
    figure_size_inches = [10.5, 8],
    plot_show=True,
    plot_save=False,
    output_directory = '.',
    filename_extension = 'png',
    y_axis_labels = ['$x$ position (meters)', '$y$ position (meters)'],
    color_axis_label = 'Quality',
    position_column_names = ['x_meters', 'y_meters'],
    quality_column_name = 'quality'
):
    time_min = df.index.min()
    time_max = df.index.max()
    fig, axes = plt.subplots(2, 1, sharex=True)
    plots = [None, None]
    for axis_index in range(2):
        plots[axis_index] = axes[axis_index].scatter(
            df.index.values,
            df[position_column_names[axis_index]],
            marker=marker,
            alpha=alpha,
            c=df[quality_column_name],
            cmap=plt.get_cmap(colormap_name),
            vmin=quality_lims[0],
            vmax=quality_lims[1]
        )
        axes[axis_index].set_ylim(room_corners[0][axis_index], room_corners[1][axis_index])
        axes[axis_index].set_ylabel(y_axis_labels[axis_index])
    axes[1].set_xlim(time_min, time_max)
    axes[1].set_xlabel('Time (UTC)')
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.colorbar(plots[1], ax=axes).set_label(color_axis_label)
    fig.suptitle('{} ({})'.format(
        entity_name,
        device_serial_number
    ))
    fig.set_size_inches(figure_size_inches[0],figure_size_inches[1])
    if plot_show:
        plt.show()
    if plot_save:
        filename = '_'.join([
            'cuwb_positions',
            slugify.slugify(device_serial_number),
            time_min.strftime('%Y%m%d-%H%M%S'),
            time_max.strftime('%Y%m%d-%H%M%S')
        ])
        filename += '.' + filename_extension
        path = os.path.join(
            output_directory,
            filename
        )
        fig.savefig(path)

def plot_positions_topdown(
    df,
    entity_name,
    device_serial_number,
    room_corners,
    marker = '.',
    alpha = 1.0,
    color_axis='quality',
    colormap_name = 'hot_r',
    quality_lims = [0, 10000],
    figure_size_inches = [10.5, 8],
    plot_show=True,
    plot_save=False,
    output_directory = '.',
    filename_extension = 'png',
    axis_labels = ['$x$ position (meters)', '$y$ position (meters)'],
    color_axis_label = 'Quality',
    position_column_names = ['x_meters', 'y_meters'],
    quality_column_name = 'quality'
):
    time_min = df.index.min()
    time_max = df.index.max()
    if color_axis == 'quality':
        color_data = df[quality_column_name]
        vmin = quality_lims[0]
        vmax = quality_lims[1]
    elif color_axis == 'time':
        color_data = df.index
        vmin = time_min
        vmax = time_max
    else:
        raise ValueError('Color axis specification not recognized')
    fig, axes = plt.subplots(1, 1)
    plot = axes.scatter(
        df[position_column_names[0]],
        df[position_column_names[1]],
        marker=marker,
        alpha=alpha,
        c=color_data,
        cmap=plt.get_cmap(colormap_name)
        # vmin=vmin,
        # vmax=vmax
    )
    axes.set_xlim(room_corners[0][0], room_corners[1][0])
    axes.set_ylim(room_corners[0][1], room_corners[1][1])
    axes.set_aspect('equal')
    axes.set_xlabel(axis_labels[0])
    axes.set_ylabel(axis_labels[1])
    cbar = fig.colorbar(plot, ax=axes)
    cbar.set_label(color_axis_label)
    fig.suptitle('{} ({})'.format(
        entity_name,
        device_serial_number
    ))
    fig.set_size_inches(figure_size_inches[0],figure_size_inches[1])
    if plot_show:
        plt.show()
    if plot_save:
        filename = '_'.join([
            'cuwb_positions_topdown',
            slugify.slugify(device_serial_number),
            time_min.strftime('%Y%m%d-%H%M%S'),
            time_max.strftime('%Y%m%d-%H%M%S')
        ])
        filename += '.' + filename_extension
        path = os.path.join(
            output_directory,
            filename
        )
        fig.savefig(path)
