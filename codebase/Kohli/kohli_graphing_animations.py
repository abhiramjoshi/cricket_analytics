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

#Default background colour to dark
config.background_color = '#FFF1D0'
#Default axes colour to dark
Axes.set_default(color='#0A273B')
BarChart.set_default(bar_colors=['#FAA916', '#FE5F55', '#95BF74', '#7392B7', '#28536B'])


kohli_stats = wsf.get_player_career_stats(KOHLI_ID)
# kohli_totals = af.get_cricket_totals(KOHLI_ID, is_object_id=True)
# root_totals = af.get_cricket_totals(ROOT_PLAYER_ID, is_object_id=True)
# williamson_totals = af.get_cricket_totals(WILLIAMSON_PLAYER_ID, is_object_id=True)
# smith_totals = af.get_cricket_totals(SPD_SMITH_ID, is_object_id=True)

class KohliCareerGraphShift(Scene):
    def construct(self):
        kohli_matches = wsf.get_player_match_list(KOHLI_ID)
        kohli_out_of_form = kohli_matches[84:]

        kohli_career = gm.CareerGraph(KOHLI_ID)
        kohli_out_of_form_career = gm.CareerGraph(KOHLI_ID, match_ids=kohli_out_of_form, x_range=(141, len(kohli_career.running_ave)), numbers_to_include=[150,160,170])

        y_range = kohli_career.bar_axes.axes[1].x_range
        kohli_intermediate_career = gm.CareerGraph(KOHLI_ID, match_ids=kohli_out_of_form, x_range=(141, len(kohli_career.running_ave)), numbers_to_include=[150,160,170], y_range=y_range)
        bad_form_running_ave = kohli_career.running_ave[141:]
        bad_form_recent_form_ave = kohli_career.recent_form_ave[141:]

        x = np.arange(141,len(kohli_career.running_ave))
        bfrfl_i = kohli_intermediate_career.bar_axes.plot_line_graph(x, bad_form_recent_form_ave, line_color=RED, add_vertex_dots=False)
        bfra_i = kohli_intermediate_career.bar_axes.plot_line_graph(x, bad_form_running_ave, line_color=BLUE, add_vertex_dots=False)
        bfrfl = kohli_out_of_form_career.bar_axes.plot_line_graph(x, bad_form_recent_form_ave, line_color=RED, add_vertex_dots=False)
        bfra = kohli_out_of_form_career.bar_axes.plot_line_graph(x, bad_form_running_ave, line_color=BLUE, add_vertex_dots=False)

        kohli_career_numbers = kohli_career.bar_axes.x_axis.submobjects.pop(0)
        kohli_career_bad_numbers = kohli_out_of_form_career.bar_axes.x_axis.submobjects.pop(0)
        kohli_int_numbers = kohli_intermediate_career.bar_axes.x_axis.submobjects.pop(0)

        # self.play(Create(kohli_career.bar_axes))
        self.play(
            Create(kohli_career.bar_axes),
            Create(kohli_career_numbers),
            #Create(kohli_career.grid), 
            Write(kohli_career.not_outs), 
            Write(kohli_career.title)
        )
        for line in kohli_career.average_lines:
            self.play(Create(line))

        self.play(
            Unwrite(kohli_career.not_outs)
        )

        # for line in kohli_career.average_lines:
        #     self.play(Uncreate(line))
        kohli_pre = VGroup(kohli_career.bar_axes, kohli_career.average_lines[0],kohli_career.average_lines[1])
        kohli_post = VGroup(kohli_out_of_form_career.bar_axes, bfra, bfrfl)
        kohli_int = VGroup(kohli_intermediate_career.bar_axes, bfra_i, bfrfl_i)


        # self.play()
        self.play(
            Uncreate(kohli_career_numbers[:-4]),
            Transform(kohli_pre, kohli_int, replace_mobject_with_target_in_scene=True),
            Transform(kohli_career_numbers[-4:], kohli_career_bad_numbers)
        )
        self.play(
            Transform(kohli_int, kohli_post)
        )
        #self.play(FadeTransform(kohli_career.grid, kohli_out_of_form_career.grid))
        
        # for line in [bfra, bfrfl]:
        #     self.play(Create(line))        

        self.wait()

