# -*- coding: utf-8 -*-
"""
Created on Thu Jun 12 10:19:14 2025

@author: weaam
"""
import folium
import pandas as pd
import geopandas as gpd
from branca.colormap import StepColormap
from folium import Element

# === Load your data ===
model_data = model_data_bc = pd.read_csv(r"C:\Users\weaam\OneDrive\Desktop\UFP_mm.csv")# Replace with actual path
df_fixed = pd.read_csv(r"C:\Users\weaam\OneDrive\Desktop\Research\Projects\3 - Beirut Monitoring Campaign\1 - Data used for training\FixedSites_percentiles_UFP.csv")    # fixed sites (49)
gdf = gpd.read_file(r"C:\Users\weaam\OneDrive\Desktop\Research\Projects\3 - Beirut Monitoring Campaign\lb_shp\shap\beirut.shp").to_crs(epsg=4326)
model_data_bc = pd.read_csv(r"C:\Users\weaam\OneDrive\Desktop\BC_mm_1.csv")
df_fixed_bc = pd.read_csv(r"C:\Users\weaam\OneDrive\Desktop\Research\Projects\3 - Beirut Monitoring Campaign\1 - Data used for training\FixedSites_percentiles_BC.csv")    # fixed sites (49)
from branca.element import MacroElement
from jinja2 import Template

