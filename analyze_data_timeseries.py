import xarray as xr
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

#day_order = ['d2', 'd6', 'd12', 'd18', 'd30']

# data_paths = [r'D:\Projects\OIC-267\processed\2026-03-13\20250927 real test batch1\D2\data.nc',
#               r'D:\Projects\OIC-267\processed\2026-03-13\20250927 real test batch1\D6\data.nc',
#               r'D:\Projects\OIC-267\processed\2026-03-13\20250927 real test batch1\D12\data.nc',
#               r'D:\Projects\OIC-267\processed\2026-03-13\20250927 real test batch1\D18\data.nc',
#               r'D:\Projects\OIC-267\processed\2026-03-13\20250927 real test batch1\D30\data.nc',
#               ]

# output_dir = Path(r'D:\Projects\OIC-267\processed\2026-03-13\20250927 real test batch1')

data_paths = [r'D:\Projects\OIC-267\processed\2026-03-13\20251205 real test batch2\D2\data.nc',
              r'D:\Projects\OIC-267\processed\2026-03-13\20251205 real test batch2\D6\data.nc',
              r'D:\Projects\OIC-267\processed\2026-03-13\20251205 real test batch2\D12\data.nc',
              r'D:\Projects\OIC-267\processed\2026-03-13\20251205 real test batch2\D18\data.nc',
              r'D:\Projects\OIC-267\processed\2026-03-13\20251205 real test batch2\D30\data.nc',
              ]

output_dir = Path(r'D:\Projects\OIC-267\processed\2026-03-13\20251205 real test batch2')



all_datasets = []

for p in data_paths:
    all_datasets.append(xr.open_dataset(p))

ds = xr.concat(all_datasets, dim="id")

# Save the combined dataset
ds.to_netcdf(output_dir / "combined_data.nc")

df = ds.to_dataframe()
df.to_csv(output_dir / "combined_data.csv")



ds.area.attrs['units'] = 'microns^2'
ds.feret_diameter_max.attrs['units'] = 'microns'

# Generate plots

df = ds.to_dataframe()

# Plot the area vs day for all the different genotypes
fig = plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='Day', y='area', hue='genotype', palette='Set2')

plt.title("Cell Area by Day and Genotype")
unit_label = ds.area.attrs.get('units', 'pixels')
plt.ylabel(f"Area ({unit_label})")

fig.savefig(output_dir / "area_overall.png")

plt.close()

fig = plt.figure(figsize=(10, 6))
# Plot just the area for a single genotype
df = ds.sel(genotype='c34').sortby('Day').area.to_dataframe().reset_index()

sns.boxplot(data=df, x='Day', y='area')
unit_label = ds.area.attrs.get('units', 'pixels')
plt.ylabel(f"Area ({unit_label})")

fig.savefig(output_dir / "Area_c34.png")