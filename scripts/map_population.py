import sys
from pathlib import Path

import folium
import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def build_map(path):
    tracts = gpd.read_file(path).to_crs("EPSG:4326")

    city_map = folium.Map(
        location=[37.54, -77.44],
        zoom_start=11,
        tiles=None,
    )

    population_layer = folium.Choropleth(
        geo_data=tracts.to_json(),
        data=tracts,
        columns=["geoid", "population"],
        key_on="feature.properties.geoid",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.4,
        legend_name="Estimated population per tract — ACS 2020–2024",
        name="Population estimates",
    ).add_to(city_map)

    population_layer.geojson.add_child(
        folium.GeoJsonTooltip(
            fields=["geoid", "population", "households"],
            aliases=["Tract GEOID:", "Population:", "Households:"],
            localize=True,
        )
    )

    min_lon, min_lat, max_lon, max_lat = tracts.total_bounds
    city_map.fit_bounds([
        [min_lat, min_lon],
        [max_lat, max_lon],
    ])

    title = """
    <h3 style="text-align:center">
        Richmond Population Estimates — ACS 2020–2024
    </h3>
    """
    city_map.get_root().html.add_child(folium.Element(title))

    output_dir = PROJECT_ROOT / "data" / "maps"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{path.stem}_population.html"
    city_map.save(str(output_path))

    print(f"Map saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python scripts/map_population.py <joined_geojson_path>"
        )

    build_map(Path(sys.argv[1]))