class KohliCareerHighlight(Scene):

    def construct(self):
        kohli_career = gm.CareerGraph(KOHLI_ID)
        kohli_career_bars = kohli_career.bar_axes.bars.copy()
        kohli_career_bars_good = kohli_career.bar_axes.bars.copy()[49:129].set_color_by_gradient('#22b525')
        kohli_career_bars_bad = kohli_career.bar_axes.bars.copy()[141:].set_color_by_gradient('#fc0335')
        kohli_career.bar_axes.axes.z_index = 1
        # self.play(Create(kohli_career.bar_axes))

        ##Need to add the averages in a box

        self.play(
            Create(kohli_career.bar_axes.axes),
            #Create(kohli_career.grid), 
            Write(kohli_career.not_outs), 
            Write(kohli_career.title),
            Create(kohli_career_bars),
        )
        # for line in kohli_career.average_lines:
        #     self.play(Create(line))

        self.play(
            Transform(kohli_career_bars[49:129], kohli_career_bars_good),
            Transform(kohli_career_bars[141:], kohli_career_bars_bad),
        )

        self.wait()

class KohliCareer(Scene):

    def construct(self):
        kohli_career = gm.CareerGraph(KOHLI_ID)
        kohli_career_bars = kohli_career.bar_axes.bars.copy()
        kohli_career.bar_axes.axes.z_index = 1
        # self.play(Create(kohli_career.bar_axes))
        self.play(
            Create(kohli_career.bar_axes.axes),
            #Create(kohli_career.grid), 
            Write(kohli_career.not_outs), 
            Write(kohli_career.title),
            Create(kohli_career_bars),
        )
        for line in kohli_career.average_lines:
            self.play(Create(line))

        self.wait()

class KohliCareerGood(Scene):
    
    @staticmethod
    def get_good_period_career():
        bottom_limit = 49
        top_limit = 129
        kohli_matches = wsf.get_player_match_list(KOHLI_ID)
        kohli_career = gm.CareerGraph(KOHLI_ID)
        kohli_in_form_career = gm.CareerGraph(KOHLI_ID, match_ids=kohli_matches[28:75], x_range=(bottom_limit, top_limit), numbers_to_include=[50, 60, 70, 80, 90, 100, 110,120])
        good_form_running_ave = kohli_career.running_ave[bottom_limit:top_limit]
        good_form_recent_form_ave = kohli_career.recent_form_ave[bottom_limit:top_limit]

        x = np.arange(bottom_limit,top_limit)
        bfrfl = kohli_in_form_career.bar_axes.plot_line_graph(x, good_form_recent_form_ave, line_color='#FE5F55', add_vertex_dots=False)
        bfra = kohli_in_form_career.bar_axes.plot_line_graph(x, good_form_running_ave, line_color='#FAA916', add_vertex_dots=False)
        return kohli_in_form_career, bfrfl, bfra
    
    def construct(self):
        kohli_in_form_career, bfrfl, bfra = self.get_good_period_career()

        self.play(
            Create(kohli_in_form_career.bar_axes),
            #Create(kohli_career.grid), 
            Write(kohli_in_form_career.not_outs), 
            Write(kohli_in_form_career.title)
        )
        for line in [bfra, bfrfl]:
            self.play(Create(line))
        
        self.wait()

class KohliCenturiesGood(Scene):
    
    @staticmethod
    def get_good_centuries():
        #Text.set_default(font='sans-serif')
        kohli_innings = af.get_cricket_totals(KOHLI_ID, _type='bat', by_innings=True, is_object_id=True)
        good_form_innings = kohli_innings[141-36:141]

        good_form_centuries = [inning for inning in good_form_innings if inning['runs'] > 99]

        century_breakdown = {}
        century_dict = {'good_form': good_form_centuries}
        combined_centuries = {}
        for centuries in century_dict:
            home = []
            away = []
            for century in century_dict[centuries]:
                if century['continent'] == 'Asia':
                    if century['ground'] not in [847]:
                        home.append(century)
                    else:
                        away.append(century)
                else:
                    away.append(century)
                
            century_breakdown[f'{centuries}_home']  = len(home)
            century_breakdown[f'{centuries}_away']  = len(away)
            combined_centuries[centuries] = len(home) + len(away)
        
        empty_graph = gm.BarChart(
            values=[0 for x in combined_centuries],
            bar_names=['Total Centuries'],
            x_axis_config={'label_constructor': Text},
            y_axis_config={'label_constructor': Text, 'decimal_number_config':{'num_decimal_places': 0}},
            # label_rotation=(3*PI)/2,
            y_range=[0, 8, 1],
            x_length=10,
            y_length=5
        )

        century_graph_breakdown = gm.BarChart(
            values=[century_breakdown[x] for x in century_breakdown],
            bar_names=['Good Home', 'Good Away'],
            x_axis_config={'label_constructor': Text},
            y_axis_config={'label_constructor': Text, 'decimal_number_config':{'num_decimal_places': 0}},
            # label_rotation=(3*PI)/2,
            y_range=[0, 5, 1],
            x_length=10,
            y_length=5
        )

        return century_graph_breakdown

    def construct(self):
        pass

