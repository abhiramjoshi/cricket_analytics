from math import isnan
import codebase.graphing_manim as gm
import codebase.analysis_functions as af
import codebase.web_scrape_functions as wsf
from manim import *
import os
from utils import DATA_LOCATION
import pickle
import pandas as pd
import json

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

kohli_stats = wsf.get_player_career_stats(KOHLI_ID)
# kohli_totals = af.get_cricket_totals(KOHLI_ID, is_object_id=True)
# root_totals = af.get_cricket_totals(ROOT_PLAYER_ID, is_object_id=True)
# williamson_totals = af.get_cricket_totals(WILLIAMSON_PLAYER_ID, is_object_id=True)
# smith_totals = af.get_cricket_totals(SPD_SMITH_ID, is_object_id=True)

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
        self._x_values = [i for i in range(len(max(self._y_values, key=lambda x: len(x))))]

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


class TestMatchScoringRates(Scene):
    
    def __init__(self, renderer=None, camera_class=Camera, always_update_mobjects=False, random_seed=None, skip_animations=False):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        
        matches_while_kohli = wsf.get_match_list(years=[2011,':'])
        pre_tests = matches_while_kohli[:398]
        post_tests = matches_while_kohli[398:]
        pre_scoring_rates_year = af.extract_scoring_rates(pre_tests, period='year')
        post_scoring_rates_year = af.extract_scoring_rates(post_tests, period='year')
        pre_scoring_rate_ave = af.resolve_scoring_rates_to_ave(pre_scoring_rates_year)
        post_scoring_rate_ave = af.resolve_scoring_rates_to_ave(post_scoring_rates_year)
        df_dict = {}
        for year in sorted(list(set(list(pre_scoring_rate_ave.keys())+list(post_scoring_rate_ave.keys())))):
            row = {}
            try:
                row['pre'] = pre_scoring_rate_ave[year]
            except KeyError:
                row['pre'] = None

            try:
                row['post'] = post_scoring_rate_ave[year]
            except KeyError:
                row['post'] = None
            
            df_dict[year] = row

        df_scoring_rates = pd.DataFrame(df_dict)
        df_scoring_rates = df_scoring_rates.T
        post_scoring_rate_ave = [float(x) if not isnan(x) else None for x in df_scoring_rates.post.to_list()]
        pre_scoring_rate_ave = [float(x) if not isnan(x) else None for x in df_scoring_rates.pre.to_list()]
        years = [int(x) for x in df_scoring_rates.index.to_list()]

        self._x_values = years
        self._y_values = [pre_scoring_rate_ave, post_scoring_rate_ave]

    def construct(self):
        graph = gm.LineGraph(
            x_values=self._x_values,
            y_values=self._y_values,
            line_names=['Pre', 'Post'],
            y_length=5,
            y_range=[2.8,4],
            x_length=10,
            x_range=[2010,2023,1],
            only_create_lines=True,
            x_axis_is_years=True
        )

        lines = graph.lines

        self.play(Write(graph))
        for line in lines:
            self.play(Create(line))
            self.wait(1)
        self.wait()

class KohliBest80Inning(Scene):

    def __init__(self, renderer=None, camera_class=Camera, always_update_mobjects=False, random_seed=None, skip_animations=False):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)

        def win_perc(result):
            total = (result['wins']+result['losses']+result['draws']+result['other'])
            percs = {key:(result[key]/total) for key in result}
            return percs

        with open(os.path.join(DATA_LOCATION, 'best_80_names.json'), 'r') as file:
            best_80_names = json.load(file)

        with open(os.path.join(DATA_LOCATION, 'results_pers_names.json'), 'r') as file:
            result_pers_names = json.load(file)

        best_80_names = {name[0]:name[1] for name in best_80_names}
        self.data = {key:(best_80_names[key], result_pers_names[key]['wins']) for key in best_80_names}
        
        self.virat_kohli = self.data['V Kohli (INDIA)']

        self.coords = [self.data[name] for name in self.data]
        self.names = list(self.data.keys())


    def construct(self):
        scatter = gm.ScatterPlot(
            values=self.coords,
            only_create_coords=True,
            x_length=10,
            y_length=5,
            x_range=[0,110],
            y_range=[0, 0.8],
            dot_radius=0.05
        )

        scatter.sort_coords()
        coords = scatter.get_coords()

        #Get VK point
        vk_point = Dot(scatter.c2p(self.virat_kohli[0], self.virat_kohli[1]), color="#58508d")
        vk_text = Tex('V Kohli', color="#58508d")
        vk_text.next_to(vk_point, UP)
        virat_kohli = VGroup(
            vk_point,
            vk_text
        )
        
        #Get better than VK points:
        better_labels = {key:self.data[key] for key in self.data if self.data[key][0] > self.virat_kohli[0] and self.data[key][1] > self.virat_kohli[1]}
        better_bats = VGroup()
        for bat in better_labels:
            better_bats.add(Dot(scatter.c2p(self.data[bat][0], self.data[bat][1]), color="#bc5090"))
        
        #Create a box that has the list of names 
        def create_name_box(names):
            box = VGroup()
            names_group = VGroup()
            for name in names:
                names_group.add(Tex(name, font_size=20))

            names_group.arrange(DOWN, aligned_edge=LEFT)
            
            box_height = names_group.get_top()[1] - names_group.get_bottom()[1] + (2*MED_SMALL_BUFF)
            box_width = names_group.get_right()[0] - names_group.get_left()[0] + (2*MED_SMALL_BUFF)
            box_border = Rectangle(height=box_height, width=box_width)
            box.add(names_group)
            box.add(box_border)
            box[0].move_to(box.get_center())

            return box

        better_bat_names = create_name_box(better_labels)
        better_bat_names.to_corner(UP+RIGHT)
        self.play(Write(scatter))
        self.play(Write(coords))
        self.play(Write(virat_kohli))
        self.wait()
        self.play(Write(better_bats))
        self.wait()
        self.play(Write(better_bat_names))
        self.wait()

