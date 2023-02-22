from math import isnan
import codebase.graphing_manim as gm
import codebase.analysis_functions as af
import codebase.web_scrape_functions as wsf
import codebase.math_utils as mu
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
Text.set_default(font='Ubuntu')
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
        kohli_career_bars_good = kohli_career.bar_axes.bars.copy()[(141-32):141].set_color_by_gradient('#95BF74')
        kohli_career_bars_bad = kohli_career.bar_axes.bars.copy()[141:].set_color_by_gradient('#FE5F55')
        kohli_career.bar_axes.axes.z_index = 1
        # self.play(Create(kohli_career.bar_axes))
        good_stats = Text("1748 @ 58.26", font_size=20, color='#95BF74').to_edge(RIGHT)
        bad_stats = Text("872 @ 27.25", font_size=20, color='#FE5F55').next_to(good_stats, DOWN)
        ##Need to add the averages in a box

        shifted_matches = wsf.get_player_match_list(KOHLI_ID)[64:]
        kohli_career_shift = gm.CareerGraph(
            KOHLI_ID, 
            match_ids=shifted_matches, 
            x_range=(141-32, len(kohli_career.running_ave)),
            numbers_to_include=[110,120,130,140,150,160,170]
        )
        kohli_career_shift_bars = kohli_career_shift.bar_axes.bars.copy()
        kohli_career_shift_bars_good = kohli_career_shift.bar_axes.bars.copy()[:32].set_color_by_gradient('#95BF74')
        kohli_career_shift_bars_bad = kohli_career_shift.bar_axes.bars.copy()[32:].set_color_by_gradient('#FE5F55')
        kohli_career.bar_axes.axes.z_index = 1

        self.play(
            Create(kohli_career.bar_axes.axes),
            #Create(kohli_career.grid), 
            Write(kohli_career.not_outs), 
            Write(kohli_career.title),
            Create(kohli_career_bars),
            Create(kohli_career.axis_labels)
        )
        # for line in kohli_career.average_lines:
        #     self.play(Create(line))

        self.play(
            Transform(kohli_career_bars[(141-32):141], kohli_career_bars_good, replace_mobject_with_target_in_scene=True),
            Transform(kohli_career_bars[141:], kohli_career_bars_bad, replace_mobject_with_target_in_scene=True),
        )
        self.wait()
        self.play(
            Uncreate(kohli_career_bars),
            Transform(kohli_career.bar_axes.axes, kohli_career_shift.bar_axes.axes),
            Transform(kohli_career.not_outs, kohli_career_shift.not_outs),
            Transform(kohli_career_bars_good, kohli_career_shift_bars_good),
            Transform(kohli_career_bars_bad, kohli_career_shift_bars_bad),
            Create(good_stats),
            Create(bad_stats)
        )

        self.wait(5)

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
            Create(kohli_career.axis_labels)
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
            y_axis_config={'label_constructor': Text, 'decimal_number_config':{'num_decimal_places': 0}, 'font_size':16},
            # label_rotation=(3*PI)/2,
            y_range=[0, 8, 1],
            x_length=10,
            y_length=5
        )

        century_graph_breakdown = gm.BarChart(
            values=[century_breakdown[x] for x in century_breakdown],
            bar_names=['Home Centuries', 'Away Centuries'],
            bar_colors=['#FE5F55'] + ['#7392B7'],
            x_axis_config={'label_constructor': Text},
            y_axis_config={'label_constructor': Text, 'decimal_number_config':{'num_decimal_places': 0}, 'font_size':16},
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
        labels = century_graph.get_bar_labels(label_constructor=Text, font_size=24)
        # kohli_in_form_career_bars = kohli_in_form_career.bar_axes.bars.copy()
        # kohli_in_form_career.bar_axes.bars = None
        title = Text("Kohli Centuries", font_size=36).next_to(century_graph.axes, UP)
        self.play(
            Create(kohli_in_form_career.bar_axes),
            #Create(kohli_in_form_career_bars),
            Create(kohli_in_form_career.not_outs),
            Create(kohli_in_form_career.title)
        )

        for line in [bfra, bfrfl]:
            self.play(Create(line))

        self.wait(4)

        self.play(
            #Uncreate(kohli_in_form_career_bars),
            Transform(kohli_in_form_career.bar_axes, century_graph),
            Uncreate(kohli_in_form_career.not_outs),
            Transform(kohli_in_form_career.title, title),
            Uncreate(bfra), Uncreate(bfrfl),
            Create(labels)
        )

        self.wait()


class KohliCareerODI(Scene):

    def construct(self):
        kohli_career = gm.CareerGraph(KOHLI_ID, _format='odi', numbers_to_include=[50,100,150,200,250])
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

        self.wait(10)

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

    @staticmethod
    def top_15_bats():
        with open(os.path.join(DATA_LOCATION, 'best_80_not_cricket_averages_names.json'), 'r') as file:
            best_80 = json.load(file)

        top_15 = sorted(best_80, key=lambda x: x[1], reverse=True)[:15]

        null_graph = gm.BarChart(
            values=[0]*15,
            bar_names=[x[0][:x[0].index('(')-1] for x in top_15],
            y_range=[50,100, 10],
            bar_colors=['#7392B7']*8 + ['#FE5F55'] + ['#7392B7']*6,
            x_axis_config={'label_constructor': Text, 'font_size':12},
            y_axis_config={'label_constructor': Text, 'font_size':16},
            label_rotation=(3*PI)/2
        )

        bar_graph = gm.BarChart(
            values=[x[1] for x in top_15],
            bar_names=[x[0][:x[0].index('(')-1] for x in top_15],
            y_range=[50,100, 10],
            bar_colors=['#7392B7']*8 + ['#FE5F55'] + ['#7392B7']*6,
            x_axis_config={'label_constructor': Text, 'font_size':12},
            y_axis_config={'label_constructor': Text, 'font_size':16},
            label_rotation=(3*PI)/2
        )

        bar_graph_no_old = gm.BarChart(
            values=[x[1] for i,x in enumerate(top_15) if i not in [0,5,9]],
            bar_names=[x[0][:x[0].index('(')-1] for i,x in enumerate(top_15) if i not in [0,5,9]],
            y_range=[50,70, 4],
            bar_colors=['#7392B7']*6 + ['#FE5F55'] + ['#7392B7']*5,
            x_axis_config={'label_constructor': Text, 'font_size':12},
            y_axis_config={'label_constructor': Text, 'font_size':16},
            label_rotation=(3*PI)/2
        )

        return null_graph, bar_graph, bar_graph_no_old

    def construct(self):
        null_graph, bar_graph, bar_graph_no_old = self.top_15_bats()
        title = Text('Best averages over 80 inning stretch', font_size=24)
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

class Top15BatsToCareerCenturies(Scene):

    def construct(self):
        kohli_in_form_career, bfrfl, bfra = KohliCareerGood().get_good_period_career()
        century_graph = KohliCenturiesGood().get_good_centuries()
        labels = century_graph.get_bar_labels(label_constructor=Text, font_size=24)
        kohli_in_form_career.title = Text("Kohli Best 80 Innings", font_size=36).next_to(kohli_in_form_career.bar_axes.axes, UP)
        # kohli_in_form_career_bars = kohli_in_form_career.bar_axes.bars.copy()
        # kohli_in_form_career.bar_axes.bars = None
        #title = Text("Kohli Centuries", font_size=36).next_to(century_graph.axes, UP)
        
        null_graph, bar_graph, bar_graph_no_old = Top15Batsman().top_15_bats()
        null_graph.x_axis.labels[8].set_color('#FE5F55')
        bar_graph.x_axis.labels[8].set_color('#FE5F55')
        bar_graph_no_old.x_axis.labels[6].set_color('#FE5F55')
        title = Text('Best averages over 80 game stretch', font_size=36)
        title.next_to(bar_graph.axes, UP)
        bar_labels = bar_graph.get_bar_labels(label_constructor=Text, font_size=16)
        bar_labels2 = bar_graph_no_old.get_bar_labels(label_constructor=Text, font_size=16)
        
        x_axis_label = Text("Innings", color='#0A273B', font_size=20).next_to(kohli_in_form_career.bar_axes.axes, DOWN)
        y_axis_label = Text("Runs", color='#0A273B', font_size=20).next_to(kohli_in_form_career.bar_axes.axes, LEFT).rotate(PI/2)
        y_axis_label2 = Text("Centuries", color='#0A273B', font_size=20).next_to(kohli_in_form_career.bar_axes.axes, LEFT).rotate(PI/2)

        self.play(
            Create(kohli_in_form_career.bar_axes),
            #Create(kohli_in_form_career_bars),
            Create(kohli_in_form_career.not_outs),
            Create(kohli_in_form_career.title),
            Create(x_axis_label), Create(y_axis_label)
        )

        for line in [bfra, bfrfl]:
            self.play(Create(line))

        self.wait(2)

        self.play(
            #Uncreate(kohli_in_form_career_bars),
            Transform(kohli_in_form_career.bar_axes, null_graph, replace_mobject_with_target_in_scene=True),
            Uncreate(kohli_in_form_career.not_outs),
            Transform(kohli_in_form_career.title, title, replace_mobject_with_target_in_scene=True),
            Uncreate(bfra), Uncreate(bfrfl), Uncreate(x_axis_label)
        )

        #self.wait()
        
        #self.play(Create(null_graph), Write(title))
        self.play(Transform(null_graph, bar_graph, replace_mobject_with_target_in_scene=True))
        self.play(Write(bar_labels))
        self.play(
            Transform(bar_graph, bar_graph_no_old, replace_mobject_with_target_in_scene=True), 
            Transform(bar_labels, bar_labels2, replace_mobject_with_target_in_scene=True)
        )
        self.wait(4)
        title2 = Text('Kohli Centuries 2017-2019', font_size=36)
        title2.next_to(bar_graph.axes, UP)
        self.play(
            Transform(bar_labels2, labels),
            Transform(bar_graph_no_old, century_graph),
            Transform(title, title2),
            Transform(y_axis_label, y_axis_label2)
        )
        self.wait(4)


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
        #Text.set_default(font_size=12)
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
            x_axis_config = {'label_constructor': Text, 'font_size':20},
            y_axis_config = {'label_constructor': Text, 'font_size':20},
            x_range=[0,110],
            y_range=[0, 0.8],
            dot_radius=0.05,
            coord_colours=['#7392B7']
        )
        x_axis_label = Text("Batting Average", color='#0A273B', font_size=20).next_to(scatter.axes, DOWN)
        y_axis_label = Text("Win Percentage", color='#0A273B', font_size=20).next_to(scatter.axes, LEFT).rotate(PI/2)
        axis_labels = VGroup(x_axis_label, y_axis_label)
        scatter.sort_coords()
        coords = scatter.get_coords()

        #Get VK point
        vk_point = Dot(scatter.c2p(self.virat_kohli[0], self.virat_kohli[1]), color='#FE5F55')
        vk_text = Text('V Kohli', color="#FE5F55", font_size=20)
        vk_text.next_to(vk_point, UP)
        virat_kohli = VGroup(
            vk_point,
            vk_text
        )
        
        #Get better than VK points:
        better_labels = {key:self.data[key] for key in self.data if self.data[key][0] > self.virat_kohli[0] and self.data[key][1] > self.virat_kohli[1]}
        better_bats = VGroup()
        for bat in better_labels:
            better_bats.add(Dot(scatter.c2p(self.data[bat][0], self.data[bat][1]), color='#95BF74'))
        
        #Create a box that has the list of names 
        def create_name_box(names):
            box = VGroup()
            names_group = VGroup()
            for name in names:
                names_group.add(Text(name, font_size=12))

            names_group.arrange(DOWN, aligned_edge=LEFT)
            
            box_height = names_group.get_top()[1] - names_group.get_bottom()[1] + (2*MED_SMALL_BUFF)
            box_width = names_group.get_right()[0] - names_group.get_left()[0] + (2*MED_SMALL_BUFF)
            box_border = Rectangle(height=box_height, width=box_width, color='#0A273B')
            box.add(names_group)
            box.add(box_border)
            box[0].move_to(box.get_center())

            return box

        better_bat_names = create_name_box(better_labels)
        better_bat_names.to_edge(RIGHT)
        title = Text("Average vs Percentage of Games Won", font_size=36)
        title.next_to(scatter.axes, UP)
        self.play(Write(scatter), Write(title), Create(axis_labels))
        self.play(Write(coords))
        self.play(Write(virat_kohli))
        self.wait()
        self.play(Write(better_bats))
        self.wait()
        self.play(Write(better_bat_names))
        self.wait()