class KohliGoodFormCareerToCenturies(Scene):
    
    def construct(self):
        kohli_in_form_career, bfrfl, bfra = KohliCareerGood().get_good_period_career()
        century_graph = KohliCenturiesGood().get_good_centuries()
        # kohli_in_form_career_bars = kohli_in_form_career.bar_axes.bars.copy()
        # kohli_in_form_career.bar_axes.bars = None

        self.play(
            Create(kohli_in_form_career.bar_axes),
            #Create(kohli_in_form_career_bars),
            Create(kohli_in_form_career.not_outs),
            Create(kohli_in_form_career.title)
        )

        for line in [bfra, bfrfl]:
            self.play(Create(line))

        self.wait()

        self.play(
            #Uncreate(kohli_in_form_career_bars),
            Transform(kohli_in_form_career.bar_axes, century_graph),
            Uncreate(kohli_in_form_career.not_outs),
            Uncreate(kohli_in_form_career.title),
            Uncreate(bfra), Uncreate(bfrfl)
        )

        self.wait()


class KohliCareerODI(Scene):

    def construct(self):
        kohli_career = gm.CareerGraph(KOHLI_ID, _format='odi')
        kohli_career_bars = kohli_career.bar_axes.bars.copy()
        kohli_career.bar_axes.axes.z_index = 1
        # self.play(Create(kohli_career.bar_axes))
        self.play(
            Create(kohli_career.bar_axes.axes),
            #Create(kohli_career.grid), 
            Write(kohli_career.not_outs), 
            Write(kohli_career.title),
            Create(kohli_career_bars),
        )
        for line in kohli_career.average_lines:
            self.play(Create(line))

        self.wait()

class KohliCareerT20(Scene):

    def construct(self):
        kohli_career = gm.CareerGraph(KOHLI_ID, _format='t20i')
        kohli_career_bars = kohli_career.bar_axes.bars.copy()
        kohli_career.bar_axes.axes.z_index = 1
        # self.play(Create(kohli_career.bar_axes))
        self.play(
            Create(kohli_career.bar_axes.axes),
            #Create(kohli_career.grid), 
            Write(kohli_career.not_outs), 
            Write(kohli_career.title),
            Create(kohli_career_bars),
        )
        for line in kohli_career.average_lines:
            self.play(Create(line))

        self.wait()

        

class Top15Batsman(Scene):

    def __init__(self, renderer=None, camera_class=Camera, always_update_mobjects=False, random_seed=None, skip_animations=False):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        Text.set_default(font='sans-serif')
        with open(os.path.join(DATA_LOCATION, 'best_80_not_cricket_averages_names.json'), 'r') as file:
            self.best_80 = json.load(file)

        self.top_15 = sorted(self.best_80, key=lambda x: x[1], reverse=True)[:15]

    def construct(self):
        null_graph = gm.BarChart(
            values=[0]*15,
            bar_names=[x[0] for x in self.top_15],
            y_range=[50,100, 10],
            bar_colors=[BLUE]*8 + [RED] + [BLUE]*6,
            x_axis_config={'label_constructor': Text, 'font_size':16},
            y_axis_config={'label_constructor': Text, 'font_size':16},
            label_rotation=(3*PI)/2
        )

        bar_graph = gm.BarChart(
            values=[x[1] for x in self.top_15],
            bar_names=[x[0] for x in self.top_15],
            y_range=[50,100, 10],
            bar_colors=[BLUE]*8 + [RED] + [BLUE]*6,
            x_axis_config={'label_constructor': Text, 'font_size':16},
            y_axis_config={'label_constructor': Text, 'font_size':16},
            label_rotation=(3*PI)/2
        )

        bar_graph_no_old = gm.BarChart(
            values=[x[1] for i,x in enumerate(self.top_15) if i not in [0,5,9]],
            bar_names=[x[0].rstrip('(') for i,x in enumerate(self.top_15) if i not in [0,5,9]],
            y_range=[50,70, 4],
            bar_colors=[BLUE]*6 + [RED] + [BLUE]*5,
            x_axis_config={'label_constructor': Text, 'font_size':16},
            y_axis_config={'label_constructor': Text, 'font_size':16},
            label_rotation=(3*PI)/2
        )

        title = Text('Best averages over 80 game stretch', font_size=24)
        title.next_to(bar_graph.axes, UP)
        bar_labels = bar_graph.get_bar_labels(label_constructor=Text, font_size=16)
        bar_labels2 = bar_graph_no_old.get_bar_labels(label_constructor=Text, font_size=16)
        self.play(Create(null_graph), Write(title))
        self.play(Transform(null_graph, bar_graph, replace_mobject_with_target_in_scene=True))
        self.play(Write(bar_labels))
        self.play(Transform(bar_graph, bar_graph_no_old), Transform(bar_labels, bar_labels2))
        self.wait()

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
            line_colours=['#FAA916', '#FE5F55', '#95BF74', '#7392B7'],
            # y_range=[25,75],
            y_length=5,
            x_length=10,
            only_create_lines=True,
        )

        linegraph.axes.set_color('#0A273B')
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
            self.play(Create(line))
            self.wait(1)
        self.play(Write(labels))
        self.wait(2)

