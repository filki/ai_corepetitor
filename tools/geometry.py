import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import uuid

def draw_shape(shape_type: str, **kwargs):
    """
    Draws a 2D shape and saves it to a file.
    
    Args:
        shape_type: 'triangle', 'square', 'rectangle', 'circle'
        kwargs: 
            - for 'triangle': a, b, c (side lengths) OR base, height
            - for 'square': side
            - for 'rectangle': width, height
            - for 'circle': radius
            - color: 'blue', 'red', 'green', etc. (default: 'blue')
            
    Returns:
        str: The path to the saved image file.
    """
    
    # Ensure static directory exists
    if not os.path.exists("static"):
        os.makedirs("static")
        
    fig, ax = plt.subplots()
    color = kwargs.get('color', 'skyblue')
    
    if shape_type == 'square':
        side = float(kwargs.get('side', 5))
        rect = patches.Rectangle((0, 0), side, side, linewidth=2, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.set_xlim(-1, side + 1)
        ax.set_ylim(-1, side + 1)
        
    elif shape_type == 'rectangle':
        width = float(kwargs.get('width', 5))
        height = float(kwargs.get('height', 3))
        rect = patches.Rectangle((0, 0), width, height, linewidth=2, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.set_xlim(-1, width + 1)
        ax.set_ylim(-1, height + 1)
        
    elif shape_type == 'circle':
        radius = float(kwargs.get('radius', 3))
        circle = patches.Circle((0, 0), radius, linewidth=2, edgecolor='black', facecolor=color)
        ax.add_patch(circle)
        ax.set_xlim(-radius - 1, radius + 1)
        ax.set_ylim(-radius - 1, radius + 1)
        
    elif shape_type == 'triangle':
        # Simple implementation for equilateral/isosceles or base/height
        # Defaulting to a simple triangle with base and height for visualization
        base = float(kwargs.get('base', 4))
        height = float(kwargs.get('height', 3))
        # Points: (0,0), (base, 0), (base/2, height) - isosceles
        triangle = patches.Polygon([[0, 0], [base, 0], [base/2, height]], closed=True, linewidth=2, edgecolor='black', facecolor=color)
        ax.add_patch(triangle)
        ax.set_xlim(-1, base + 1)
        ax.set_ylim(-1, height + 1)

    ax.set_aspect('equal')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.title(f"{shape_type.capitalize()}")
    
    # Save file
    filename = f"shape_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join("static", filename)
    plt.savefig(filepath)
    plt.close()
    
    return f"Image saved to {filepath}"