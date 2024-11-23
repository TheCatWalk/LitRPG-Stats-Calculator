from .base_calculator import BaseCalculator

class StatsCalculator(BaseCalculator):
    def __init__(self):
        self.primary_stats = {
            "Body": ["Endurance", "Vitality", "Strength", "Agility", "Dexterity"],
            "Mind": ["Intelligence", "Memory", "Perception", "Clarity", "Focus"],
            "Spirit": ["Adaptability", "Density", "Purity", "Fortitude", "Magnitude"]
        }
        self.stats = {stat: {"auto": 1, "free": 0, "train": 0, "weight": 0.20, "constraint": 20.00, "total": 1} 
                      for primary in self.primary_stats.values() for stat in primary}
        self.primary_totals = {primary: 1.0 for primary in self.primary_stats}
        self.free_points = 0
        self.train_points = 0
        self.calculate()

    def calculate(self):
        for primary, secondary_stats in self.primary_stats.items():
            total_points = sum(sum(self.stats[stat][cat] for cat in ['auto', 'free', 'train']) for stat in secondary_stats)
            total_manual_auto_points = sum(self.stats[stat]['auto'] + self.stats[stat]['free'] for stat in secondary_stats)
            primary_total = 0

            for stat in secondary_stats:
                auto = self.stats[stat]['auto']
                free = self.stats[stat]['free']
                train = self.stats[stat]['train']
                total = auto + free + train

                weight = (auto + free) / total_manual_auto_points if total_manual_auto_points > 0 else 0
                normalized_weight = weight / sum((self.stats[s]['auto'] + self.stats[s]['free']) / total_manual_auto_points
                                                 for s in secondary_stats) if total_manual_auto_points > 0 else 0

                self.stats[stat]['weight'] = weight
                self.stats[stat]['total'] = total
                self.stats[stat]['constraint'] = (total / total_points) * 100 if total_points > 0 else 0

                primary_total += total * normalized_weight

            self.primary_totals[primary] = primary_total

    def update(self, stat, category, change):
        if category == 'free':
            if self.free_points - change < 0 or self.stats[stat][category] + change < 0:
                return False
            self.free_points -= change
        elif category == 'train':
            if self.train_points - change < 0 or self.stats[stat][category] + change < 0:
                return False
            self.train_points -= change
        
        self.stats[stat][category] += change
        self.calculate()
        return True

    def level_up(self, primary):
        for stat in self.primary_stats[primary]:
            self.stats[stat]['auto'] += 1
        self.free_points += 5
        self.train_points += 5
        self.calculate()