class Top15BattsmanBar(Scene):

    def __init__(self, renderer=None, camera_class=Camera, always_update_mobjects=False, random_seed=None, skip_animations=False):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)

        pass

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
            # line_colours=[
            #     "#003f5c",
            #     "#ff6361",
            #     "#bc5090",
            # ],
            x_length=10,
            y_length=5,
            only_create_lines=True
        )

        all_lines = full_graph.lines

        self.play(Write(full_graph))
        for line in all_lines:
            self.play(Create(line))
        self.wait()

class KohliDismissals(Scene):
    def construct(self):
        test_match_list = wsf.get_player_match_list(KOHLI_ID, _format='test')
        kohli_totals = af.get_cricket_totals(int(KOHLI_ID), matches=test_match_list, _type='bat', by_innings=True, is_object_id=True)
        cum_dismissals = af.get_cumulative_dismissals(kohli_totals)
        x = list(range(len(cum_dismissals[list(cum_dismissals.keys())[0]]))) 
        dismissal_graph = gm.LineGraph(
            x_values = x,
            y_values=[cum_dismissals[y] for y in cum_dismissals],
            x_length=10,
            y_length=5,
            only_create_lines=True
        )

        legend = dismissal_graph.get_legend([k.replace('_', ' ') for k in cum_dismissals])
        all_lines = dismissal_graph.lines

        self.play(Write(dismissal_graph))
        for line in all_lines:
            self.play(Create(line))
        self.play(Create(legend))
        self.wait()
    
class KohliCenturiesBreakdown(Scene):
    def construct(self):
        Text.set_default(font='sans-serif')
        kohli_innings = af.get_cricket_totals(KOHLI_ID, _type='bat', by_innings=True, is_object_id=True)
        good_form_innings = kohli_innings[141-36:141]
        bad_form_innings = kohli_innings[141:]

        good_form_centuries = [inning for inning in good_form_innings if inning['runs'] > 99]
        bad_form_centuries = [inning for inning in bad_form_innings if inning['runs'] > 99]

        century_breakdown = {}
        century_dict = {'good_form': good_form_centuries, 'bad_form':bad_form_centuries}
        combined_centuries = {}
        for centuries in century_dict:
            home = []
            away = []
            for century in century_dict[centuries]:
                if century['continent'] == 'Asia':
                    if century['ground'] not in [847]:
                        home.append(century)
                    else:
                        away.append(century)
                else:
                    away.append(century)
                
            century_breakdown[f'{centuries}_home']  = len(home)
            century_breakdown[f'{centuries}_away']  = len(away)
            combined_centuries[centuries] = len(home) + len(away)
        
        empty_graph = gm.BarChart(
            values=[0 for x in combined_centuries],
            bar_names=['Good Form', 'Bad Form'],
            x_axis_config={'label_constructor': Text, 'font_size':16},
            y_axis_config={'label_constructor': Text, 'font_size':16, 'decimal_number_config':{'num_decimal_places': 0}},
            # label_rotation=(3*PI)/2,
            y_range=[0, 8, 1],
            x_length=10,
            y_length=5
        )

        century_graph = gm.BarChart(
            values=[combined_centuries[x] for x in combined_centuries],
            bar_names=['Good Form', 'Bad Form'],
            x_axis_config={'label_constructor': Text, 'font_size':16},
            y_axis_config={'label_constructor': Text, 'font_size':16, 'decimal_number_config':{'num_decimal_places': 0}},
            # label_rotation=(3*PI)/2,
            y_range=[0, 8, 1],
            x_length=10,
            y_length=5
        )

        century_graph_breakdown = gm.BarChart(
            values=[century_breakdown[x] for x in century_breakdown],
            bar_names=['Good Home', 'Good Away', 'Bad Home', 'Bad Away'],
            x_axis_config={'label_constructor': Text, 'font_size':16},
            y_axis_config={'label_constructor': Text, 'font_size':16, 'decimal_number_config':{'num_decimal_places': 0}},
            # label_rotation=(3*PI)/2,
            y_range=[0, 5, 1],
            x_length=10,
            y_length=5
        )

        title = Text('Kohli Centuries', font_size=24)
        title.next_to(century_graph.axes, UP)
        bar_labels = century_graph.get_bar_labels(label_constructor=Text, font_size=16)
        bar_labels2 = century_graph_breakdown.get_bar_labels(label_constructor=Text, font_size=16)
        self.play(Create(empty_graph), Write(title))
        self.play(Transform(empty_graph, century_graph, replace_mobject_with_target_in_scene=True))
        self.play(Write(bar_labels))
        self.play(Transform(century_graph, century_graph_breakdown), Transform(bar_labels, bar_labels2))
        self.wait()