class PercentageRunsCoverDrive(Scene):
    @staticmethod
    def percentage_coverdrives_runs():
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

        line = self.percentage_coverdrives_runs()
        lines = line.lines

        self.play(Write(line))
        self.play(Create(lines))
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
        cover_drive_perc_runs = af.fraction_of_total(kohli_cover_drive_stats, kohli_innings, 'balls_faced')
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
        flick_perc_runs = af.fraction_of_total(kohli_flick_stats, kohli_innings, 'balls_faced')
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

class SinglesFreq(Scene):
    
    @staticmethod
    def singles_freq_graph():
        kohli_matches = wsf.get_player_match_list(KOHLI_ID)
        with open(os.path.join(DATA_LOCATION, 'kohli_comms.p'), 'rb') as file:
            kohli_comms = pickle.load(file)
        kohli_innings = af.get_cricket_totals(KOHLI_ID, kohli_matches, _type='bat', by_innings=True, is_object_id=True, from_scorecards=False)
        singles_comms = []

        for i, comms in enumerate(kohli_comms):
            singles = comms[comms.batsmanRuns == 1]

            singles_comms.append(singles)
        single_stats = [af.analyse_batting_inning(comms) for comms in singles_comms]
        perc_balls_singles = af.fraction_of_total(single_stats, kohli_innings, 'balls_faced')
        moving_singles_smooth = af.moving_average(perc_balls_singles, window_size=10)

        line = gm.LineGraph(
            x_values=list(range(len(moving_singles_smooth))),
            y_values=moving_singles_smooth,
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
        runs_cd = PercentageRunsCoverDrive().percentage_coverdrives_runs()

        full_graph = gm.LineGraph(
            x_values=cd_line.x_values,
            y_values=[
                dot_line.y_values[0],
                cd_line.y_values[0], 
                flick_line.y_values[0],
                runs_cd.y_values[0]      
            ],
            line_colours=[
                '#FE5F55',
                '#28536B',
                '#FAA916',
                '#7392B7'
            ],
            x_length=10,
            y_length=5,
            x_axis_config={'label_constructor': Text, 'font_size':20, 'decimal_number_config':{'num_decimal_places': 0}},
            y_axis_config={'label_constructor': Text, 'font_size':20},
            only_create_lines=True
        )
        labels=full_graph.get_line_labels(
            values=[
                'Dots Freq',
                'Cover Drive Freq',
                'Flicks Freq',
                'Cover Drive Runs'
            ],
            font_size=16
        )
        x_axis_label = Text("Innings", color='#0A273B', font_size=20).next_to(full_graph.axes, DOWN)
        y_axis_label = Text("Shot Freq. (Percentage)", color='#0A273B', font_size=20).rotate(PI/2).next_to(full_graph.axes, LEFT)
        axis_labels = VGroup(x_axis_label, y_axis_label)
        arrow_up = Arrow(start=LEFT, end=RIGHT, color='#FE5F55', max_tip_length_to_length_ratio=0.15)
        arrow_up.rotate(PI/6).shift([3.1, 1.5, 0])
        arrow_down = Arrow(start=LEFT, end=RIGHT, color='#28536B', max_tip_length_to_length_ratio=0.15)
        arrow_down.rotate(-PI/6).shift([3.1, -0.5, 0])
        arrow_down_steep = Arrow(start=LEFT, end=RIGHT, color='#7392B7', max_tip_length_to_length_ratio=0.15)
        arrow_down_steep.rotate(-(2*PI)/6).shift([3.6, -0.2, 0])
        all_lines = full_graph.lines
        all_lines[1].set_z_index(1)
        title = Text("Kohli Shot Frequencies", font_size=36)
        title.next_to(full_graph.axes, UP)
        self.play(Write(full_graph), Create(title), Create(axis_labels))
        self.play(Create(all_lines[0]))
        self.wait(3)
        self.play(Create(arrow_up))
        for line in [all_lines[1],all_lines[2]]:
            self.play(Create(line))
        self.play(Create(labels[:3]))
        self.play(Create(arrow_down))
        self.wait()
        self.play(Uncreate(labels[0]), Uncreate(labels[2]))
        self.play(Uncreate(arrow_up))
        for line in [all_lines[0],all_lines[2]]:
            self.play(Uncreate(line))
        self.play(Uncreate(arrow_down))
        self.play(Create(all_lines[3]), Create(arrow_down_steep))
        self.play(Create(labels[3]))
        self.wait()

class CoverDriveFreqAndRuns_F(Scene):
    def construct(self):
        cd_line = CoverDriveShotFreq().cover_drive_freq_graph()
        runs_cd = PercentageRunsCoverDrive().percentage_coverdrives_runs()

        full_graph = gm.LineGraph(
            x_values=cd_line.x_values,
            y_values=[
                cd_line.y_values[0], 
                (runs_cd.y_values[0], {'dashed':True})      
            ],
            line_colours=[
                '#FE5F55',
                '#7392B7',
            ],
            x_length=10,
            y_length=5,
            x_axis_config={'label_constructor': Text, 'font_size':16, 'decimal_number_config':{'num_decimal_places': 0}},
            y_axis_config={'label_constructor': Text, 'font_size':16},
            only_create_lines=True
        )
        labels=full_graph.get_line_labels(
            values=[
                'Cover Drive Freq',
                'Cover Drive Runs'
            ],
            font_size=16
        )
        x_axis_label = Text("Innings", color='#0A273B', font_size=20).next_to(full_graph, DOWN)
        y_axis_label = Text("Percent Shots Played/Runs Per Shot", color='#0A273B', font_size=20).rotate(PI/2).next_to(full_graph.axes, LEFT)
        #axis_labels = VGroup(x_axis_label, y_axis_label)
        all_lines = full_graph.lines
        all_lines[1].set_z_index(1)
        highlight_line = Line(LEFT, RIGHT, color='#FE5F55').shift([4.1, -1.5, 0])
        title = Text("Coverdrive Freq and Scoring", font_size=36)
        title.next_to(full_graph.axes, UP)
        self.play(Write(full_graph), Create(title), Create(x_axis_label), Create(y_axis_label))
        self.play(Create(all_lines[0]))
        self.play(Create(labels[0]))
        self.wait(2)
        self.play(Create(highlight_line))
        self.wait(10)
        self.play(Uncreate(highlight_line), Create(all_lines[1]))
        self.play(Create(labels[1]))
        self.wait(5)

class SinglesVsDotsFreq(Scene):
    def construct(self):
        singles_line = SinglesFreq.singles_freq_graph()
        dots_line = DotBallFreq().dot_ball_freq_graph()

        full_graph = gm.LineGraph(
            x_values=singles_line.x_values,
            y_values=[
                singles_line.y_values[0], 
                dots_line.y_values[0],      
            ],
            # line_colours=[
            #     '#FE5F55',
            #     '#7392B7',
            # ],
            x_length=10,
            y_length=5,
            x_axis_config={'label_constructor': Text, 'font_size':20, 'decimal_number_config':{'num_decimal_places': 0}},
            y_axis_config={'label_constructor': Text, 'font_size':20},
            only_create_lines=True
        )
        labels=full_graph.get_line_labels(
            values=[
                'Singles',
                'Dots'
            ]
        )
        x_axis_label = Text("Innings", color='#0A273B', font_size=20).next_to(full_graph.axes, DOWN)
        y_axis_label = Text("Shot Freq. (Percentage)", color='#0A273B', font_size=20).rotate(PI/2).next_to(full_graph.axes, LEFT)
        axis_labels = VGroup(x_axis_label, y_axis_label)
        all_lines = full_graph.lines
        all_lines[1].set_z_index(1)
        title = Text("Singles and Dots Frequency", font_size=36)
        title.next_to(full_graph.axes, UP)
        self.play(Write(full_graph), Create(title), Create(axis_labels))
        self.play(Create(all_lines[0]))
        self.play(Create(all_lines[1]))
        self.play(Create(labels))
        self.wait(8)

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

class RootScoringInnings(Scene):
    @staticmethod
    def root_inning_scoring_rate():
        root_matches = wsf.get_player_match_list(303669)
        root_innings = af.get_player_contributions(303669, matches=root_matches, _type='bat', by_innings=True, is_object_id=True)
        average_inning = af.average_innings(root_innings)
        x = list(range(len(average_inning)))

        speed_of_innings = gm.LineGraph(
            x_values=x,
            y_values=[
                average_inning,
            ],
            only_create_lines=True,
            x_length=10,
            y_length=5
        )

        return speed_of_innings

class StokesScoringInnings(Scene):
    @staticmethod
    def stokes_inning_scoring_rate():
        stokes_matches = wsf.get_player_match_list(311158)
        stokes_innings = af.get_player_contributions(311158, matches=stokes_matches, _type='bat', by_innings=True, is_object_id=True)
        average_inning = af.average_innings(stokes_innings)
        x = list(range(len(average_inning)))

        speed_of_innings = gm.LineGraph(
            x_values=x,
            y_values=[
                average_inning,
            ],
            only_create_lines=True,
            x_length=10,
            y_length=5
        )

        return speed_of_innings

class KohliScoringInnings(Scene):
    @staticmethod
    def kohli_inning_scoring_rate():
        kohli_matches = wsf.get_player_match_list(KOHLI_ID)
        kohli_innings = af.get_player_contributions(KOHLI_ID, matches=kohli_matches, _type='bat', by_innings=True, is_object_id=True)
        pre_average_inning = af.average_innings(kohli_innings[:141])
        post_average_inning = af.average_innings(kohli_innings[141:])
        pre_x = list(range(len(pre_average_inning)))
        post_x = list(range(len(post_average_inning)))
        sixty_sr = [x*0.6 for x in pre_x]
        speed_of_innings = gm.LineGraph(
            x_values=pre_x,
            y_values=[
                pre_average_inning,
                post_average_inning,
                (sixty_sr, {'dashed':True, 'dashed_ratio':0.5, 'dash_length':1})
            ],
            line_colours=[
                '#95BF74',
                '#FAA916',
                '#7392B7'
            ],
            x_axis_config={'label_constructor': Text, 'font_size':20, 'decimal_number_config':{'num_decimal_places': 0}},
            y_axis_config={'label_constructor': Text, 'font_size':20},
            only_create_lines=True,
            x_length=10,
            y_length=5
        )

        return speed_of_innings

    def construct(self):
        speed_of_innings = self.kohli_inning_scoring_rate()
        title = Text("Kohli Average Innings", font_size=36).next_to(speed_of_innings.axes, UP)
        legend = speed_of_innings.get_legend(
            values=[
                'Kohli in-form',
                'Kohli OoF',
                'SR 60'
            ]
        )
        self.play(
            Create(speed_of_innings),
            Create(title)
        )
        for line in speed_of_innings.lines:
            self.play(Create(line))
        self.play(Create(legend))
        self.wait()

class ScoringRateInInning_F(Scene):
    def construct(self):
        kohli = KohliScoringInnings().kohli_inning_scoring_rate()
        root = RootScoringInnings().root_inning_scoring_rate()
        stokes = StokesScoringInnings().stokes_inning_scoring_rate()
        x = list(range(max([len(l) for l in [kohli.y_values[0], root.y_values[0], stokes.y_values[0]]])))
        speed_of_innings2 = gm.LineGraph(
            x_values=x,
            y_values=[
                root.y_values[0],
                stokes.y_values[0]
            ],
            x_length=10,
            y_length=5,
            x_axis_config={'label_constructor': Text, 'font_size':20, 'decimal_number_config':{'num_decimal_places': 0}},
            y_axis_config={'label_constructor': Text, 'font_size':20},
            only_create_lines=True
        )
        speed_of_innings3 = gm.LineGraph(
            x_values=x,
            y_values=[
                root.y_values[0],
                stokes.y_values[0],
                kohli.y_values[0]
            ],
            line_colours=[
                '#FE5F55',
                '#28536B',
                '#95BF74',
            ],
            x_length=10,
            y_length=5,
            x_axis_config={'label_constructor': Text, 'font_size':20, 'decimal_number_config':{'num_decimal_places': 0}},
            y_axis_config={'label_constructor': Text, 'font_size':20},
            only_create_lines=True
        )
        speed_of_innings = gm.LineGraph(
            x_values=x,
            y_values=[
                root.y_values[0],
                stokes.y_values[0],
                kohli.y_values[0],
                kohli.y_values[1]
            ],
            line_colours=[
                '#FE5F55',
                '#28536B',
                '#95BF74',
                '#FAA916'
            ],
            x_length=10,
            y_length=5,
            x_axis_config={'label_constructor': Text, 'font_size':20, 'decimal_number_config':{'num_decimal_places': 0}},
            y_axis_config={'label_constructor': Text, 'font_size':20},
            only_create_lines=True
        )
        x_axis_label = Text("Balls", color='#0A273B', font_size=20).next_to(speed_of_innings.axes, DOWN)
        y_axis_label = Text("Runs", color='#0A273B', font_size=20).rotate(PI/2).next_to(speed_of_innings.axes, LEFT)
        axis_labels = VGroup(x_axis_label, y_axis_label)
        title2 = Text("Kohli Average Innings", font_size=36).next_to(kohli.axes, UP)
        title = Text("Average Innings", font_size=36)
        title.next_to(speed_of_innings.axes, UP)
        legend_small = speed_of_innings2.get_legend(
            values=[
                'Root',
                'Stokes'
            ],
            font_size=16
        )
        legend_3 = speed_of_innings3.get_legend(
            values=[
                'Root',
                'Stokes',
                'Kohli'
            ],
            font_size=16
        )
        legend = speed_of_innings.get_legend(
            values=[
                'Root',
                'Stokes',
                'Kohli in-form',
                'Kohli OoF'
            ],
            font_size=16
        )
        legend_kohli = kohli.get_legend(
            values=[
                'Kohli in-form',
                'Kohli OoF',
                '60 SR'
            ],
            font_size=16
        )
        legend_kohli.to_edge(RIGHT)
        legend_small.to_edge(RIGHT)
        legend_3.to_edge(RIGHT)
        legend.to_edge(RIGHT)
        all_lines = speed_of_innings.lines
        self.play(Create(speed_of_innings), Create(title), Create(axis_labels))
        self.wait(5)
        for line in all_lines[:2]:
            self.play(Create(line))
        self.play(Create(legend_small))
        self.wait(5)
        for line in all_lines[2]:
            self.play(Create(line))
        self.play(Transform(legend_small ,legend_3, replace_mobject_with_target_in_scene=True))
        self.wait(5)
        
        for line in all_lines[3]:
            self.play(Create(line))

        self.play(Transform(legend_3 ,legend, replace_mobject_with_target_in_scene=True))
        self.wait(5)
        for line in all_lines[:2]:
            self.play(Uncreate(line))
        self.play(
            Create(kohli.lines[2]),
            Transform(speed_of_innings, kohli),
            Transform(title, title2),
            Transform(legend, legend_kohli)
        )
        self.wait(5)

class KohliCoverDriveControl(Scene):
    
    @staticmethod
    def cover_drive_control():

        match_set = {
            '2011-2013':wsf.get_player_match_list(KOHLI_ID, '2011-01-01:2013-12-31'),
            '2014-2016':wsf.get_player_match_list(KOHLI_ID, '2014-01-01:2016-12-31'),
            '2016-2019':wsf.get_player_match_list(KOHLI_ID, '2017-01-01:2019-12-31'),
            '2020-NOW':wsf.get_player_match_list(KOHLI_ID, '2020-01-01:'),
        }

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

        cover_drive_beat_primary = [
            'beaten'
        ]
        cover_drive_beat_search = [
            'edged',
            ('wicket', 0.25),
            ('edge', 0.25),
            ('miss', 0.25),
            'beats[\s]{0,1}[\s\w\'\-\,]{0,}(?:edge|kohli|batsman|drive)',
            'beat[\s]{0,1}[\s\w\'\-\,]{0,}(?:edge|kohli|batsman|drive)',
            'beating[\s]{0,1}[\s\w\'\-\,]{0,}(?:edge|drive|shot)',
            ('beat him', 0.25),
            'beats him',
            'attempt[\s\w\'\-\,]{0,}(?:drive)',
            '(?:get|find|take|grazing|kiss|got)[\s]{0,1}[\s\w\'\-\,]{0,}(?:edge)',
            'edge[\s]{0,1}[\s\w\'\-\,]{0,}(?:slip|gully)',
            ('loose shot', 0.25),
            ('drop', 0.25),
            ('slip', 0.25),
            ('(?:push|drive)[\s]{0,1}[\s\w\'\-\,]{0,}away[\s]{0,1}[\s\w\'\-\,]{0,}body', 0.25),
            '(?:catch|caught)[\s\w\'\-\,]{0,}(?:slip|gully)'
            #outside edge, inside edge
        ]
        cover_drive_beat_exclude = [
            'nicely', 
            ('beats[\s]{0,1}[\s\w]{0,} (?:fielder|bowler|man|cover|point)'),
            'top shot'
        ]

        beaten = {}
        wickets = {}
        for matches in match_set:
            comms = af.get_player_contributions(KOHLI_ID, match_set[matches], 'bat', True, True)
            cover_drives = af.search_shots_in_comms(comms, cover_drive_search_kw, cover_drive_exlude_words, primary_keywords=cover_drive_primary_kw, threshold=0.49)
            cover_drives_beaten = af.search_shots_in_comms(cover_drives, cover_drive_beat_search, cover_drive_beat_exclude, cover_drive_beat_primary, threshold=0.49)
            
            cover_drives_wickets = []
            for inning in cover_drives:
                cover_drives_wickets += inning[inning.isWicket==True].commentTextItems.to_list()

            cover_drives_beaten_flat = []
            for inning in cover_drives_beaten:
                cover_drives_beaten_flat += inning.commentTextItems.to_list()

            cover_drives_flat = []
            for inning in cover_drives:
                cover_drives_flat += inning.commentTextItems.to_list()

            cover_drives_beaten_flat += [x for x in cover_drives_wickets if x not in cover_drives_beaten_flat]
            
            period_length = len(cover_drives_flat)

            beaten[matches] = len(cover_drives_beaten_flat)/period_length
            wickets[matches] = len(cover_drives_wickets)/period_length

        return beaten, wickets

    def construct(self):
        beaten, wickets = self.cover_drive_control()
        linegraph = gm.LineGraph(
            x_values = [1,2,3,4],
            y_values=[
                [beaten[year]*100 for year in beaten],
                ([wickets[year]*100 for year in wickets], {'dashed':True})
            ],
            x_length=10,
            y_length=5,
            x_range=[0,5,1],
            x_axis_config={'label_constructor': Text, 'font_size':20, 'numbers_to_exclude':[1,2,3,4,5], 'decimal_number_config':{'num_decimal_places': 0}},
            only_create_lines=True,
            
        )
        period_1 = Text("2011-13", font_size=20).shift([-3.1,-3, 0])
        period_2 = Text("2014-16", font_size=20).shift([-1,-3, 0])
        period_3 = Text("2017-19", font_size=20).shift([1,-3, 0])
        period_4 = Text("2019-Now", font_size=20).shift([3.1,-3, 0])
        title = Text("Kohli Cover Drive Control").next_to(linegraph.axes, UP)
        #x_axis_label = Text("Innings", color='#0A273B', font_size=20).next_to(linegraph.axes, DOWN)
        y_axis_label = Text("Control/Wickets Percentage", color='#0A273B', font_size=20).rotate(PI/2).next_to(linegraph.axes, LEFT)
        axis_labels = VGroup(y_axis_label)
        self.play(
            Create(linegraph),
            Create(title),
            Create(axis_labels),
            Create(period_1),
            Create(period_2),
            Create(period_3),
            Create(period_4),
        )
        
        for line in linegraph.lines:
            self.play(Create(line))

        labels = linegraph.get_line_labels(
            values=['beaten percentage', 'wickets percentage'],
            font_size=20
        )
        self.play(Create(labels))
        self.wait(4)
        return 


class KohliCoverWicketPercentage(Scene):
    def construct(self):
        wicket_bars_none = gm.BarChart(
            values=[0,0,0,0],
            bar_names=[
                '2011-13',
                '2014-16',
                '2016-18',
                '2019-Now'
            ],
            y_range=[0, 0.5, 0.1],
            x_length=10,
            y_length=5,
            x_axis_config= {'label_constructor':Text, 'font_size':20},
            y_axis_config= {'label_constructor':Text, 'font_size':20},
            bar_colors=[
                '#7392B7', '#95BF74', '#28536B', '#FE5F55'
            ]
        )

        wicket_bars = gm.BarChart(
            values=[0.257, 0.333, 0.255, 0.38],
            bar_names=[
                '2011-13',
                '2014-16',
                '2016-18',
                '2019-Now'
            ],
            y_range=[0, 0.5, 0.1],
            x_length=10,
            y_length=5,
            x_axis_config= {'label_constructor':Text, 'font_size':20},
            y_axis_config= {'label_constructor':Text, 'font_size':20},
            bar_colors=[
                '#7392B7', '#95BF74', '#28536B', '#FE5F55'
            ]
        )
        #x_axis_label = Text("Innings", color='#0A273B', font_size=20).next_to(wicket_bars.axes, DOWN)
        y_axis_label = Text("Wickets Percentage", color='#0A273B', font_size=20).rotate(PI/2).next_to(wicket_bars.axes, LEFT)
        axis_labels = VGroup(y_axis_label)
        labels = wicket_bars.get_bar_labels(
            values=[9, 17, 12, 14],
            label_constructor=Text,
            color='#0A273B'
        )
        title = Text("Kohli Percentage of Wickets off Cover Drives", font_size=36).next_to(wicket_bars.axes, UP)
        self.play(
            Create(wicket_bars_none),
            Create(title), Create(axis_labels)
        ),
        self.play(
            Transform(wicket_bars_none, wicket_bars),
        )
        self.play(Create(labels))
        self.wait()

class CareersAndDismissals():

    def __init__(self, player_id) -> None:
        self.player_id = player_id
        self.test_match_list = wsf.get_player_match_list(self.player_id, _format='test')
        self.totals = af.get_cricket_totals(int(self.player_id), matches=self.test_match_list, _type='bat', by_innings=True, is_object_id=True)
        self.cum_dismissals = af.get_cumulative_dismissals(self.totals)
        self.cum_dismissals = {key:self.cum_dismissals[key] for key in self.cum_dismissals if key in ['caught', 'bowled', 'lbw']}
        self.career_graph = self.get_career_graph()
        self.dismissals, self.dismissals_legend, self.dismissals_labels = self.get_dismissals()
        self.dismissal_freq, self.dismissal_freq_legend, self.dismissal_freq_labels = self.get_dismissal_freq()

    def get_career_graph(self):
        career_graph = gm.CareerGraph(self.player_id)
        return career_graph

    def get_dismissals(self):
        x = list(range(len(self.cum_dismissals[list(self.cum_dismissals.keys())[0]]))) 
        dismissal_graph = gm.LineGraph(
            x_values = x,
            y_values=[self.cum_dismissals[y] for y in self.cum_dismissals],
            x_length=10,
            y_length=2.5,
            x_axis_config = {'decimal_number_config':{'num_decimal_places': 0}}
            #only_create_lines=True
        )

        labels = dismissal_graph.get_line_labels([k.replace('_', ' ') for k in self.cum_dismissals], font_size=20)
        legend = dismissal_graph.get_legend([k.replace('_', ' ') for k in self.cum_dismissals])
        return dismissal_graph, legend, labels

    def get_dismissal_freq(self):
        diff_cum_dismissals = {key:mu.first_difference(mu.clusterize(self.cum_dismissals[key], bin_size=5)) for key in self.cum_dismissals}
        diff_cum_dismissals = {key:list(diff_cum_dismissals[key]) for key in diff_cum_dismissals}
        x = list(range(len(diff_cum_dismissals[list(diff_cum_dismissals.keys())[0]])))
        dismissal_freq_graph = gm.LineGraph(
            x_values = x,
            y_values=[diff_cum_dismissals[y] for y in diff_cum_dismissals],
            x_length=10,
            y_length=2.5,
            x_axis_config = {'decimal_number_config':{'num_decimal_places': 0}}
            #only_create_lines=True
        )

        labels = dismissal_freq_graph.get_line_labels([k.replace('_', ' ') for k in self.cum_dismissals], font_size=20)
        legend = dismissal_freq_graph.get_legend([k.replace('_', ' ') for k in diff_cum_dismissals])
        return dismissal_freq_graph, legend, labels

class SehwagCareer(Scene):
    def construct(self):
        sehwag = CareersAndDismissals(35263)
        self.play(
            Create(sehwag.career_graph.bar_axes),
            #Create(kohli_career.grid), 
            Write(sehwag.career_graph.not_outs), 
            Write(sehwag.career_graph.title),
        )
        for line in sehwag.career_graph.average_lines:
            self.play(Create(line))
        self.play(
            Uncreate(sehwag.career_graph.not_outs),
        )
        self.play(Transform(sehwag.career_graph.bar_axes, sehwag.dismissals, replace_mobject_with_target_in_scene=True))
        
        for line in sehwag.career_graph.average_lines:
            self.play(Uncreate(line))

        for line in sehwag.dismissals.lines:
            self.play(Create(line))
            
        sehwag.dismissals_legend.to_edge(RIGHT)
        self.play(Create(sehwag.dismissals_legend))
        self.play(Transform(sehwag.dismissals, sehwag.dismissal_freq))
        for line in sehwag.dismissals.lines:
            self.play(Uncreate(line))
        for line in sehwag.dismissal_freq.lines:
            self.play(Create(line))
        sehwag.dismissal_freq_legend.to_edge(RIGHT)
        self.play(Transform(
            sehwag.dismissals_legend,
            sehwag.dismissal_freq_legend
        ))

class SehwagBellCareers(Scene):
    def construct(self):
        sehwag = CareersAndDismissals(35263)
        bell = CareersAndDismissals(9062)

        sehwag_recent_form = [x if x < 150 else 150 for x in sehwag.career_graph.recent_form_ave ]
        sehwag_running_ave = [x if x < 150 else 150 for x in sehwag.career_graph.running_ave]
        bell_recent_form = [x if x < 150 else 150 for x in bell.career_graph.recent_form_ave]
        bell_running_ave = [x if x < 150 else 150 for x in bell.career_graph.running_ave]

        x_sw = list(range(max([len(x) for x in [
            sehwag_running_ave,
            sehwag_recent_form,
        ]])))
        x_bell = list(range(max([len(x) for x in [
            bell_recent_form,
            bell_running_ave
        ]])))
        #Sehwag and bell career graph
        career_sw = gm.LineGraph(
            x_values=x_sw,
            y_values=[
                sehwag_running_ave,
                sehwag_recent_form,
            ],
            y_length=2.5,
            x_length=10,
            x_axis_config = {'label_constructor': Text, 'font_size':20},
            y_axis_config = {'label_constructor': Text, 'font_size':20}
        )
        career_bell = gm.LineGraph(
            x_values=x_bell,
            y_values=[
                bell_running_ave,
                bell_recent_form
            ],
            y_length=2.5,
            x_length=10,
            x_axis_config = {'label_constructor': Text, 'font_size':20},
            y_axis_config = {'label_constructor': Text, 'font_size':20}
        )
        title = Text("Sehwag vs Bell Careers", font_size=36).to_edge(UP)
        sehwag_label = Text("Sehwag", font_size=20).rotate(PI/2).next_to(career_sw, LEFT).shift(1.65*UP)
        bell_label = Text("Bell", font_size=20).rotate(PI/2).next_to(career_bell, LEFT).shift(1.50*DOWN)
        career_sw.shift(1.55*UP)
        career_bell.shift(1.55*DOWN)
        self.play(Create(title), Create(sehwag_label), Create(bell_label))
        self.play(Create(career_sw), Create(career_bell))
        self.wait(10)
        dismissals_sw = sehwag.dismissals.shift(1.55*UP)
        dismissals_bell = bell.dismissals.shift(1.55*DOWN)
        dismissals_sw_labels = sehwag.dismissals_labels.shift(1.55*UP)
        dismissals_bell_labels = bell.dismissals_labels.shift(1.55*DOWN)
        self.play(
            Transform(career_sw, dismissals_sw, replace_mobject_with_target_in_scene=True),
            Transform(career_bell, dismissals_bell, replace_mobject_with_target_in_scene=True)
        )
        self.play(
            Create(dismissals_sw_labels),
            Create(dismissals_bell_labels)
        )
        self.wait(10)
        self.play(
            Uncreate(dismissals_sw_labels),
            Uncreate(dismissals_bell_labels)
        )
        dismissals_f_sw = sehwag.dismissal_freq.shift(1.55*UP)
        dismissals_f_bell = bell.dismissal_freq.shift(1.55*DOWN)
        dismissals_sw_f_labels = sehwag.dismissal_freq_labels.shift(1.55*UP)
        dismissals_bell_f_labels = bell.dismissal_freq_labels.shift(1.55*DOWN)
        self.play(
            Transform(dismissals_sw, dismissals_f_sw, replace_mobject_with_target_in_scene=True),
            Transform(dismissals_bell, dismissals_f_bell, replace_mobject_with_target_in_scene=True)
        )
        self.play(
            Create(dismissals_sw_f_labels),
            Create(dismissals_bell_f_labels)
        )
        self.wait(10)

class TopCareersCricketersInline(Scene):
    def career_lines_only(self, player_id):
        running_ave = af.get_running_average(player_id)
        recent_ave = af.get_recent_form_average(player_id)
        career_graph = gm.LineGraph(
            x_values=list(range(len(running_ave))),
            y_values=[
                running_ave,
                recent_ave,
            ],
            y_length=3,
            x_length=12,
            x_axis_config = {'label_constructor': Text, 'font_size':20},
            y_axis_config = {'label_constructor': Text, 'font_size':20}
        )
        return career_graph

    def construct(self):
        #config.frame_rate = 60
        
        #square = Square(color=BLACK)
        ponting = self.career_lines_only(7133).shift([0,-2.5,0])
        #kallis = self.career_lines_only(45789).shift([0,-7.1,0])
        lara = self.career_lines_only(52337).shift([0,7.1,0])
        richards = self.career_lines_only(52812).shift([0,-7.1,0])
        #khan = self.career_lines_only(43652).shift([0,11.7,0])
        de_villiers = self.career_lines_only(44936).shift([0,2.5,0])

        def label_c(s, y):
            return Text(s, font_size=16).rotate(PI/2).shift([-7.5, y, 0])
        ponting_l = label_c('Ponting', -2.5)
        #kallis_l = label_c('Kallis', -7.1)
        lara_l = label_c('Lara', 7.1)
        richards_l = label_c('Richards', -7.1)
        #khan_l = label_c('Khan', 11.7)
        de_villiers_l = label_c('De Villiers', 2.5)

        self.play(
            #Create(square),
            Create(ponting),
            #Create(kallis),
            Create(lara),
            Create(richards),
            #Create(khan),
            Create(de_villiers),
            Create(ponting_l),
            #Create(kallis_l),
            Create(lara_l),
            Create(richards_l),
            #Create(khan_l),
            Create(de_villiers_l),
        )
        self.wait(10)

class TopCareersCricketersInlineStill(Scene):
    def career_lines_only(self, player_id):
        running_ave = af.get_running_average(player_id)
        recent_ave = af.get_recent_form_average(player_id)
        career_graph = gm.LineGraph(
            x_values=list(range(len(running_ave))),
            y_values=[
                running_ave,
                recent_ave,
            ],
            y_length=3,
            x_length=12,
            x_axis_config = {'label_constructor': Text, 'font_size':20},
            y_axis_config = {'label_constructor': Text, 'font_size':20}
        )
        return career_graph

    def construct(self):
        #config.frame_rate = 60
        
        #square = Square(color=BLACK)
        ponting = self.career_lines_only(7133).shift([0,-2.5,0])
        #kallis = self.career_lines_only(45789).shift([0,-7.1,0])
        lara = self.career_lines_only(52337).shift([0,7.1,0])
        richards = self.career_lines_only(52812).shift([0,-7.1,0])
        #khan = self.career_lines_only(43652).shift([0,11.7,0])
        de_villiers = self.career_lines_only(44936).shift([0,2.5,0])

        def label_c(s, y):
            return Text(s, font_size=16).rotate(PI/2).shift([-7.5, y, 0])
        ponting_l = label_c('Ponting', -2.5)
        #kallis_l = label_c('Kallis', -7.1)
        lara_l = label_c('Lara', 7.1)
        richards_l = label_c('Richards', -7.1)
        #khan_l = label_c('Khan', 11.7)
        de_villiers_l = label_c('De Villiers', 2.5)

        self.add(
            ponting,
            lara,
            richards,
            de_villiers,
            ponting_l,
            lara_l,
            richards_l,
            de_villiers_l
        )

class TopCareersCricketers(Scene):
    def career_lines_only(self, player_id):
        running_ave = af.get_running_average(player_id)
        recent_ave = af.get_recent_form_average(player_id)
        career_graph = gm.LineGraph(
            x_values=list(range(len(running_ave))),
            y_values=[
                running_ave,
                recent_ave,
            ],
            y_length=1.7,
            x_length=4.5,
            x_axis_config = {'label_constructor': Text, 'font_size':20},
            y_axis_config = {'label_constructor': Text, 'font_size':20}
        )
        return career_graph

    def construct(self):
        ponting = self.career_lines_only(7133).shift([-3.2,-2.2,0])
        kallis = self.career_lines_only(45789).shift([-3.2,0,0])
        lara = self.career_lines_only(52337).shift([-3.2,2.2,0])
        richards = self.career_lines_only(52812).shift([3.2,-2.2,0])
        khan = self.career_lines_only(43652).shift([3.2,0,0])
        de_villiers = self.career_lines_only(44936).shift([3.2,2.2,0])

        self.play(
            Create(ponting),
            Create(kallis),
            Create(lara),
            Create(richards),
            Create(khan),
            Create(de_villiers)
        )
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
    
    # config.pixel_width = 2560
    # config.pixel_height = 3320
    # config.frame_width = 16
    # config.frame_height = 27
    # print(kohli_stats)
    # scene = TestMatchScoringRates()
    # scene = KohliBest80Inning()
    # scene = CoverDriveShotFreq()
    # scene = FlickShotFreq()
    # scene = DotBallFreq()
    # scene = KohliCareer()
    # scene = KohliCareerGood()
    # scene = KohliCareerHighlight()
    # scene = KohliCareerGraphShift()
    # scene = KohliCareerODI()
    # scene = KohliCareerT20()
    # scene = KohliCenturiesBreakdown()
    # scene = KohliScoringInnings()
    # scene = SinglesVsDotsFreq()
    # scene = SehwagCareer()
    # scene = SehwagBellCareers()
    # scene = TopCareersCricketersInlineStill()
    # scene = ScoringRateInInning_F()
    # scene = KohliDismissals()
    # scene = Top15Batsman()
    # scene = ShiftedAxis()
    # scene = NumberlineTest()
    # scene = ShotFrequenciesKohli()
    # scene = CoverDriveFreqAndRuns_F()
    # scene = PercentageRunsCoverDrive()
    # scene = Fab4Careers()
    # scene = KohliGoodFormCareerToCenturies()
    # scene = KohliCoverDriveControl()
    # scene = Top15BatsToCareerCenturies()
    scene = KohliCoverWicketPercentage()
    scene.render()

