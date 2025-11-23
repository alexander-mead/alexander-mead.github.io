import healpy as hp
import numpy as np
import plotly.graph_objects as go
from fastapi import FastAPI
from matplotlib.colors import ListedColormap
from pydantic import BaseModel
from scipy.interpolate import griddata
from world_generator import SphericalWorld, terrain_dictionary

# Create the FastAPI app instance
app = FastAPI()

NSIDE = 128
RADIUS = 100  # km
PIXELS = 12 * NSIDE**2


@app.get("/ping")
async def ping() -> dict[str, str]:
    """
    Endpoint to check if the server is live
    """
    return {"message": "pong"}


@app.post("/worlds")
async def worlds() -> dict[str, str]:
    """
    Endpoint to generate a new world
    """

    # Altitude parameters
    altitude_mean = 0.0  # Mean height above sea level [m]
    altitude_large_power_sigma = (
        700.0  # Amplitude of large-scale altitude variation [m]
    )
    altitude_small_power_sigma = (
        300.0  # Amplitude of small-scale altitude variation [m]
    )
    altitude_large_power_smooth = (
        1.0 * RADIUS
    )  # Maximum-ish size of features in altitude [km]
    altitude_small_power_smooth = 0.15 * RADIUS  # Small-scale features [km]
    altitude_power_index = -1.0  # Altitude power-law index
    altitude_nonlinear_power = 2.0  # Power for non-linear field sharpening
    altitude_nonlinear_pivot = 1000.0  # Pivot altitude for non-linear sharpening [m]
    altitude_erosion_parameter = 1.5  # Erosion parameter [m * km]
    altitude_erosion_iterations = 10  # Number of erosion iterations

    # Rainfall parameters
    rainfall_mean = 1000.0  # Mean rainfall [mm/year]
    rainfall_quadrupole_sigma = 500.0  # Amplitude of rainfall variation [mm/year]
    rainfall_power_sigma = 1000.0  # Standard deviation of rainfall [mm/year]
    rainfall_power_smooth = (
        1.0 * RADIUS
    )  # Maximum-ish size of features in rainfall [km]
    rainfall_power_index = -0.5  # Rainfall power-law index

    # Temperature parameters
    temperature_mean = 15.0  # Mean temperature [deg C]
    temperature_quadrupole_sigma = 15.0  # Amplitude of temperature variation [deg C]
    temperature_power_sigma = 1.0  # Standard deviation of temperature [deg C]
    temperature_power_smooth = (
        0.1 * RADIUS
    )  # Maximum-ish size of features in temperature [km]
    temperature_power_index = 1.0  # Temperature power-law index
    temperature_lapse_rate = 0.01  # Temperature lapse rate [deg C/m]

    world = SphericalWorld(
        pixels=PIXELS,
        radius=RADIUS,
        mean_altitude=altitude_mean,
        mean_rainfall=rainfall_mean,
        mean_temperature=temperature_mean,
    )

    # Generate altitude
    world.add_field_power(  # Adds continents/oceans-scale features
        "altitude",
        altitude_large_power_sigma,
        altitude_power_index,
        altitude_large_power_smooth,
    )
    world.add_field_power(  # Adds mountain/lake-scale feature
        "altitude",
        altitude_small_power_sigma,
        altitude_power_index,
        altitude_small_power_smooth,
    )
    world.sharpen_field("altitude", altitude_nonlinear_power, altitude_nonlinear_pivot)
    world.erode_altitude(altitude_erosion_parameter, altitude_erosion_iterations)

    # Generate rainfall
    world.add_field_quadrupole("rainfall", rainfall_quadrupole_sigma, subtract=True)
    world.add_field_power(
        "rainfall", rainfall_power_sigma, rainfall_power_index, rainfall_power_smooth
    )
    world.remove_negative_field_values("rainfall")

    # Generate temperature
    world.add_field_quadrupole("temperature", temperature_quadrupole_sigma)
    world.add_field_power(
        "temperature",
        temperature_power_sigma,
        temperature_power_index,
        temperature_power_smooth,
    )
    world.add_temperature_altitude_lapse(temperature_lapse_rate)

    # Generate terrain
    world.generate_terrain()

    # Fill colormap for terrain types
    colors = []
    for color in terrain_dictionary.values():
        colors.append(color)
    terrain_colors = ListedColormap(colors)

    # Build a regular lon-lat grid
    lon, lat = hp.pix2ang(NSIDE, np.arange(PIXELS), lonlat=True)
    nlon, nlat = 360, 180
    res_fac = 3
    lon_grid = np.linspace(0, 360, res_fac * nlon + 1)
    lat_grid = np.linspace(-90, 90, res_fac * nlat + 1)
    lon_grid, lat_grid = np.meshgrid(lon_grid, lat_grid)

    # Interpolate HEALPix -> grid
    alt_grid = griddata(
        (lon, lat), world.altitude, (lon_grid, lat_grid), method="linear"
    )
    terrain_grid = griddata(
        (lon, lat), world.terrain, (lon_grid, lat_grid), method="nearest"
    )

    # Calculate 3D coordinates
    height_fac = 0.01
    R = 1 + height_fac * (np.where(alt_grid > 0, alt_grid / 1000.0, 0))
    x = R * np.cos(np.radians(lat_grid)) * np.cos(np.radians(lon_grid))
    y = R * np.cos(np.radians(lat_grid)) * np.sin(np.radians(lon_grid))
    z = R * np.sin(np.radians(lat_grid))

    # Create Plotly surface plot
    _terrain_colors = [
        [i / (len(terrain_colors.colors) - 1), c]
        for i, c in enumerate(terrain_colors.colors)
    ]
    fig = go.Figure(
        go.Surface(
            x=x,
            y=y,
            z=z,
            surfacecolor=terrain_grid,
            colorscale=_terrain_colors,
            showscale=False,
        )
    )
    fig.update_layout(
        scene=dict(
            xaxis=dict(showbackground=False, showticklabels=False, visible=False),
            yaxis=dict(showbackground=False, showticklabels=False, visible=False),
            zaxis=dict(showbackground=False, showticklabels=False, visible=False),
            aspectmode="data",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.show()
    html_content = fig.to_html(include_plotlyjs="cdn")

    return {"message": "World generated", "html": html_content}