class ScoringRateInInning(Scene):
    def construct(self):
        Text.set_default(font='sans-serif')
        kohli_matches = wsf.get_player_match_list(KOHLI_ID)
        kohli_innings = af.get_player_contributions(KOHLI_ID, matches=kohli_matches, _type='bat', by_innings=True, is_object_id=True)
        pre_average_inning = af.average_innings(kohli_innings[:141])
        post_average_inning = af.average_innings(kohli_innings[141:])
        pre_x = list(range(len(pre_average_inning)))
        post_x = list(range(len(post_average_inning)))

        speed_of_innings = gm.LineGraph(
            x_values=pre_x,
            y_values=[
                pre_average_inning,
                post_average_inning
            ],
            only_create_lines=True,
            x_length=10,
            y_length=5
        )

        self.play(
            Create(speed_of_innings)
        )
        for line in speed_of_innings.lines:
            self.play(Create(line))

        self.wait()
        

class KohliDotBalls(Scene):
    pass

class TopBatsmanForm(Scene):
    pass

class NumberlineTest(Scene):
    def construct(self):
        line1 = NumberLine(
            x_range=[1,10,1],
            length=10,
            include_numbers=True
        )
        line2 = NumberLine(
            x_range=[7,10,1],
            length=10,
            include_numbers=True
        )
        line1.submobjects.pop(1)
        line2.submobjects.pop(1)
        self.play(Create(line1), Create(line1.numbers))
        self.play(Transform(line1, line2))
        self.play(Uncreate(line1.numbers[:6]), Transform(line1.numbers[6:] , line2.numbers, replace_mobject_with_target_in_scene=True))
        self.wait()

class ShiftedAxis(Scene):
    def construct(self):
        kohli_matches = wsf.get_player_match_list(KOHLI_ID)
        kohli_out_of_form = kohli_matches[84:]
        kohli_out_of_form_career = gm.CareerGraph(KOHLI_ID, match_ids=kohli_out_of_form, x_range=(141,173), numbers_to_include=[150,160,170])

        self.add(kohli_out_of_form_career.bar_axes)
        self.add(kohli_out_of_form_career.average_lines[0])

if __name__ == "__main__":
    
    # print(kohli_stats)
    # scene = TestMatchScoringRates()
    # scene = KohliBest80Inning()
    # scene = CoverDriveShotFreq()
    # scene = FlickShotFreq()
    # scene = DotBallFreq()
    # scene = KohliCareer()
    # scene = KohliCareerGood()
    # scene = KohliCareerHighlight()
    # scene = KohliCareerODI()
    # scene = KohliCareerT20()
    # scene = KohliCenturiesBreakdown()
    # scene = ScoringRateInInning()
    # scene = KohliDismissals()
    # scene = Top15Batsman()
    # scene = ShiftedAxis()
    # scene = NumberlineTest()
    # scene = ShotFrequenciesKohli()
    # scene = Fab4Careers()
    scene = KohliGoodFormCareerToCenturies()
    scene.render()

