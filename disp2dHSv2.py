import pandas as pd
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import datetime
from scipy.stats import gaussian_kde
from matplotlib.colors import Normalize # Normalizeをimport

def round_time_to_nearest_60min(dt):
    minute = dt.minute
    delta = (minute + 30) // 60 * 60 - minute
    rounded_dt = dt + datetime.timedelta(minutes=delta)
    return rounded_dt.replace(second=0, microsecond=0)

def idx_of_the_nearest(data, value):
    idx = np.argmin(np.abs(np.array(data) - value))
    return idx

# Path to your SWAN NetCDF file
file_path = 'hsign.nc'
nc_file = Dataset(file_path, 'r')

# Example: Reading the 'significant_wave_height' (SWH) variable
swan_stime     = datetime.datetime.strptime('2023-10-01 00:00:00', '%Y-%m-%d %H:%M:%S')
swan_hs        = nc_file.variables['hs'][:]  # Use the actual variable name in your SWAN file
print(swan_hs.shape)
swan_longitude = nc_file.variables['longitude'][:]
swan_latitude  = nc_file.variables['latitude'][:]
swan_hs1d      = []

print(swan_stime)
print(swan_longitude)
print(swan_latitude)

# 
# Path to your CSV file (replace with the actual file path)
file_path = 'swhOnly_202310231430-1500.csv' # validation data set

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(file_path)
nrt_latitude  = df['latitude'].to_numpy()
nrt_longitude = df['longitude'].to_numpy()
nrt_swh       = df['value'].to_numpy()
nrt_time      = df['time'].to_numpy()
nrt_hs1d    = []
maxvalue = 6
#
fig, ax = plt.subplots()
#plt.figure(figsize=(10, 6))
levels = np.linspace(0, maxvalue, 13)
#levels = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]
plt.contourf(swan_longitude, swan_latitude ,swan_hs[(23-1)*24+15+1,:,:], vmin=0.0, vmax=maxvalue, levels=levels, cmap='jet', norm=Normalize(vmin=0, vmax=maxvalue)) # 23日15時のSWAN
plt.colorbar(label='Significant Wave Height (m)', ax=ax, shrink=0.90, norm=Normalize(vmin=0, vmax=9))
plt.title('SWH by SWAN. Case: ERA5surface-SWAN(JANSSEN)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.xlim([30, 80])
plt.ylim([-8, 32])
#plt.show()
ax.set_aspect('equal')

plt.scatter(nrt_longitude, nrt_latitude, vmin=0.0, vmax=maxvalue, c=nrt_swh, cmap='jet', s=5, alpha=0.5)
plt.scatter(52.45, 15.5, color='black', s=10, alpha=0.5)
plt.savefig("2dimensionalWRF(ERA5)-SWAN(JANSSEN).png", dpi=300)
plt.show()
