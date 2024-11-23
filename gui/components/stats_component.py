from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QScrollArea, QWidget
from .base_component import BaseComponent

class StatsComponent(BaseComponent):
    def __init__(self, calculator, parent=None):
        self.calculator = calculator
        super().__init__(parent)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Free and Train pools
        pool_layout = QHBoxLayout()
        self.free_pool_label = QLabel("Free Points: 0")
        self.train_pool_label = QLabel("Train Points: 0")
        pool_layout.addWidget(self.free_pool_label)
        pool_layout.addWidget(self.train_pool_label)
        layout.addLayout(pool_layout)

        # Stats
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        stats_widget = QWidget()
        scroll_area.setWidget(stats_widget)
        stats_layout = QHBoxLayout(stats_widget)

        self.stat_widgets = {}
        for primary, secondary_stats in self.calculator.primary_stats.items():
            primary_frame = QFrame()
            primary_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
            primary_layout = QVBoxLayout(primary_frame)
            primary_layout.addWidget(QLabel(f"<b>{primary}</b>"))

            for stat in secondary_stats:
                stat_layout = QGridLayout()
                stat_layout.addWidget(QLabel(f"<b>{stat}</b>"), 0, 0, 1, 4)
                
                self.stat_widgets[stat] = {}
                for i, category in enumerate(['auto', 'free', 'train']):
                    stat_layout.addWidget(QLabel(f"{category.capitalize()}:"), i+1, 0)
                    value_label = QLabel(str(self.calculator.stats[stat][category]))
                    stat_layout.addWidget(value_label, i+1, 1)
                    self.stat_widgets[stat][category] = value_label
                    if category != 'auto':
                        minus_button = QPushButton("-")
                        minus_button.clicked.connect(lambda _, s=stat, c=category: self.update_stat(s, c, -1))
                        stat_layout.addWidget(minus_button, i+1, 2)
                        plus_button = QPushButton("+")
                        plus_button.clicked.connect(lambda _, s=stat, c=category: self.update_stat(s, c, 1))
                        stat_layout.addWidget(plus_button, i+1, 3)
                        self.stat_widgets[stat][f"{category}_minus"] = minus_button
                        self.stat_widgets[stat][f"{category}_plus"] = plus_button

                weight_label = QLabel(f"Weight: {self.calculator.stats[stat]['weight']:.2f}")
                stat_layout.addWidget(weight_label, 4, 0, 1, 2)
                constraint_label = QLabel(f"Constraint: {self.calculator.stats[stat]['constraint']:.2f}%")
                stat_layout.addWidget(constraint_label, 4, 2, 1, 2)
                total_label = QLabel(f"Total: {self.calculator.stats[stat]['total']}")
                stat_layout.addWidget(total_label, 5, 0, 1, 4)

                self.stat_widgets[stat]['weight'] = weight_label
                self.stat_widgets[stat]['constraint'] = constraint_label
                self.stat_widgets[stat]['total'] = total_label

                primary_layout.addLayout(stat_layout)

            primary_total_label = QLabel(f"Primary {primary}: {self.calculator.primary_totals[primary]:.2f}")
            primary_layout.addWidget(primary_total_label)
            self.stat_widgets[primary] = {'total': primary_total_label}

            stats_layout.addWidget(primary_frame)

    def update_stat(self, stat, category, change):
        if self.calculator.update(stat, category, change):
            self.update_display()

    def update_display(self):
        for stat, widgets in self.stat_widgets.items():
            if stat in self.calculator.primary_stats:
                widgets['total'].setText(f"Primary {stat}: {self.calculator.primary_totals[stat]:.2f}")
            else:
                for category in ['auto', 'free', 'train']:
                    widgets[category].setText(str(self.calculator.stats[stat][category]))
                widgets['weight'].setText(f"Weight: {self.calculator.stats[stat]['weight']:.2f}")
                
                constraint_value = self.calculator.stats[stat]['constraint']
                constraint_text = f"Constraint: {constraint_value:.2f}%"
                widgets['constraint'].setText(constraint_text)
                
                if constraint_value >= 40:
                    widgets['constraint'].setStyleSheet("color: red;")
                elif constraint_value <= 10:
                    widgets['constraint'].setStyleSheet("color: maroon;")
                else:
                    widgets['constraint'].setStyleSheet("")
                
                widgets['total'].setText(f"Total: {self.calculator.stats[stat]['total']}")

                for category in ['free', 'train']:
                    minus_button = widgets[f"{category}_minus"]
                    plus_button = widgets[f"{category}_plus"]
                    minus_button.setEnabled(self.calculator.stats[stat][category] > 0)
                    plus_button.setEnabled(getattr(self.calculator, f"{category}_points") > 0)

        self.free_pool_label.setText(f"Free Points: {self.calculator.free_points}")
        self.train_pool_label.setText(f"Train Points: {self.calculator.train_points}")