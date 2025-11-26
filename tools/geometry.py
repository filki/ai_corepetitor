import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import uuid

def draw_shape(shape_type: str, side: float = 0, width: float = 0, height: float = 0, radius: float = 0, base: float = 0, color: str = 'skyblue'):
    """
    Draws a 2D shape and saves it to a file.
    
    Args:
        shape_type: The type of shape to draw. Options: 'square', 'rectangle', 'circle', 'triangle'.
        side: Length of the side for a square.
        width: Width of a rectangle.
        height: Height of a rectangle or triangle.
        radius: Radius of a circle.
        base: Base length of a triangle.
        color: Color of the shape (e.g., 'red', 'blue', 'green'). Default is 'skyblue'.
            
    Returns:
        str: The path to the saved image file.
    """
    
    # Ensure static directory exists
    if not os.path.exists("static"):
        os.makedirs("static")
        
    fig, ax = plt.subplots()
    
    if shape_type == 'square':
        s = float(side) if side else 5.0
        rect = patches.Rectangle((0, 0), s, s, linewidth=2, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.set_xlim(-1, s + 1)
        ax.set_ylim(-1, s + 1)
        
    elif shape_type == 'rectangle':
        w = float(width) if width else 5.0
        h = float(height) if height else 3.0
        rect = patches.Rectangle((0, 0), w, h, linewidth=2, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.set_xlim(-1, w + 1)
        ax.set_ylim(-1, h + 1)
        
    elif shape_type == 'circle':
        r = float(radius) if radius else 3.0
        circle = patches.Circle((0, 0), r, linewidth=2, edgecolor='black', facecolor=color)
        ax.add_patch(circle)
        ax.set_xlim(-r - 1, r + 1)
        ax.set_ylim(-r - 1, r + 1)
        
    elif shape_type == 'triangle':
        b = float(base) if base else 4.0
        h = float(height) if height else 3.0
        # Points: (0,0), (base, 0), (base/2, height) - isosceles
        triangle = patches.Polygon([[0, 0], [b, 0], [b/2, h]], closed=True, linewidth=2, edgecolor='black', facecolor=color)
        ax.add_patch(triangle)
        ax.set_xlim(-1, b + 1)
        ax.set_ylim(-1, h + 1)

    ax.set_aspect('equal')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.title(f"{shape_type.capitalize()}")
    
    # Save file
    filename = f"shape_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join("static", filename)
    plt.savefig(filepath)
    plt.close()
    
    return filepath