class LatLonSearch(MacroElement):
    def __init__(self):
        super().__init__()
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
        var searchControl = L.control({ position: 'topright' });
        searchControl.onAdd = function (map) {
            var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            div.innerHTML = `
              <input id="coord-search" type="text" placeholder="Search by Lat, Lon"
                     style="
                        width: 260px;
                        height: 36px;
                        font-size: 14px;
                        padding: 6px 12px;
                        border-radius: 20px;
                        border: 1px solid #ccc;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
                        outline: none;
                        font-family: Arial, sans-serif;
                     " />
            `;
            div.style.backgroundColor = 'transparent';
            div.style.boxShadow = 'none';
            return div;
        };
        searchControl.addTo({{ this._parent.get_name() }});

        setTimeout(function () {
            var input = document.getElementById('coord-search');
            if (input) {
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        var coords = input.value.split(',');
                        if (coords.length === 2) {
                            var lat = parseFloat(coords[0].trim());
                            var lon = parseFloat(coords[1].trim());
                            if (!isNaN(lat) && !isNaN(lon)) {
                                {{ this._parent.get_name() }}.setView([lat, lon], 16);
                                L.marker([lat, lon]).addTo({{ this._parent.get_name() }})
                                  .bindPopup("Lat: " + lat.toFixed(5) + "<br>Lon: " + lon.toFixed(5)).openPopup();
                            } else {
                                alert("Invalid coordinates.");
                            }
                        }
                    }
                });
            }
        }, 500);
        {% endmacro %}
        """)
# === Create Map ===
from folium.features import DivIcon

m = folium.Map(location=[33.89, 35.50], zoom_start=12, control_scale=True,tiles=None)
# === Basemap Layers ===
folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
folium.TileLayer('CartoDB Positron', name='CartoDB Positron').add_to(m)
folium.TileLayer('CartoDB Dark_Matter', name='CartoDB Dark Matter').add_to(m)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='ESRI World Imagery',
    name='ESRI World Imagery'
).add_to(m)

ufp_layer = folium.FeatureGroup(name='UFP Concentration', show=True)
bc_layer = folium.FeatureGroup(name='BC Concentration', show=False)
# === Step Colormap ===
colormap = StepColormap(
    colors=['#F5F500', '#F5B800', '#F57A00', '#F53D00', '#F50000'],
    vmin=0, vmax=200000,
    index=[0, 30000, 50000, 70000, 100000],
    caption='UFP Concentration (#/cm³)'
)
colormap_bc = StepColormap(
    colors=['#F5F500', '#F5B800', '#F57A00', '#F53D00', '#F50000'],
    vmin=0, vmax=30000,
    index=[0, 3000, 6000, 9000, 12000],
    caption='BC Concentration (ng/m³)'
)
# === Add CircleMarkers ===
for _, row in model_data.iterrows():
    tooltip_text_ufp = folium.Tooltip(
        f"<b>Average UFP Measured (#/cm³):</b> {row['UFP']:.0f}",
        sticky=True
    )
    
    folium.CircleMarker(
        location=[row['Latitude_point'], row['Longitude_point']],
        radius=4,
        color=colormap(row['UFP']),
        fill=True,
        fill_color=colormap(row['UFP']),
        fill_opacity=0.8,
        tooltip=tooltip_text_ufp
    ).add_to(ufp_layer)

# === Add Fixed Sites (star markers) ===
for _, row in df_fixed.iterrows():
    tooltip_text_ufp_fixed = folium.Tooltip(
        f"<b>Average UFP Measured (#/cm³):</b> {row['mean']:.0f}",
        sticky=True
    )
    folium.Marker(
    location=[row['Latitude'], row['Longitude']],
    icon=DivIcon(
        icon_size=(80, 80),
        icon_anchor=(15, 15),
        html=f"""
        <div style="
            font-size: 20px;
            color: {colormap(row['mean'])};
            text-shadow: 
                -1px -1px 0 black, 
                 1px -1px 0 black, 
                -1px  1px 0 black, 
                 1px  1px 0 black;
            transform: rotate(0deg);
            line-height: 20px;
        ">
            ★
        </div>
        """
    ),
    tooltip=tooltip_text_ufp_fixed
).add_to(ufp_layer)
# === Add CircleMarkers ===
for _, row in model_data_bc.iterrows():
    tooltip_text_bc = folium.Tooltip(
        f"<b>Average BC Measured (ng/m³):</b> {row['BC']:.0f}",
        sticky=True
    )
    folium.CircleMarker(
        location=[row['Latitude_point'], row['Longitude_point']],
        radius=4,
        color=colormap_bc(row['BC']),
        fill=True,
        fill_color=colormap_bc(row['BC']),
        fill_opacity=0.8,
        tooltip=tooltip_text_bc
    ).add_to(bc_layer)

# === Add Fixed Sites (triangle markers) ===
for _, row in df_fixed_bc.iterrows():
    tooltip_text_bc_fixed = folium.Tooltip(
        f"<b>Average BC Measured (ng/m³):</b> {row['BC_mean']:.0f}",
        sticky=True
    )
    folium.Marker(
    location=[row['Latitude'], row['Longitude']],
    icon=DivIcon(
        icon_size=(80, 80),
        icon_anchor=(15, 15),
        html=f"""
        <div style="
            font-size: 20px;
            color: {colormap_bc(row['BC_mean'])};
            text-shadow: 
                -1px -1px 0 black, 
                 1px -1px 0 black, 
                -1px  1px 0 black, 
                 1px  1px 0 black;
            transform: rotate(0deg);
            line-height: 20px;
        ">
            ★
        </div>
        """
    ),
    tooltip=tooltip_text_bc_fixed
).add_to(bc_layer)
ufp_layer.add_to(m)
bc_layer.add_to(m)
# === Add Boundary ===
folium.GeoJson(
    gdf.to_json(),
    name="Beirut Boundary",
    style_function=lambda x: {
        'fill': False,
        'color': 'white',
        'weight': 2,
        'dashArray': '5, 5'
    },
    tooltip="Beirut"
).add_to(m)

# === Add Airport Icon ===
folium.Marker(
    location=[33.8268, 35.4930],
    icon=folium.Icon(icon='plane', prefix='fa', color='blue'),
    popup="Beirut–Rafic Hariri Intl Airport"
).add_to(m)

# === Add Custom Legend ===
ufp_legend = """
<div id="ufp-legend" style="display: block; position: fixed; bottom: 30px; right: 30px; width: 300px; height: auto; z-index:9999;
    font-size: 14px; background-color: rgba(0,0,0,0.6); padding: 12px; color: white; border-radius: 5px;">
