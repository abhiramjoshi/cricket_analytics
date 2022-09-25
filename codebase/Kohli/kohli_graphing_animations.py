import codebase.graphing_manim as gm
import codebase.analysis_functions as af
from manim import *
import os
from utils import DATA_LOCATION
import pickle

KOHLI_ID = '253802'
ROOT_PLAYER_ID = '303669'
WILLIAMSON_PLAYER_ID = '277906'
SPD_SMITH_ID = '267192'

PLAYER_IDS = [
    KOHLI_ID,
    ROOT_PLAYER_ID,
    WILLIAMSON_PLAYER_ID,
    SPD_SMITH_ID
]
#y_values = [[j*i for j in range(50)] for i in range(4)]

class Fab4Careers(Scene):
    
    def __init__(self, renderer=None, camera_class=Camera, always_update_mobjects=False, random_seed=None, skip_animations=False):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        if os.path.exists(os.path.join(DATA_LOCATION, 'career_dict_fab4.p')):
            with open(os.path.join(DATA_LOCATION, 'career_dict_fab4.p'), 'rb') as f:
                career_forms_fab4 = pickle.load(f)

        else:
            career_forms_fab4 = af.apply_aggregate_func_to_list(PLAYER_IDS, [af.calculate_running_average, af.calculate_recent_form_average], disable_logging=False, return_innings=True)
            with open(os.path.join(DATA_LOCATION, 'career_dict_fab4.p'), 'wb') as f:
                career_forms_fab4 = pickle.dump(career_forms_fab4, f)

        self._y_values = [career_forms_fab4['calculate_recent_form_average'][key] for key in career_forms_fab4['calculate_recent_form_average']]
        self._x_values = [i for i in range(len(max(y_values, key=lambda x: len(x))))]

    #x_values = [i for i in range(50)]

    def construct(self):
        linegraph = gm.LineGraph(
            x_values=self._x_values,
            y_values=self._y_values,
            # y_range=[25,75],
            y_length=5,
            x_length=10,
            only_create_lines=True
        )

        labels=linegraph.get_line_labels(
            values=[
                'Kohli',
                'Root',
                'Williamson',
                'Smith'
            ]
        )
        
        # legend = linegraph.get_legend(
        #     values=[
        #         'Kohli',
        #         'Root',
        #         'Williamson',
        #         'Smith'
        #     ]
        # )
        #legend.next_to((linegraph.c2p(1, 0)[0], (linegraph.c2p(0, linegraph.y_range[1])[1]-legend.height/2), 0))
        #self.add(linegraph, labels)
        lines = linegraph.lines
        self.play(Write(linegraph))
        for line in lines:
            self.play(Write(line))
            self.wait(1)
        self.play(Write(labels))
        self.wait(2)

if __name__ == "__main__":
    
    scene = Fab4Careers()
    scene.render()

