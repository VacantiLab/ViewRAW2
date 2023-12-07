from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
from bokeh.io import curdoc
from bokeh.models import TextInput, NumeralTickFormatter, PrintfTickFormatter
from bokeh.events import DoubleTap, Tap

from fisher_py import RawFile
from fisher_py.data.business import TraceType, Scan
import numpy as np
import os

from pdb import set_trace

# Get the absolute path of the directory of the script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Change the working directory
os.chdir(dir_path)

filename = '/Users/nate/Dropbox/Research/Vacanti_Laboratory/projects/DNS_MassSpectrometry/ReadRawFile/ViewRAW/YY2019060827.raw'
raw_file = RawFile(filename)


target_mass = 205.098
mass_tolerance_ppm = 1e11
rt, i = raw_file.get_chromatogram(target_mass, mass_tolerance_ppm,TraceType.MassRange)
mz, i2, charges, real_rt = raw_file.get_scan_ms1(5.7)
a_scanned_mass = mz[0]

# Define the data for the plots
data = ColumnDataSource(data=dict(
    x=rt,
    y=i
))

# Create a figure for the line plot
p1 = figure(width=1200, height=400, title='Chromatograph')
# Add a line glyph to the line plot
p1.line('x', 'y', source=data, line_width=2)
p1.xaxis.axis_line_width = 3
p1.yaxis.axis_line_width = 3
p1.xaxis.major_tick_line_width = 3
p1.yaxis.major_tick_line_width = 3
p1.xaxis.minor_tick_line_color = None
p1.yaxis.minor_tick_line_color = None
p1.xgrid.grid_line_color = None
p1.ygrid.grid_line_color = None
p1.outline_line_color = None
p1.xaxis.major_label_text_font_size = "12pt"
p1.yaxis.major_label_text_font_size = "12pt"
p1.yaxis[0].formatter = PrintfTickFormatter(format="%.1e")


# Define the data for the bar plot
data2 = ColumnDataSource(data=dict(
    x=mz,
    y=i2,
    width=[0.5]*len(mz)
))

# Create a figure for the bar plot
# Create a figure for the bar plot
p2 = figure(width=1200, height=400, title='Mass Sepctrum')
# Add a vbar glyph to the bar plot with a smaller width
#p2.vbar(x='x', top='y', width=0.002, source=data2)  # set width to 0.1
p2.line('x', 'y', source=data2, line_width=2)
p2.xaxis.axis_line_width = 3
p2.yaxis.axis_line_width = 3
p2.xaxis.major_tick_line_width = 3
p2.yaxis.major_tick_line_width = 3
p2.xaxis.minor_tick_line_color = None
p2.yaxis.minor_tick_line_color = None
p2.xgrid.grid_line_color = None
p2.ygrid.grid_line_color = None
p2.outline_line_color = None
p2.xaxis.major_label_text_font_size = "12pt"
p2.yaxis.major_label_text_font_size = "12pt"
p2.yaxis[0].formatter = PrintfTickFormatter(format="%.1e")

# Create TextInput widgets for target_mass and mass_tolerance_ppm
target_mass_input = TextInput(value=str('TIC'), title="Target Mass:")
mass_tolerance_ppm_input = TextInput(value=str('NA'), title="Mass Tolerance PPM:")

# Define a function to update the data source for the plots
def update_data_source(attr, old, new, a_scanned_mass=a_scanned_mass):
    if target_mass_input.value == 'TIC':
        target_mass = a_scanned_mass
        mass_tolerance_ppm = 1e11
    if target_mass_input.value != 'TIC':
        mass_tolerance_ppm = mass_tolerance_ppm_input.value
        if mass_tolerance_ppm == 'NA':
            mass_tolerance_ppm = 10
        target_mass = float(target_mass_input.value)
        mass_tolerance_ppm = float(mass_tolerance_ppm)
    rt, i = raw_file.get_chromatogram(target_mass, mass_tolerance_ppm,TraceType.MassRange)
    mz, i2, charges, real_rt = raw_file.get_scan_ms1(5.7)
    data.data = dict(x=rt, y=i)
    data2.data = dict(x=mz, y=i2, width=[0.002]*len(mz))

# Define a function to update the data source for the second plot
def update_data_source2(event):
    # Get the x-coordinate of the click event
    x_value = event.x
    
    # Use the x-value as the input to raw_file.get_scan_ms1()
    mz, i2, charges, real_rt = raw_file.get_scan_ms1(x_value)
    data2.data = dict(x=mz, y=i2, width=[0.002]*len(mz))

# Use the on_event method of the first plot to call the function
p1.on_event(Tap, update_data_source2)

# Add the callback function to the TextInput widgets
target_mass_input.on_change('value', update_data_source)
mass_tolerance_ppm_input.on_change('value', update_data_source)


# Create a layout to arrange the plots and TextInput widgets vertically
layout = column(target_mass_input, mass_tolerance_ppm_input, p1, p2)

# Define a function to modify doc
def modify_doc(doc):
    doc.add_root(layout)

# Run the server with the function
curdoc().add_root(layout)