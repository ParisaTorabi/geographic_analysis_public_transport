import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
from sklearn.cluster import DBSCAN
from sklearn.metrics import DistanceMetric
import numpy as np


def create_reach_area(
    stops: gpd.GeoDataFrame, buffer_degrees: float
) -> gpd.GeoDataFrame:

    # function to create a buffer around each stop
    def create_buffer_500m(point):
        return point.buffer(buffer_degrees)

    # Convert latitude and longitude coordinates to Shapely Point objects
    stops["geometry"] = [Point(xy) for xy in zip(stops["stop_lon"], stops["stop_lat"])]

    # Create buffers around each stop
    stops["reach_area"] = stops["geometry"].apply(create_buffer_500m)

    # Merge overlapping buffers into a single polygon (reach area)
    reach_area_union = unary_union(stops["reach_area"])
    return gpd.GeoDataFrame(geometry=[reach_area_union])


def cluster_population(
    pop_data: gpd.GeoDataFrame, eps: float, min_samples: int
) -> np.ndarray:
    # Convert latitudes and longitudes to radians for haversine distance calculation
    coords = np.radians(pop_data[["lat", "lon"]])

    # Calculate haversine distances
    dist = DistanceMetric.get_metric("haversine")
    distances = dist.pairwise(coords)

    # Perform DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric="precomputed")
    return dbscan.fit_predict(distances, sample_weight=pop_data["Pop"])
