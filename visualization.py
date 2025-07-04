import folium
import pandas as pd
import geopandas as gpd
import random
import seaborn as sns


def create_base_map(base_lat: pd.Series, base_lon: pd.Series, zoom: int) -> folium.Map:
    m = folium.Map(
        location=[base_lat.mean(), base_lon.mean()],
        zoom_start=zoom,
        min_lat=base_lat.min(),
        max_lat=base_lat.max(),
        min_lon=base_lon.min(),
        max_lon=base_lon.max(),
    )

    return m


def add_population_points(
    m: folium.Map, pop_data: pd.DataFrame, circle_size_scale: float, color: str
) -> folium.Map:
    for _, row in pop_data.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=row["Pop"] / circle_size_scale,
            color=color,
            fill=False,
            tooltip=f"Population: {row['Pop']}",
        ).add_to(m)
    return m


def add_stops(m: folium.Map, stops_data: pd.DataFrame) -> folium.Map:
    for _, stop in stops_data.iterrows():
        folium.Marker(
            location=[stop["stop_lat"], stop["stop_lon"]], popup=stop["stop_name"]
        ).add_to(m)
    return m


def visualize_pop_stops(
    save_filename: str,
    zoom: int = 2,
    pop_data: pd.DataFrame | None = None,
    circle_size_scale: float = 100,
    stops_data: pd.DataFrame | None = None,
) -> None:

    if pop_data is not None:
        m = create_base_map(pop_data["lat"], pop_data["lon"], zoom)
    else:  # either stops_data or pop_data must be given

        m = create_base_map(stops_data["stop_lat"], stops_data["stop_lon"], zoom)

    # If given, add population points to the map as circles with radius proportional to population
    if pop_data is not None:
        m = add_population_points(
            m, pop_data=pop_data, circle_size_scale=circle_size_scale, color="blue"
        )

    # If stops data is given, add markers for each stop to the map
    if stops_data is not None:
        m = add_stops(m=m, stops_data=stops_data)

    m.save(save_filename)


def visualize_pop_reach(
    save_filename: str,
    reach_area_gdf: gpd.GeoDataFrame,
    pop_data: pd.DataFrame,
    zoom: int = 7,
    circle_size_scale: float = 100,
) -> None:

    m = create_base_map(pop_data["lat"], pop_data["lon"], zoom)

    # Add reach area to the map
    geojson = reach_area_gdf.set_crs(epsg=4326)
    folium.GeoJson(geojson).add_to(m)

    # Add population points to the map
    m = add_population_points(
        m, pop_data=pop_data, circle_size_scale=circle_size_scale, color="red"
    )

    m.save(save_filename)


def visualize_clusters(
    save_filename: str,
    pop_data: pd.DataFrame,
    zoom: int = 7,
    circle_size_scale: float = 100,
    n_clusters: int = 1000,
) -> None:

    num_colors = n_clusters

    colors = sns.color_palette(palette="hls", n_colors=num_colors).as_hex()
    random.shuffle(colors)

    m = create_base_map(pop_data["lat"], pop_data["lon"], zoom)

    # Add population points to the map with color specified with the cluster number
    for _, row in pop_data.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=row["Pop"] / circle_size_scale,
            color=colors[row["cluster"]],
            fill=False,
            tooltip=f"Cluster: {row['cluster']}, Population: {row['Pop']}",
        ).add_to(m)

    m.save(save_filename)
