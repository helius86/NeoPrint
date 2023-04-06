from PIL import Image
import imageio

with imageio.get_reader('p1.gif') as reader:
    frames = [im for im in reader]
    frames_resized = [Image.fromarray(im).resize((250, 250), resample=Image.LANCZOS) for im in frames]

# Create a list to store the output frames
frames_output = []

# Loop through the resized frames
for frame in frames_resized:
    # Create a new image with an alpha channel
    alpha = Image.new('L', frame.size, 255)
    # Convert the frame to RGBA mode and paste the alpha channel onto it
    frame_rgba = frame.convert('RGBA')
    frame_rgba.putalpha(alpha)
    # Append the resulting frame to the output frames list
    frames_output.append(frame_rgba)

# Save the resized and transparent GIF animation
imageio.mimsave('output1.gif', frames_output, duration=0.1)
