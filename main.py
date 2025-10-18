# main.py
import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QFileDialog, QTableView,
                             QComboBox, QLineEdit, QLabel, QTabWidget,
                             QMessageBox, QSplitter, QGroupBox)
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QColor, QPalette
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np


# ----------------------------- Table Model -----------------------------
class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == Qt.BackgroundRole:
                # Alternate row colors
                if index.row() % 2 == 0:
                    return QColor(50, 50, 50)
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None


# ----------------------------- Main Dashboard -----------------------------
class DataAnalyticsDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.filtered_df = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Data Analytics Dashboard')
        self.setGeometry(100, 100, 1400, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Data and Chart Tabs
        self.data_tab = QWidget()
        self.tabs.addTab(self.data_tab, "Data View")

        self.charts_tab = QWidget()
        self.tabs.addTab(self.charts_tab, "Charts")

        self.setup_data_tab()
        self.setup_charts_tab()

        # Status bar
        self.statusBar().showMessage('Ready to import data')

    # ----------------------------- DATA TAB -----------------------------
    def setup_data_tab(self):
        layout = QVBoxLayout(self.data_tab)

        controls_layout = QHBoxLayout()

        # Buttons
        self.import_btn = QPushButton('Import CSV/Excel')
        self.import_btn.clicked.connect(self.import_data)
        controls_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton('Export Data')
        self.export_btn.clicked.connect(self.export_data)
        self.export_btn.setEnabled(False)
        controls_layout.addWidget(self.export_btn)

        controls_layout.addSpacing(20)
        controls_layout.addWidget(QLabel('Filter Column:'))

        self.filter_column = QComboBox()
        self.filter_column.currentTextChanged.connect(self.update_filter_value_combo)
        controls_layout.addWidget(self.filter_column)

        controls_layout.addWidget(QLabel('Filter Value:'))
        self.filter_value = QComboBox()
        controls_layout.addWidget(self.filter_value)

        self.filter_btn = QPushButton('Apply Filter')
        self.filter_btn.clicked.connect(self.apply_filter)
        self.filter_btn.setEnabled(False)
        controls_layout.addWidget(self.filter_btn)

        self.clear_filter_btn = QPushButton('Clear Filter')
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        self.clear_filter_btn.setEnabled(False)
        controls_layout.addWidget(self.clear_filter_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Table
        self.table_view = QTableView()
        layout.addWidget(self.table_view)

        # Info
        self.info_label = QLabel('No data loaded')
        self.info_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.info_label)

    # ----------------------------- CHARTS TAB -----------------------------
    def setup_charts_tab(self):
        layout = QVBoxLayout(self.charts_tab)
        chart_controls = QHBoxLayout()

        chart_controls.addWidget(QLabel('Chart Type:'))
        self.chart_type = QComboBox()
        self.chart_type.addItems(['Bar Chart', 'Line Chart', 'Scatter Plot', 'Histogram', 'Box Plot'])
        chart_controls.addWidget(self.chart_type)

        chart_controls.addWidget(QLabel('X-Axis:'))
        self.x_axis = QComboBox()
        chart_controls.addWidget(self.x_axis)

        chart_controls.addWidget(QLabel('Y-Axis:'))
        self.y_axis = QComboBox()
        chart_controls.addWidget(self.y_axis)

        self.generate_chart_btn = QPushButton('Generate Chart')
        self.generate_chart_btn.clicked.connect(self.generate_chart)
        self.generate_chart_btn.setEnabled(False)
        chart_controls.addWidget(self.generate_chart_btn)

        chart_controls.addStretch()
        layout.addLayout(chart_controls)

        # Chart Area
        self.chart_widget = QWidget()
        chart_layout = QVBoxLayout(self.chart_widget)
        self.figure = plt.figure(facecolor='#2b2b2b')
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        layout.addWidget(self.chart_widget)

    # ----------------------------- DATA FUNCTIONS -----------------------------
    def import_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Data File', '', 'CSV Files (*.csv);;Excel Files (*.xlsx *.xls)')

        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                else:
                    self.df = pd.read_excel(file_path)

                self.filtered_df = self.df.copy()
                self.update_data_display()
                self.update_filter_controls()
                self.update_chart_controls()

                self.export_btn.setEnabled(True)
                self.filter_btn.setEnabled(True)
                self.clear_filter_btn.setEnabled(True)
                self.generate_chart_btn.setEnabled(True)

                self.statusBar().showMessage(f'Data loaded: {len(self.df)} rows, {len(self.df.columns)} columns')

            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load file:\n{str(e)}')

    def update_data_display(self):
        model = PandasModel(self.filtered_df)
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()

        total_rows = len(self.df)
        filtered_rows = len(self.filtered_df)
        info_text = f'Total Rows: {total_rows}'
        if filtered_rows != total_rows:
            info_text += f' | Filtered: {filtered_rows}'
        self.info_label.setText(info_text)

    def update_filter_controls(self):
        self.filter_column.clear()
        self.filter_column.addItems(self.df.columns.tolist())
        self.update_filter_value_combo(self.filter_column.currentText())

    def update_filter_value_combo(self, column_name):
        if self.df is not None and column_name in self.df.columns:
            self.filter_value.clear()
            unique_values = self.df[column_name].dropna().unique()
            self.filter_value.addItems([str(val) for val in unique_values])

    def update_chart_controls(self):
        self.x_axis.clear()
        self.y_axis.clear()
        if self.df is not None:
            cols = self.df.columns.tolist()
            self.x_axis.addItems(cols)
            self.y_axis.addItems(cols)

    def apply_filter(self):
        if self.df is not None:
            col = self.filter_column.currentText()
            val = self.filter_value.currentText()
            try:
                num_val = float(val)
                self.filtered_df = self.df[self.df[col] == num_val]
            except ValueError:
                self.filtered_df = self.df[self.df[col].astype(str) == val]
            self.update_data_display()

    def clear_filter(self):
        if self.df is not None:
            self.filtered_df = self.df.copy()
            self.update_data_display()

    def export_data(self):
        if self.filtered_df is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Export Data', '', 'CSV Files (*.csv);;Excel Files (*.xlsx)')
            if file_path:
                try:
                    if file_path.endswith('.csv'):
                        self.filtered_df.to_csv(file_path, index=False)
                    else:
                        self.filtered_df.to_excel(file_path, index=False)
                    QMessageBox.information(self, 'Success', 'Data exported successfully!')
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to export:\n{str(e)}')

    # ----------------------------- CHART FUNCTIONS -----------------------------
    def generate_chart(self):
        if self.filtered_df is None:
            return

        chart_type = self.chart_type.currentText()
        x_col = self.x_axis.currentText()
        y_col = self.y_axis.currentText()

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')

        try:
            if chart_type == 'Bar Chart':
                if self.filtered_df[x_col].dtype == 'object':
                    data = self.filtered_df.groupby(x_col)[y_col].mean()
                    data.plot(kind='bar', ax=ax, color='skyblue')
                    ax.set_ylabel(f'Average {y_col}')
                else:
                    self.filtered_df[x_col].value_counts().head(10).plot(kind='bar', ax=ax, color='lightgreen')
                    ax.set_ylabel('Count')
                ax.set_xlabel(x_col)

            elif chart_type == 'Line Chart':
                ax.plot(self.filtered_df[x_col], self.filtered_df[y_col], color='cyan', linewidth=2)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)

            elif chart_type == 'Scatter Plot':
                ax.scatter(self.filtered_df[x_col], self.filtered_df[y_col], color='orange', alpha=0.7)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)

            elif chart_type == 'Histogram':
                self.filtered_df[x_col].hist(ax=ax, bins=20, color='violet', alpha=0.7)
                ax.set_xlabel(x_col)
                ax.set_ylabel('Frequency')

            elif chart_type == 'Box Plot':
                self.filtered_df[[x_col, y_col]].boxplot(ax=ax)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)

            ax.set_title(f'{chart_type}: {x_col} vs {y_col}')
            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            QMessageBox.warning(self, 'Chart Error', f'Could not generate chart:\n{str(e)}')


# ----------------------------- MODERN THEME -----------------------------
def set_modern_theme(app, theme="dark"):
    palette = QPalette()
    if theme == "dark":
        palette.setColor(QPalette.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.Highlight, QColor(100, 150, 200))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)


# ----------------------------- MAIN -----------------------------
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    set_modern_theme(app, theme="dark")

    dashboard = DataAnalyticsDashboard()
    dashboard.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