class CoverDriveShotFreq(Scene):
    
    @staticmethod
    def cover_drive_freq_graph():
        KOHLI_ID = '253802'
        kohli_matches = wsf.get_player_match_list(KOHLI_ID)
        with open(os.path.join(DATA_LOCATION, 'kohli_comms.p'), 'rb') as file:
            kohli_comms = pickle.load(file)
        kohli_innings = af.get_cricket_totals(KOHLI_ID, kohli_matches, _type='bat', by_innings=True, is_object_id=True, from_scorecards=False)
        cover_drive_primary_kw = ['cover drive', 'cover-drive']

        cover_drive_search_kw = [
            'drive',
            ('punch', 0.3),
            ('cover', 0.3),
            ('off side', 0.2),
            ('full', 0.25),
            ('wide', 0.2) ,
            ('outside edge', 0.3),
            ('reach', 0.3),
            ('slip', 0.25),
            ('edge', 0.3),
            'driving',
            ('force', 0.2),
            ('push', 0.3),
            ('pitched up', 0.3),
            ('Overpitched', 0.2),
            ('dab', 0.2),
            ('outside off', 0.25)

        ]
        cover_drive_exlude_words = [
            'run out',
            'pull', 'flick', 'shoulder[\s\w]{0,}(?:arm){1,}',
            'bouncer', 'short ball', 'stays back',
            'backfoot', 'top edge', 'leave', 'back foot', ('back', 0.2),
            'lets one go', 'easy leave', 'leaves the ball', 'goes back',
            'leg side', 'leading edge', ('leg ', 0.25), 'cut', ('leg', 0.25),
            'on the pads', 'left alone', ('short', 0.25), ('midwicket', 0.2), ('long-on', 0.25), ('long on', 0.25), ('back of a length', 0.25)
        ]
        kohli_coverdrive_comms = af.search_shots_in_comms(kohli_comms, cover_drive_search_kw, cover_drive_exlude_words, cover_drive_primary_kw, threshold=0.49)
        kohli_cover_drive_stats = [af.analyse_batting_inning(inning) for inning in kohli_coverdrive_comms]
        cover_drive_perc_runs = af.fraction_of_total(kohli_cover_drive_stats, kohli_innings, 'runs')
        moving_cover_drive_perc = af.moving_average(cover_drive_perc_runs, window_size=10)


        line = gm.LineGraph(
            x_values=list(range(len(moving_cover_drive_perc))),
            y_values=moving_cover_drive_perc,
            x_length=10,
            y_length=5,
            only_create_lines=True
        )

        return line

    def construct(self):

        line = self.cover_drive_freq_graph()
        lines = line.lines

        self.play(Write(line))
        self.play(Create(lines))
        self.wait()

