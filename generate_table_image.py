import matplotlib.pyplot as plt
from matplotlib.table import Table
from PIL import Image

def generate_table_image(data, headers, filename="table.png"):
    fig, ax = plt.subplots(figsize=(10, 2))  # Adjust the size to fit the content
    ax.axis('tight')
    ax.axis('off')

    # Add a title to the table
    ax.set_title("Task List", fontweight="bold", fontsize=16, pad=12)

    # Create the table with some additional styling
    table = ax.table(cellText=[headers] + data, cellLoc='center', loc='center')

    # Style the header
    for (i, j), cell in table.get_celld().items():
        cell.set_fontsize(12)
        if i == 0:  # header
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#40466e')
            cell.set_text_props(color='w')
        elif i % 2 == 0:
            cell.set_facecolor('#f5f5f5')
        else:
            cell.set_facecolor('#ffffff')

    table.auto_set_column_width(col=list(range(len(headers))))  # Auto set the width of the columns
    table.scale(1, 1.5)  # Adjust the scale of the table

    fig.tight_layout()

    plt.savefig(filename, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return filename
