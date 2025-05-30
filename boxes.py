# Generates an SVG layout of a box with customizable finger joints for laser cutting, based on user-defined dimensions and settings.

import svgwrite

# Settings
settings = {
    'finger_joint': {
        'style': 'rectangular',
        'finger_width': 2.0,
        'space': 2.0,
        'extra_length': 0.0,
        'play': 0.0,
        'width': 1.0,
    },
    'lid': {
        'handle': 'none',
        'style': 'none',
        'handle_height': 8.0,
        'height': 4.0,
        'play': 0.1,
    },
    'box': {
        'x': 100.0,  # inner width
        'y': 100.0,  # inner depth
        'h': 100.0,  # inner height
        'thickness': 3.0,  # thickness of material
    },
    'burn': 0.1,  # burn correction (in mm)
}

def create_box_svg(settings):
    # Create a new SVG drawing
    dwg = svgwrite.Drawing("box_with_finger_joints.svg", profile="tiny")

    # Box dimensions based on input
    x, y, h = settings['box']['x'], settings['box']['y'], settings['box']['h']
    thickness = settings['box']['thickness']
    
    # Calculate the outer dimensions considering thickness
    outer_x = x + 2 * thickness
    outer_y = y + 2 * thickness
    outer_h = h + 2 * thickness
    
    # Finger joint settings
    finger_width = settings['finger_joint']['finger_width'] * thickness
    space = settings['finger_joint']['space'] * thickness
    
    # Draw the base of the box (rectangular)
    dwg.add(dwg.rect(insert=(thickness, thickness), size=(x, y), stroke="black", fill="none", stroke_width=1))
    
    # Draw the sides of the box
    # Left side
    dwg.add(dwg.rect(insert=(0, thickness), size=(thickness, y), stroke="black", fill="none", stroke_width=1))
    # Right side
    dwg.add(dwg.rect(insert=(outer_x, thickness), size=(thickness, y), stroke="black", fill="none", stroke_width=1))
    # Top side
    dwg.add(dwg.rect(insert=(thickness, 0), size=(x, thickness), stroke="black", fill="none", stroke_width=1))
    # Bottom side
    dwg.add(dwg.rect(insert=(thickness, outer_y), size=(x, thickness), stroke="black", fill="none", stroke_width=1))
    
    # Create the finger joints (for simplicity, just creating rectangular placeholders)
    for i in range(0, int(x / (finger_width + space))):
        start_x = thickness + i * (finger_width + space)
        dwg.add(dwg.rect(insert=(start_x, 0), size=(finger_width, thickness), stroke="black", fill="none", stroke_width=1))

    # Save the SVG file
    dwg.save()
    print("SVG file created: box_with_finger_joints.svg")

# Generate the box SVG
create_box_svg(settings)
