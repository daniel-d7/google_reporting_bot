"""Image generation module for creating report charts."""
import matplotlib.pyplot as plt
import pandas as pd
from typing import Tuple

from ..utils import get_logger


logger = get_logger(__name__)


def img_gen_country(data: pd.DataFrame, filename: str) -> None:
    """
    Generate country report image as a table.
    
    Args:
        data: DataFrame with country report data
        filename: Output file path for the image
    """
    _generate_table_image(
        data=data,
        filename=filename,
        figsize=(6, 3),
        header_fontsize=12,
        data_fontsize=10,
        total_fontsize=12
    )
    logger.info(f"Country report image generated: {filename}")


def img_gen_pic(data: pd.DataFrame, filename: str) -> None:
    """
    Generate manager/PIC report image as a table.
    
    Args:
        data: DataFrame with manager report data
        filename: Output file path for the image
    """
    _generate_table_image(
        data=data,
        filename=filename,
        figsize=(6, 2),
        header_fontsize=13,
        data_fontsize=11,
        total_fontsize=13
    )
    logger.info(f"Manager report image generated: {filename}")


def _generate_table_image(
    data: pd.DataFrame,
    filename: str,
    figsize: Tuple[int, int],
    header_fontsize: int,
    data_fontsize: int,
    total_fontsize: int
) -> None:
    """
    Generate a styled table image from DataFrame.
    
    Args:
        data: DataFrame to visualize
        filename: Output file path
        figsize: Figure size as (width, height)
        header_fontsize: Font size for header row
        data_fontsize: Font size for data rows
        total_fontsize: Font size for total row
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('tight')
    ax.axis('off')
    
    # Calculate column widths based on content
    col_widths = _calculate_column_widths(data)
    
    # Create table
    table = ax.table(
        cellText=data.values,
        colLabels=data.columns,
        loc='center',
        cellLoc='center',
        colWidths=col_widths
    )
    
    # Style the table
    _style_table(table, data, header_fontsize, data_fontsize, total_fontsize)
    
    # Save image
    plt.savefig(filename, bbox_inches='tight', dpi=300, pad_inches=0)
    plt.close()


def _calculate_column_widths(data: pd.DataFrame) -> list:
    """
    Calculate proportional column widths based on content.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        List of proportional column widths
    """
    col_max_lens = []
    for col in data.columns:
        max_len = max(len(str(col)), data[col].astype(str).map(len).max())
        col_max_lens.append(max_len)
    
    total_len = sum(col_max_lens)
    col_widths = [
        max_len / total_len if total_len > 0 else 1 / len(data.columns) 
        for max_len in col_max_lens
    ]
    
    return col_widths


def _style_table(
    table,
    data: pd.DataFrame,
    header_fontsize: int,
    data_fontsize: int,
    total_fontsize: int
) -> None:
    """
    Apply styling to table cells.
    
    Args:
        table: Matplotlib table object
        data: DataFrame being visualized
        header_fontsize: Font size for header
        data_fontsize: Font size for data rows
        total_fontsize: Font size for total row
    """
    num_rows = len(data)
    
    for (row, col), cell in table.get_celld().items():
        cell.PAD = 0
        
        if row == 0:
            # Header row
            _style_header_cell(cell, header_fontsize)
        elif row == num_rows:
            # Total row
            _style_total_cell(cell, total_fontsize)
        else:
            # Data rows
            _style_data_cell(cell, data_fontsize)


def _style_header_cell(cell, fontsize: int) -> None:
    """Style header cell."""
    cell.set_fontsize(fontsize)
    cell.get_text().set_fontweight('bold')
    cell.set_facecolor('#002859')
    cell.get_text().set_color('white')
    cell.get_text().set_ha('center')


def _style_total_cell(cell, fontsize: int) -> None:
    """Style total row cell."""
    cell.set_fontsize(fontsize)
    cell.get_text().set_fontweight('bold')
    cell.set_facecolor('#002859')
    cell.get_text().set_color('white')
    
    text = cell.get_text().get_text().strip()
    is_numeric = _is_numeric_text(text)
    
    cell.get_text().set_ha('right' if is_numeric else 'center')
    if text:
        cell.get_text().set_text(text + ' ')


def _style_data_cell(cell, fontsize: int) -> None:
    """Style data row cell."""
    cell.set_fontsize(fontsize)
    
    text = cell.get_text().get_text().strip()
    is_numeric = _is_numeric_text(text)
    
    cell.get_text().set_ha('right' if is_numeric else 'center')
    if text:
        cell.get_text().set_text(text + ' ')


def _is_numeric_text(text: str) -> bool:
    """
    Check if text represents a numeric value.
    
    Args:
        text: Text to check
        
    Returns:
        True if numeric, False otherwise
    """
    try:
        cleaned = text.replace(',', '').replace('%', '')
        float(cleaned)
        return True
    except ValueError:
        return False
