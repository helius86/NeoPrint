import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle
import numpy as np
from scipy.ndimage import gaussian_filter

data = [
    [175.2, 91.1, 0.62, 45.4],
    [220.8, 143.7, 0.93, 78.9],
    [92.4, 75.6, 1.84, 150.2],
    [40.1, 169.5, 1.01, 103.5],
    [196.3, 53.2, 0.75, 68.9],
    [119.7, 183.2, 2.01, 188.1],
    [269.1, 211.3, 0.92, 121.7],
    [259.1, 211.3, 0.34, 11.7]
]

# Set the fixed window size and create an empty matrix for the heatmap
window_size = 300
heatmap = np.zeros((window_size, window_size))

# Iterate through data points and populate the heatmap matrix
for x, y, activation_distance, activation_force in data:
    xi, yi = int(x), int(y)
    weight = activation_distance * window_size / max([point[2] for point in data]) # scale to size of window to get darker colour
    heatmap[yi, xi] += weight

# Apply a Gaussian filter to smooth the heatmap and create the heat effect around points
sigma = 10
smoothed_heatmap = gaussian_filter(heatmap, sigma)

# Create a circular mask
y, x = np.ogrid[-window_size//2:window_size//2, -window_size//2:window_size//2]
mask = x**2 + y**2 <= (window_size//2)**2
circle = Circle((window_size/2, window_size/2), radius=window_size/2, edgecolor='black', facecolor='none')


# Normalize activation distance and force values
activation_distances = [point[2] for point in data]
activation_forces = [point[3] for point in data]
normalized_distances = np.interp(activation_distances, (0, max(activation_distances)), (0, 1))
normalized_forces = np.interp(activation_forces, (0, max(activation_forces)), (0, 1))

# Create a colormap with different color shades for activation distances and lightness/darkness for activation forces
cmap = plt.cm.viridis

#customize colours
colormap = plt.get_cmap('YlOrBr')

# Create a circular RGBA image from the smoothed_heatmap
image = colormap(smoothed_heatmap)
image[~mask, 3] = 0  # Set the alpha channel to 0 outside the circular mask

# Plot the heatmap
plt.figure(figsize=(6, 6))
heatmap = plt.imshow(image, origin='lower', extent=[0, window_size, 0, window_size], aspect='auto', cmap=colormap)

#plt.colorbar(label='Activation Intensity')
cbar = plt.colorbar(heatmap)
cbar.set_label('Activation Distance')
heatmap.set_clim(vmin=0, vmax=max(activation_distances))


# Plot the data points with different colors for activation distance and different alpha for activation force
for i, (x, y, _, _) in enumerate(data):
    plt.scatter(x, y, color=colormap(normalized_distances[i]), s=125, edgecolors='black', marker='o')

plt.title('Activation Heatmap')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.gca().set_facecolor((0, 0, 0, 0))  # Set background color to transparent
plt.gca().add_patch(circle) # add circle outline to show edge of button
plt.show()
