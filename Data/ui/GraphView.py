from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
import plotly.express as px
import plotly.graph_objects as go
import os
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QLabel
from collections import Counter

from ..core.GraphGeneration import organise_data, organise_sankey_data

class GraphView(QMainWindow):
    def __init__(self, data_file_path, self_main):
        super().__init__()
        self.setGeometry(1125, 100, 400, 650)

        if self_main.dark_theme:
            icon_path = "../icons/graph_icon-dark.ico"
        else:
            icon_path = "../icons/graph_icon-light.ico"

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(self.base_path, icon_path)))

        data = organise_data(data_file_path)

        rename_dict = {
            'car': 'Car',
            'truck': 'Truck',
            'bus': 'Bus',
        }

        data['type'] = data['type'].map(rename_dict).fillna(data['type'])

        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)

        type_counts = data['type'].value_counts()
        fig = px.bar(
            type_counts.reset_index(),
            x='type',
            y='count',
            title="Vehicle Counts by Type",
            labels={'type': 'Vehicle Type', 'count': 'Count'},
            color='type',
        )

        fig.update_layout(
            width=400,
            height=300,
            title_font=dict(size=24, color='white'),
            plot_bgcolor='rgb(30, 30, 30)',
            paper_bgcolor='rgb(30, 30, 30)',
            font=dict(family="Arial, sans-serif", size=14, color="white"),
            xaxis=dict(
                tickangle=45,
                title='Vehicle Type',
                title_font=dict(size=18, color='white'),
                tickfont=dict(size=12, color='white'),
            ),
            yaxis=dict(
                title='Count',
                title_font=dict(size=18, color='white'),
                tickfont=dict(size=12, color='white'),
            ),
        )

        image_path1 = os.path.join(self.base_path, "../temp/temp_plotly_bar_graph.png")
        image_path2 = os.path.join(self.base_path, "../temp/temp_plotly_graph2.png")

        fig.write_image(image_path1)

        pixmap = QPixmap(image_path1)
        label = QLabel(self)
        label.setPixmap(pixmap)
        central_layout.addWidget(label)

        locations, source, target, values = organise_sankey_data(data_file_path)

        flow_counter = Counter()
        for s, t, v in zip(source, target, values):
            flow_counter[(s, t)] += v
            flow_counter[(t, s)] -= v

        aggregated_source = []
        aggregated_target = []
        aggregated_values = []

        for (s, t), v in flow_counter.items():
            if v > 0:
                aggregated_source.append(s)
                aggregated_target.append(t)
                aggregated_values.append(v)

        fig2 = go.Figure(data=[go.Sankey(
            node=dict(
                pad=80,
                thickness=20,
                line=dict(color="black", width=0.7),
                label=locations,
                color=["red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan", "magenta", "brown"]
            ),
            link=dict(
                source=aggregated_source,
                target=aggregated_target,
                value=aggregated_values,
                hovertemplate='From: %{source.label} <br> To: %{target.label} <br> Value: %{value}<extra></extra>'
            )
        )])

        fig2.update_layout(
            width=400,
            height=300,
            title="Flow of Vehicles",
            title_font=dict(size=24, color='white'),
            plot_bgcolor='rgb(30, 30, 30)',
            paper_bgcolor='rgb(30, 30, 30)'
        )

        fig2.write_image(image_path2)

        pixmap2 = QPixmap(image_path2)
        label2 = QLabel(self)
        label2.setPixmap(pixmap2)
        central_layout.addWidget(label2)

        self.setCentralWidget(central_widget)

        self.setWindowTitle("Analysis Results")
