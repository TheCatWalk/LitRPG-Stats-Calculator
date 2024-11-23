from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QScrollArea, QWidget
from PyQt5.QtGui import QColor
from .base_component import BaseComponent

class StatsComponent(BaseComponent):
    def __init__(self, calculator, parent=None):
        self.calculator = calculator
        self.stat_widgets = {}
        self.is_locked = True
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
        for primary in ["Body", "Spirit", "Mind"]:
            primary_frame = QFrame()
            primary_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
            primary_layout = QVBoxLayout(primary_frame)
            primary_layout.addWidget(QLabel(f"<b>{primary}</b>"))

            for stat in self.calculator.primary_stats[primary]:
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

            stats_layout.addWidget(primary_frame)

        # Primary Stats Display
        primary_stats_layout = QHBoxLayout()
        self.body_label = QLabel("Body: 0")
        self.spirit_label = QLabel("Spirit: 0")
        self.mind_label = QLabel("Mind: 0")
        
        primary_stats_layout.addWidget(self.body_label)
        primary_stats_layout.addWidget(self.spirit_label)
        primary_stats_layout.addWidget(self.mind_label)
        
        layout.addLayout(primary_stats_layout)

    def update_stat(self, stat, category, change):
        if self.calculator.update(stat, category, change):
            self.update_display()

    def update_display(self):
        stats_data = self.calculator.get_stats()
        for stat, widgets in self.stat_widgets.items():
            for category in ['auto', 'free', 'train']:
                widgets[category].setText(str(stats_data['stats'][stat][category]))
            
            weight_value = stats_data['stats'][stat]['weight']
            widgets['weight'].setText(f"Weight: {weight_value:.2f}")
            if weight_value < 0.10:
                widgets['weight'].setStyleSheet("color: maroon;")
            elif weight_value > 0.40:
                widgets['weight'].setStyleSheet("color: red;")
            else:
                widgets['weight'].setStyleSheet("")
            
            constraint_value = stats_data['stats'][stat]['constraint']
            widgets['constraint'].setText(f"Constraint: {constraint_value:.2f}%")
            if constraint_value < 10:
                widgets['constraint'].setStyleSheet("color: maroon;")
            elif constraint_value > 40:
                widgets['constraint'].setStyleSheet("color: red;")
            else:
                widgets['constraint'].setStyleSheet("")
            
            widgets['total'].setText(f"Total: {stats_data['stats'][stat]['total']}")

            for category in ['free', 'train']:
                minus_button = widgets[f"{category}_minus"]
                plus_button = widgets[f"{category}_plus"]
                minus_button.setEnabled(stats_data['stats'][stat][category] > 0)
                plus_button.setEnabled(getattr(self.calculator, f"{category}_points") > 0)

        self.free_pool_label.setText(f"Free Points: {stats_data['free_points']}")
        self.train_pool_label.setText(f"Train Points: {stats_data['train_points']}")

        self.body_label.setText(f"Body: {stats_data['primary_totals']['Body']:.2f}")
        self.spirit_label.setText(f"Spirit: {stats_data['primary_totals']['Spirit']:.2f}")
        self.mind_label.setText(f"Mind: {stats_data['primary_totals']['Mind']:.2f}")
        self.update_ui_state()

    def handle_level_up(self, new_level, primary_stat):
        self.calculator.handle_level_up(new_level, primary_stat)
        self.update_display()

    def set_locked(self, locked):
        self.is_locked = locked
        self.update_ui_state()

    def update_ui_state(self):
        for stat, widgets in self.stat_widgets.items():
            for category in ['free', 'train']:
                widgets[f"{category}_minus"].setEnabled(not self.is_locked)
                widgets[f"{category}_plus"].setEnabled(not self.is_locked)

