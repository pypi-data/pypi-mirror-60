# CTT Sensor Station Utility
### Requirements
[pandas - Python Data Analysis Library](https://pandas.pydata.org/)
### Directions
Clone the repository to your computer.
The `data_manager.py` script can merge a set of data files saved by the sensor station into single data files.
### Example
`python data_manager.py ./data/rotated/ctt`
This will merge all files in the `./data/rotated/ctt` directory and save output files in the current directory:
* station-beep-data.merged.2020-01-06_202843.csv
* station-gps-data.merged.2020-01-06_202843.csv
* station-health-data.merged.2020-01-06_202843.csv

You can optionally specify begin and end dates between which to export data by calling the export function with a begin and end date.

