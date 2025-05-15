import pandas as pd
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import datetime
from scipy.stats import gaussian_kde
from sklearn.metrics import mean_squared_error

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
file_path = 'swhOnly_20231001-20231101.csv' # validation data set

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(file_path)
nrt_latitude  = df['latitude'].to_numpy()
nrt_longitude = df['longitude'].to_numpy()
nrt_swh       = df['value'].to_numpy()
nrt_time      = df['time'].to_numpy()
nrt_hs1d    = []

iso_time = datetime.datetime.fromisoformat('2019-09-08T14:32:01+09:00')

for i in range(len(nrt_latitude)):

	# Convesrion from satellite time to SWAN time steps. 
	nrt_iso_time = datetime.datetime.fromisoformat(nrt_time[i])
	# 時間の丸め込み
	rounded_time = round_time_to_nearest_60min(nrt_iso_time)
	diff_time = rounded_time.replace(tzinfo=None) - swan_stime
	nrt_ntime = diff_time.days*24 + diff_time.seconds/3600
	#print(nrt_iso_time, rounded_time, nrt_ntime)
	#tmp_time = datetime.datetime.strptime(nrt_iso_time, '%Y-%m-%d %H:%M:%S')
	
	long_idx = idx_of_the_nearest(swan_longitude, nrt_longitude[i])
	lat_idx  = idx_of_the_nearest(swan_latitude, nrt_latitude[i])
	print(long_idx, lat_idx, int(nrt_ntime))
	print("swan = ", swan_hs[int(nrt_ntime)][lat_idx][long_idx], "satellite=", nrt_swh[i])
	#
	if 48 <= nrt_ntime and nrt_ntime <= 720 and nrt_swh[i] > 0.01 and swan_hs[int(nrt_ntime)][lat_idx][long_idx] > 0.01:
	#if nrt_swh[i] > 0.01 and swan_hs[int(nrt_ntime)][lat_idx][long_idx] > 0.01:
		swan_hs1d.append(swan_hs[int(nrt_ntime)][lat_idx][long_idx])
		tmp_nrt_swh = nrt_swh[i] #*0.684 + 0.128
		nrt_hs1d.append(tmp_nrt_swh)
		#nrt_hs1d.append(nrt_swh[i])
	
Rresult = np.corrcoef(swan_hs1d, nrt_hs1d)
#plt.scatter(swan_hs1d, nrt_hs1d, alpha=0.4) #, s=600, c="pink", alpha=0.5, linewidths="2", edgecolors="red")
xy1 = np.vstack([swan_hs1d, nrt_hs1d])
z1 = gaussian_kde(xy1)(xy1)

# プロットの設定
g = plt.subplot()
plt.scatter(swan_hs1d, nrt_hs1d, c=z1, s=5, marker='o', cmap='jet', alpha=0.8)
plt.plot([0,0],[4.0,4.0], linestyle="solid")
plt.xlabel('Simulated SWH by SWAN (m)')
plt.ylabel('Observed SWH by satellite (m)')

# Rの表示
Rtext = "R:" + str("{:.3f}".format(Rresult[1,0]))
boxdic = {
    "facecolor" : "white",
    "edgecolor" : "black",
    "linewidth" : 1
}
plt.text(0.2, 6.4, Rtext, backgroundcolor='white', fontsize=12, bbox=boxdic)
#
rmse = mean_squared_error(swan_hs1d, nrt_hs1d, squared=True)
print(f"RMSE: {round(rmse, 3)}")

#軸の設定
g.set_aspect('equal')
g.set_ylim([0,7.0])
g.set_xlim([0,7.0])
g.grid();
plt.savefig("scatterERA5surfaceSWAN.png")
plt.show()
