import matplotlib.pyplot as plt

def img_gen_country(data, filename):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis('tight')
    ax.axis('off')

    col_max_lens = []
    for col in data.columns:
        max_len = max(len(str(col)), data[col].astype(str).map(len).max())
        col_max_lens.append(max_len)

    total_len = sum(col_max_lens)
    col_widths = [max_len / total_len if total_len > 0 else 1/len(data.columns) for max_len in col_max_lens]

    table = ax.table(
        cellText=data.values,
        colLabels=data.columns,
        loc='center',
        cellLoc='center',
        colWidths=col_widths
    )

    num_rows = len(data)
    for (row, col), cell in table.get_celld().items():
        cell.PAD = 0
        if row == 0:
            cell.set_fontsize(12)
            cell.get_text().set_fontweight('bold')
            cell.set_facecolor('#002859')
            cell.get_text().set_color('white')
            cell.get_text().set_ha('center')
        elif row == num_rows:
            cell.set_fontsize(12)
            cell.get_text().set_fontweight('bold')
            cell.set_facecolor('#002859')
            cell.get_text().set_color('white')
            text = cell.get_text().get_text().strip()
            is_numeric = True
            try:
                cleaned = text.replace(',', '').replace('%', '')
                float(cleaned)
            except ValueError:
                is_numeric = False
            cell.get_text().set_ha('right' if is_numeric else 'center')
            if text:
                cell.get_text().set_text(text + ' ')
        else:
            cell.set_fontsize(10)
            text = cell.get_text().get_text().strip()
            is_numeric = True
            try:
                cleaned = text.replace(',', '').replace('%', '')
                float(cleaned)
            except ValueError:
                is_numeric = False
            cell.get_text().set_ha('right' if is_numeric else 'center')
            if text:
                cell.get_text().set_text(text + ' ')

    plt.savefig(filename, bbox_inches='tight', dpi=300, pad_inches=0)
    plt.close()

def img_gen_pic(data, filename):
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.axis('tight')
    ax.axis('off')

    col_max_lens = []
    for col in data.columns:
        max_len = max(len(str(col)), data[col].astype(str).map(len).max())
        col_max_lens.append(max_len)

    total_len = sum(col_max_lens)
    col_widths = [max_len / total_len if total_len > 0 else 1/len(data.columns) for max_len in col_max_lens]

    table = ax.table(
        cellText=data.values,
        colLabels=data.columns,
        loc='center',
        cellLoc='center',
        colWidths=col_widths
    )

    num_rows = len(data)
    for (row, col), cell in table.get_celld().items():
        cell.PAD = 0
        if row == 0:
            cell.set_fontsize(13)
            cell.get_text().set_fontweight('bold')
            cell.set_facecolor('#002859')
            cell.get_text().set_color('white')
            cell.get_text().set_ha('center')
        elif row == num_rows:
            cell.set_fontsize(13)
            cell.get_text().set_fontweight('bold')
            cell.set_facecolor('#002859')
            cell.get_text().set_color('white')
            text = cell.get_text().get_text().strip()
            is_numeric = True
            try:
                cleaned = text.replace(',', '').replace('%', '')
                float(cleaned)
            except ValueError:
                is_numeric = False
            cell.get_text().set_ha('right' if is_numeric else 'center')
            if text:
                cell.get_text().set_text(text + ' ')
        else:
            cell.set_fontsize(11)
            text = cell.get_text().get_text().strip()
            is_numeric = True
            try:
                cleaned = text.replace(',', '').replace('%', '')
                float(cleaned)
            except ValueError:
                is_numeric = False
            cell.get_text().set_ha('right' if is_numeric else 'center')
            if text:
                cell.get_text().set_text(text + ' ')

    plt.savefig(filename, bbox_inches='tight', dpi=300, pad_inches=0)
    plt.close()