class FlickShotFreq(Scene):
    
    @staticmethod
    def flick_freq_graph():

        flick_primary_kw = [
            'flick'
        ]
        flick_search_kw = [
            'tuck',
            'clipped',
            'clip',
            ('pads', 0.3),
            ('pad ', 0.3),
            'on the pads',
            #('leg side', 0.25),
            ('leg', 0.3),
            ('square', 0.19),
            'glance'
            'off the pads',
            'off his pads',
            ('nudge', 0.3),
            ('pick', 0.3),
            ('straight', 0.3),
            #('square leg', 0.25),
            ('whip', 0.4),
            'on the legs',
            ('work', 0.25),
            ('midwicket', 0.3),
            ('on side', 0.25),
            ('across', 0.3)
        ]
        flick_exlude_words = [
            'run out', 'bumper', 'sweep', 'swept',
            'pull', 'drive', 'cover-drive', ('cover', 0.3),
            'bouncer', 'short ball', 'stays back',
            'backfoot', 'top edge',
            'lets one go', 'easy leave', 'leaves the ball', 'padded away',
            ('off side', 0.25), 'cut', 'left alone', ('point', 0.25), ('defend', 0.3), ('push', 0.25)
        ]
        kohli_matches = wsf.get_player_match_list(KOHLI_ID)
        with open(os.path.join(DATA_LOCATION, 'kohli_comms.p'), 'rb') as file:
            kohli_comms = pickle.load(file)
        kohli_innings = af.get_cricket_totals(KOHLI_ID, kohli_matches, _type='bat', by_innings=True, is_object_id=True, from_scorecards=False)
        kohli_flick_shot_comms = af.search_shots_in_comms(kohli_comms, flick_search_kw, flick_exlude_words, flick_primary_kw, threshold=0.49)
        kohli_flick_stats = [af.analyse_batting_inning(inning) for inning in kohli_flick_shot_comms]
        flick_perc_runs = af.fraction_of_total(kohli_flick_stats, kohli_innings, 'runs')
        moving_flick_perc = af.moving_average(flick_perc_runs, window_size=5)

        line = gm.LineGraph(
            x_values=list(range(len(moving_flick_perc))),
            y_values=moving_flick_perc,
            x_length=10,
            y_length=5,
            only_create_lines=True
        )

        return line
    
    def construct(self):
        line = self.flick_freq_graph()

        lines = line.lines
        
        self.play(Write(line))
        self.play(Create(lines))
        self.wait()

class DotBallFreq(Scene):
    
    @staticmethod
    def dot_ball_freq_graph():
        kohli_matches = wsf.get_player_match_list(KOHLI_ID)
        with open(os.path.join(DATA_LOCATION, 'kohli_comms.p'), 'rb') as file:
            kohli_comms = pickle.load(file)
        kohli_innings = af.get_cricket_totals(KOHLI_ID, kohli_matches, _type='bat', by_innings=True, is_object_id=True, from_scorecards=False)
        dot_ball_comms = []

        for i, comms in enumerate(kohli_comms):
            dot_balls = comms[comms.batsmanRuns == 0]

            dot_ball_comms.append(dot_balls)
        dot_ball_stats = [af.analyse_batting_inning(comms) for comms in dot_ball_comms]
        perc_balls_dots = af.fraction_of_total(dot_ball_stats, kohli_innings, 'balls_faced')
        moving_balls_dots_smooth = af.moving_average(perc_balls_dots, window_size=10)

        line = gm.LineGraph(
            x_values=list(range(len(moving_balls_dots_smooth))),
            y_values=moving_balls_dots_smooth,
            x_length=10,
            y_length=5,
            y_range=[0.6,0.9],
            only_create_lines=True
        )

        return line

    def construct(self):
        line = self.dot_ball_freq_graph()
        lines = line.lines

        self.play(Write(line))
        self.play(Create(lines))
        self.wait()

class ShotFrequenciesKohli(Scene):
    def construct(self):
        cd_line = CoverDriveShotFreq().cover_drive_freq_graph()
        flick_line = FlickShotFreq().flick_freq_graph()
        dot_line = DotBallFreq().dot_ball_freq_graph()

        full_graph = gm.LineGraph(
            x_values=cd_line.x_values,
            y_values=[
                dot_line.y_values[0],
                (cd_line.y_values[0], {'dashed':True, 'dashed_ratio':0.3}),
                (flick_line.y_values[0], {'dashed':True}),
                
            ],
            line_colours=[
                "#003f5c",
                "#ff6361",
                "#bc5090",
            ],
            x_length=10,
            y_length=5,
            only_create_lines=True
        )

        all_lines = full_graph.lines

        self.play(Write(full_graph))
        for line in all_lines:
            self.play(Create(line))
        self.wait()

class ScoringRateInInning(Scene):
    pass

class KohliDotBalls(Scene):
    pass

class TopBatsmanForm(Scene):
    pass

if __name__ == "__main__":
    
    # print(kohli_stats)
    # scene = TestMatchScoringRates()
    # scene = KohliBest80Inning()
    # scene = CoverDriveShotFreq()
    # scene = FlickShotFreq()
    # scene = DotBallFreq()
    scene = ShotFrequenciesKohli()
    # scene = Fab4Careers()
    scene.render()

