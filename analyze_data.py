import xarray as xr
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

microns_per_pixel = 1000 / 594
day_order = ['d2', 'd6', 'd12', 'd18', 'd30']

#data_path = Path(r'D:\Projects\OIC-267\processed\20260305\test\data.nc')
data_path = Path(r'D:\Projects\OIC-267\processed\20260306\20251205 real test batch2\data.nc')

xds = xr.open_dataset(data_path)
xds = xds.set_index(index=["genotype", "day", "image", "label"]).rename({'index':'cell_index'})

# print(xds)

# Convert units from pixels to microns
xds['area'].values = xds['area'].values * microns_per_pixel ** 2
xds.area.attrs['units'] = 'microns^2'

xds['feret_diameter_max'].values = xds['feret_diameter_max'].values * microns_per_pixel
xds.feret_diameter_max.attrs['units'] = 'microns^2'

# Convert back to a pandas dataframe to plot

df = xds.to_dataframe().reset_index()

# Plot the area vs day for all the different genotypes
fig = plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='day', y='area', hue='genotype', palette='Set2', order=day_order)

plt.title("Cell Area by Day and Genotype")
unit_label = xds.area.attrs.get('units', 'pixels')
plt.ylabel(f"Area ({unit_label})")

fig.savefig(data_path.parent / "area_overall.png")

plt.close()

fig = plt.figure(figsize=(10, 6))
# Plot just the area for a single genotype
df = xds.sel(genotype='c34').sortby('day').area.to_dataframe().reset_index()
df['area'] = df['area'] * microns_per_pixel

sns.boxplot(data=df, x='day', y='area', order=day_order)
unit_label = xds.area.attrs.get('units', 'pixels')
plt.ylabel(f"Area ({unit_label})")

fig.savefig(data_path.parent / "Area_c34.png")