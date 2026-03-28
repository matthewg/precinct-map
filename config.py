import yaml
import os

class Config:
    def __init__(self, data):
        self._data = data
        self.join_keys = data.get('join_keys', {})
        self.geo_join_key = self.join_keys.get('geo_join_key')
        self.csv_join_key = self.join_keys.get('csv_join_key')
        
        if not self.geo_join_key or not self.csv_join_key:
            raise ValueError("Configuration must provide both geo_join_key and csv_join_key in 'join_keys'")

        self.subarea_filter = data.get('subarea_filter', {})
        self.display = data.get('display', {})
        self.value_column = self.display.get('value_column')
        self.title = self.display.get('title', 'Choropleth Map')
        self.tooltips = self.display.get('tooltips', [self.geo_join_key])
        self.drop_unmatched_geo = self.display.get('drop_unmatched_geo', True)
        
    @classmethod
    def from_yaml(cls, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(data)