<b style="font-size: 16px;">UFP Concentration (#/cm³)</b><br><br>

<div style="display: flex; align-items: center;"><div style="background:#F5F500;width:30px;height:10px;margin-right:8px;"></div> 0 – 30000</div>
<div style="display: flex; align-items: center;"><div style="background:#F5B800;width:30px;height:10px;margin-right:8px;"></div> 30000 – 50000</div>
<div style="display: flex; align-items: center;"><div style="background:#F57A00;width:30px;height:10px;margin-right:8px;"></div> 50000 – 70000</div>
<div style="display: flex; align-items: center;"><div style="background:#F53D00;width:30px;height:10px;margin-right:8px;"></div> 70000 – 100000</div>
<div style="display: flex; align-items: center;"><div style="background:#F50000;width:30px;height:10px;margin-right:8px;"></div> > 100000</div>

<br><b style="font-size: 16px;">Marker Legend</b><br><br>
<div style="display: flex; align-items: center;">
  <div style="width:12px;height:12px;border-radius:50%;background:white;border:1px solid black;margin-right:8px;"></div> 
  Mobile Monitoring
</div>
<div style="display: flex; align-items: center;">
  <div style="font-size: 16px; color: white; margin-right: 8px; line-height: 12px;">★</div> 
  Fixed Site
</div>
</div>
"""

bc_legend = """
<div id="bc-legend" style="display: none; position: fixed; bottom: 30px; right: 30px; width: 300px; height: auto; z-index:9999;
    font-size: 14px; background-color: rgba(0,0,0,0.6); padding: 12px; color: white; border-radius: 5px;">
<b style="font-size: 16px;">BC Concentration (ng/m³)</b><br><br>

<div style="display: flex; align-items: center;"><div style="background:#F5F500;width:30px;height:10px;margin-right:8px;"></div> 0 – 3000</div>
<div style="display: flex; align-items: center;"><div style="background:#F5B800;width:30px;height:10px;margin-right:8px;"></div> 3000 – 6000</div>
<div style="display: flex; align-items: center;"><div style="background:#F57A00;width:30px;height:10px;margin-right:8px;"></div> 6000 – 9000</div>
<div style="display: flex; align-items: center;"><div style="background:#F53D00;width:30px;height:10px;margin-right:8px;"></div> 9000 – 12000</div>
<div style="display: flex; align-items: center;"><div style="background:#F50000;width:30px;height:10px;margin-right:8px;"></div> > 12000</div>

<br><b style="font-size: 16px;">Marker Legend</b><br><br>
<div style="display: flex; align-items: center;">
  <div style="width:12px;height:12px;border-radius:50%;background:white;border:1px solid black;margin-right:8px;"></div> 
  Mobile Monitoring
</div>
<div style="display: flex; align-items: center;">
  <div style="font-size: 16px; color: white; margin-right: 8px;">★</div> 
  Fixed Site
</div>
</div> 
"""


m.get_root().html.add_child(Element(ufp_legend))
m.get_root().html.add_child(Element(bc_legend))
# === Add North Arrow (base64) ===
north_arrow = """
<div style="position: fixed; top: 80px; left: 20px; z-index:9999;
             background-color: rgba(255, 255, 255, 0.7); padding: 4px; border-radius: 4px;">
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAACNElEQVR4nO3dMU4CURAF0HMT7L6zEIgMYeIJG8hr7LVq7GCzq7O6kegNXXN2fnRYvnkye+KFV9UpX1SlfVKX9UpX1SlfVKX9UpX1SlfVKX9UpX1SlfVKX9UpX1SlfVKX9Upf1yQqbuQ7PhzGjdMGc3Q+PWyL6NSCfp1IU7qa9mkZDZTUtIItWnJ0gQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7Sn5gQ7WnZgQ7Wn5gQ7SnZgQ7S/X6roek4gmr5J61lAAAAAElFTkSuQmCC"
       style="width:30px; transform: rotate(0deg);" alt="North Arrow">
</div>
"""
bounds = [[33.866, 35.477], [33.913, 35.543]]
from folium.raster_layers import ImageOverlay
from folium.plugins import FloatImage
# Add the generator image as an overlay
generator_layer = folium.FeatureGroup(name='Generator Sites', show=False)

ImageOverlay(
    name='Generator Sites',
    image=r"C:\Users\weaam\OneDrive\Desktop\Research\Projects\3 - Beirut Monitoring Campaign\Maps HTML\generator_map.png",  # Must be in the same directory as the HTML output
    bounds=bounds,
    opacity=0.75,
    interactive=True,
    cross_origin=False
).add_to(generator_layer)

generator_layer.add_to(m)
#m.get_root().html.add_child(Element(north_arrow))
map_id = m.get_name()
legend_script = """
<script>
window.onload = function () {
    function updateLegend() {
        let ufpOn = false;
        let bcOn = false;
        document.querySelectorAll('.leaflet-control-layers-overlays input').forEach(input => {
            const label = input.nextSibling?.textContent?.trim();
            if (label === "UFP Concentration" && input.checked) ufpOn = true;
            if (label === "BC Concentration" && input.checked) bcOn = true;
        });
        document.getElementById('ufp-legend').style.display = ufpOn ? 'block' : 'none';
        document.getElementById('bc-legend').style.display = bcOn ? 'block' : 'none';
    }

    document.querySelectorAll('.leaflet-control-layers-overlays input').forEach(input => {
        input.addEventListener('change', updateLegend);
    });

    updateLegend();
};
</script>
"""
m.get_root().html.add_child(Element(legend_script))

#m.add_child(LatLonSearch())

# === Centered Search Bar + Logo in Top-Right ===
import base64

# === Logo in top-right ===
# === Logo in top header ===
with open("C:/Users/weaam/OneDrive/Desktop/Research/Projects/3 - Beirut Monitoring Campaign/Python Coding/PositiveZero_Branding_White.png", "rb") as f:
    encoded_logo = base64.b64encode(f.read()).decode()

# === Header with title and logo ===
header_html = f"""
<div style="
    position: fixed;
    top: 0px;
    left: 0;
    width: 100%;
    height: 60px;
    background-color: #002147;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    font-family: Arial, sans-serif;
    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
">
    <div style="font-size: 20px; font-weight: bold; color: #ffffff;">
        Measured UFP and BC Concentrations - Greater Beirut Area 2024
    </div>
    <img src="data:image/png;base64,{encoded_logo}" style="height: 80px;" />
</div>
"""
m.get_root().html.add_child(Element(header_html))

# === Search bar (below header) ===
custom_header = f"""
<div style="
    position: fixed;
    top: 70px;
    left: 50%;
    transform: translateX(-50%);
    z-index:9999;">
    <input id="coord-search" type="text" placeholder="Search by Latitude, Longitude"
           style="width: 260px; height: 36px; font-size: 14px; padding: 6px 12px;
           border-radius: 20px; border: 1px solid #ccc; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
           outline: none; font-family: Arial, sans-serif;" />
</div>

<script>
setTimeout(function () {{
    var input = document.getElementById('coord-search');
    if (input) {{
        input.addEventListener('keydown', function(e) {{
            if (e.key === 'Enter') {{
                var coords = input.value.split(',');
                if (coords.length === 2) {{
                    var lat = parseFloat(coords[0].trim());
                    var lon = parseFloat(coords[1].trim());
                    if (!isNaN(lat) && !isNaN(lon)) {{
                        var map = window.{m.get_name()};
                        map.setView([lat, lon], 16);
                        L.marker([lat, lon]).addTo(map)
                          .bindPopup("Lat: " + lat.toFixed(5) + "<br>Lon: " + lon.toFixed(5)).openPopup();
                    }} else {{
                        alert("Invalid coordinates.");
                    }}
                }}
            }}
        }});
    }}
}}, 500);
</script>
"""
m.get_root().html.add_child(Element(custom_header.replace("{map_id}", m.get_name())))

# === CSS fix to push layer control down below header ===
layer_offset_css = """
<style>
.leaflet-control-layers {
    margin-top: 80px !important;
}
</style>
"""
m.get_root().html.add_child(Element(layer_offset_css))

zoom_style = """
<style>
.leaflet-control-zoom {
    top: 60px !important;  /* Adjust this value as needed */
}
</style>
"""
m.get_root().html.add_child(Element(zoom_style))

# === Add layer control and save map ===
folium.LayerControl().add_to(m)
m.save(r'C:\Users\weaam\OneDrive\Desktop\Research\Projects\3 - Beirut Monitoring Campaign\Maps HTML\Measured_concentrations1.html')
##################################################################################
#Predictions 
import folium
import geopandas as gpd
from branca.colormap import StepColormap

# === Load fishnet with predictions ===
fishnet = gpd.read_file(r"C:\Users\weaam\OneDrive\Desktop\Research\Projects\3 - Beirut Monitoring Campaign\6 - Surfaces\UFP_HybridCluster_GBA_XG_surface.shp").to_crs(epsg=4326)
value_column = 'prediction'
ufp_layer = folium.FeatureGroup(name='UFP prediction', show=True)

fishnet_BC = gpd.read_file(r"C:\Users\weaam\OneDrive\Desktop\Research\Projects\3 - Beirut Monitoring Campaign\6 - Surfaces\BC_HybridCluster_GBA_XG_surface.shp").to_crs(epsg=4326)
value_column = 'prediction'
bc_layer = folium.FeatureGroup(name='BC prediction', show=False)
# === Initialize map ===
m = folium.Map(location=[33.89, 35.50], zoom_start=12, control_scale=True,tiles=None)
# === Basemap Layers ===
folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
folium.TileLayer('CartoDB Positron', name='CartoDB Positron').add_to(m)
folium.TileLayer('CartoDB Dark_Matter', name='CartoDB Dark Matter').add_to(m)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='ESRI World Imagery',
    name='ESRI World Imagery'
).add_to(m)
# === Colormap ===
colormap = StepColormap(
    colors=['#F5F500', '#F5B800', '#F57A00', '#F53D00', '#F50000'],
    vmin=0, vmax=fishnet["prediction"].max(),
    index=[0, 30000, 50000, 70000, 100000],
    caption='Predicted UFP (#/cm³)'
)
colormap_bc = StepColormap(
    colors=['#F5F500', '#F5B800', '#F57A00', '#F53D00', '#F50000'],
    vmin=0, vmax=fishnet_BC["prediction"].max(),
    index=[0, 3000, 6000, 9000, 12000],
    caption='Predicted BC (ng/m³)'
)

# === Add polygons ===
folium.GeoJson(
    fishnet,
    name="Predicted UFP Surface",
    style_function=lambda feature: {
        'fillColor': colormap(feature['properties']['prediction']),
        'color': 'black',
        'weight': 0,
        'fillOpacity': 0.7,
    },
    tooltip=folium.GeoJsonTooltip(fields=['prediction'], aliases=['UFP Prediction (#/cm³)'])
).add_to(ufp_layer)

folium.GeoJson(
    fishnet_BC,
    name="Predicted BC Surface",
    style_function=lambda feature: {
        'fillColor': colormap_bc(feature['properties']['prediction']),
        'color': 'black',
        'weight': 0,
        'fillOpacity': 0.7,
    },
    tooltip=folium.GeoJsonTooltip(fields=['prediction'], aliases=['BC Prediction (ng/m³)'])
).add_to(bc_layer)
#colormap.add_to(m)

# Optional: Add boundary
folium.GeoJson(
    gdf.to_json(),
    name="Beirut Boundary",
    style_function=lambda x: {'fill': False, 'color': 'white', 'weight': 2, 'dashArray': '5,5'}
).add_to(m)

m.add_child(LatLonSearch())

# === Add Airport Icon ===
folium.Marker(
    location=[33.8268, 35.4930],
    icon=folium.Icon(icon='plane', prefix='fa', color='blue'),
    popup="Beirut–Rafic Hariri Intl Airport"
).add_to(m)
ufp_layer.add_to(m)
bc_layer.add_to(m)

# === Add Custom Legend ===
ufp_legend  = """
<div id="ufp-legend" style="display: block; position: fixed; bottom: 30px; right: 30px; width: 280px; height: auto; z-index:9999;
    font-size: 14px; background-color: rgba(0,0,0,0.6); padding: 10px; color: white; border-radius: 5px;">
<b style="font-size: 16px;">UFP Concentration (#/cm³)</b><br><br>
<div style="display: flex; align-items: center;">
  <div style="background:#F5F500;width:30px;height:10px;margin-right:8px;"></div> 0 – 30000
</div>
<div style="display: flex; align-items: center;">
  <div style="background:#F5B800;width:30px;height:10px;margin-right:8px;"></div> 30000 – 50000
</div>
<div style="display: flex; align-items: center;">
  <div style="background:#F57A00;width:30px;height:10px;margin-right:8px;"></div> 50000 – 70000
</div>
<div style="display: flex; align-items: center;">
  <div style="background:#F53D00;width:30px;height:10px;margin-right:8px;"></div> 70000 – 100000
</div>
<div style="display: flex; align-items: center;">
  <div style="background:#F50000;width:30px;height:10px;margin-right:8px;"></div> > 100000
</div>
</div>"""

bc_legend  = """
<div id="bc-legend" style="display: none; position: fixed; bottom: 30px; right: 30px; width: 280px; height: auto; z-index:9999;
    font-size: 14px; background-color: rgba(0,0,0,0.6); padding: 10px; color: white; border-radius: 5px;">
<b style="font-size: 16px;">BC Concentration (ng/m³)</b><br><br>
<div style="display: flex; align-items: center;">
  <div style="background:#F5F500;width:30px;height:10px;margin-right:8px;"></div> 0 – 3000
</div>
<div style="display: flex; align-items: center;">
  <div style="background:#F5B800;width:30px;height:10px;margin-right:8px;"></div> 3000 – 6000
</div>
<div style="display: flex; align-items: center;">
  <div style="background:#F57A00;width:30px;height:10px;margin-right:8px;"></div> 6000 – 9000
</div>
<div style="display: flex; align-items: center;">
  <div style="background:#F53D00;width:30px;height:10px;margin-right:8px;"></div> 9000 – 12000
</div>
<div style="display: flex; align-items: center;">
  <div style="background:#F50000;width:30px;height:10px;margin-right:8px;"></div> > 12000
</div>
</div>"""



m.get_root().html.add_child(Element(ufp_legend))
m.get_root().html.add_child(Element(bc_legend))
map_id = m.get_name()
legend_script = """
<script>
window.onload = function () {
    function updateLegend() {
        let ufpOn = false;
        let bcOn = false;
        document.querySelectorAll('.leaflet-control-layers-overlays input').forEach(input => {
            const label = input.nextSibling?.textContent?.trim();
            if (label === "UFP prediction" && input.checked) ufpOn = true;
            if (label === "BC prediction" && input.checked) bcOn = true;
        });
        document.getElementById('ufp-legend').style.display = ufpOn ? 'block' : 'none';
        document.getElementById('bc-legend').style.display = bcOn ? 'block' : 'none';
    }

    document.querySelectorAll('.leaflet-control-layers-overlays input').forEach(input => {
        input.addEventListener('change', updateLegend);
    });

    updateLegend();
};
</script>
"""
m.get_root().html.add_child(Element(legend_script))# === Add Layer Control ===
# === Centered Search Bar + Logo in Top-Right ===
import base64

# === Logo in top-right ===
# === Logo in top header ===
with open("C:/Users/weaam/OneDrive/Desktop/Research/Projects/3 - Beirut Monitoring Campaign/Python Coding/PositiveZero_Branding_White.png", "rb") as f:
    encoded_logo = base64.b64encode(f.read()).decode()

# === Header with title and logo ===
header_html = f"""
<div style="
    position: fixed;
    top: 0px;
    left: 0;
    width: 100%;
    height: 60px;
    background-color: #002147;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    font-family: Arial, sans-serif;
    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
">
    <div style="font-size: 20px; font-weight: bold; color: #ffffff;">
        Predicted UFP and BC Concentrations - Greater Beirut Area 2024
    </div>
    <img src="data:image/png;base64,{encoded_logo}" style="height: 80px;" />
</div>
"""
m.get_root().html.add_child(Element(header_html))

# === Search bar (below header) ===
custom_header = f"""
<div style="
    position: fixed;
    top: 70px;
    left: 50%;
    transform: translateX(-50%);
    z-index:9999;">
    <input id="coord-search" type="text" placeholder="Search by Latitude, Longitude"
           style="width: 260px; height: 36px; font-size: 14px; padding: 6px 12px;
           border-radius: 20px; border: 1px solid #ccc; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
           outline: none; font-family: Arial, sans-serif;" />
</div>

<script>
setTimeout(function () {{
    var input = document.getElementById('coord-search');
    if (input) {{
        input.addEventListener('keydown', function(e) {{
            if (e.key === 'Enter') {{
                var coords = input.value.split(',');
                if (coords.length === 2) {{
                    var lat = parseFloat(coords[0].trim());
                    var lon = parseFloat(coords[1].trim());
                    if (!isNaN(lat) && !isNaN(lon)) {{
                        var map = window.{m.get_name()};
                        map.setView([lat, lon], 16);
                        L.marker([lat, lon]).addTo(map)
                          .bindPopup("Lat: " + lat.toFixed(5) + "<br>Lon: " + lon.toFixed(5)).openPopup();
                    }} else {{
                        alert("Invalid coordinates.");
                    }}
                }}
            }}
        }});
    }}
}}, 500);
</script>
"""
m.get_root().html.add_child(Element(custom_header.replace("{map_id}", m.get_name())))

# === CSS fix to push layer control down below header ===
layer_offset_css = """
<style>
.leaflet-control-layers {
    margin-top: 80px !important;
}
</style>
"""
m.get_root().html.add_child(Element(layer_offset_css))

zoom_style = """
<style>
.leaflet-control-zoom {
    top: 60px !important;  /* Adjust this value as needed */
}
</style>
"""
m.get_root().html.add_child(Element(zoom_style))

# === Add layer control and save map ===

folium.LayerControl().add_to(m)

# === Save to file ===
m.save(r'C:\Users\weaam\OneDrive\Desktop\Research\Projects\3 - Beirut Monitoring Campaign\Maps HTML\Predicted_concentrations.html')
