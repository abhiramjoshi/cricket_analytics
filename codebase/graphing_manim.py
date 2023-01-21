from logging import logMultiprocessing
from telnetlib import DO
from manim import *
import codebase.analysis_functions as af
import codebase.web_scrape_functions as wsf
import pandas as pd
from typing import Iterable, MutableSequence, Sequence
config.quality = 'low_quality'

class CareerGraph(Scene):
    def __init__(self, player_id, renderer=None, camera_class=Camera, always_update_mobjects=False, random_seed=None, skip_animations=False,
                _format = 'test', _type='bat', player_age=None, dates=None, window_size=10, match_ids=None, x_range=None, y_range=None, numbers_to_include=None):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        
        if player_age:
            self.dates = af.dates_from_age(player_id, player_age)
        else:
            self.dates = dates
        
        self.player_id = player_id
        self.player_name = wsf.get_player_json(self.player_id)["name"]
        self.type = _type
        self.format = _format
        if match_ids:
            self.matchlist = match_ids
        else:
            self.matchlist = wsf.get_player_match_list(player_id, dates=self.dates, _format=self.format)
        self.innings = af.get_cricket_totals(self.player_id, self.matchlist, _type=self.type, by_innings=True, is_object_id=True)
        self.running_ave = af.get_running_average(self.player_id, self.innings)
        self.recent_form_ave = af.get_recent_form_average(self.player_id, self.innings, window_size=window_size)
        
        self.innings_df = pd.DataFrame(self.innings)
        x = np.arange(len(self.running_ave))
        if x_range is not None and len(x_range) == 3:
            self._x_range = x_range
        elif x_range is not None:
            self._x_range=[x_range[0], x_range[1], (lambda x:x//4 if (x < 50) else 10)(x_range[1])]
        else:
            self._x_range=[0, x[-1]+1, (lambda x:x//4 if (x < 50) else 10)(x[-1])]
        
        if y_range is not None and len(y_range) == 3:
            self._y_range = y_range
        elif y_range is not None:
            self._y_range=[y_range[0], y_range[1], max((y_range[1]//8), 10)]
        else:
            self._y_range=[0, max(self.innings_df.runs)+20, max((max(self.innings_df.runs)//8), 10)]
        
        if numbers_to_include:
            self.numbers_to_include = numbers_to_include
        else:
            self.numbers_to_include = np.arange(self._x_range[0],self._x_range[1], self._x_range[2])

        self.bar_axes = self.get_bars_chart(x_range)
        self.not_outs = self.get_not_outs()
        self.average_lines = self.get_average_lines()
        self.title = self.get_title()
        self.grid = self.make_grid()

    def get_bars_chart(self, x_range=None):
        x = np.arange(len(self.running_ave))
        axes = BarChart(
            values=self.innings_df.runs,
            y_range=(self._y_range[0], self._y_range[1], self._y_range[2]),
            x_range=x_range,
            # x_range=(self._x_range[0], self._x_range[1], self._x_range[2])
            axis_config={"include_numbers": True, 'decimal_number_config':{'num_decimal_places': 0}},
            x_axis_config={
               "numbers_to_include": self.numbers_to_include,
               'include_ticks':False,
               'decimal_number_config':{'num_decimal_places': 0}
            },
            bar_colors=['#003f5c']*len(x)
        )

        return axes

    def get_not_outs(self):
        constr_args = {'radius':self.bar_axes.bars[0].width/4, 'fill_opacity':1, 'no_val':True}
        _not_outs = self.bar_axes.get_bar_labels(color=RED, constr_args=constr_args, label_constructor=Circle, buff=SMALL_BUFF)
        not_outs = VGroup()
        n = [x for i,x in enumerate(_not_outs) if self.innings_df.not_out.iloc[i]]
        for i in n:
            not_outs.add(i)
        return not_outs

    def make_grid(self):
        grid= VGroup()
        for val in np.arange(self._x_range[0]+self._x_range[2],self._x_range[1]+(1*self._x_range[2]), self._x_range[2]):
            grid += self.bar_axes.get_vertical_line(self.bar_axes.c2p(val, self._y_range[1], 0), color=GRAY)
        for val in np.arange(self._y_range[0]+self._y_range[2],self._y_range[1], self._y_range[2]):
            grid += self.bar_axes.get_horizontal_line(self.bar_axes.c2p(self._x_range[1], val, 0), color=GRAY)
        return grid
        
    def get_average_lines(self):
        
        r_a = self.running_ave
        if r_a[0] == None:
            x_r_a = np.arange(self._x_range[0], self._x_range[1])[1:]
            r_a = r_a[1:]        
        else:
            x_r_a = np.arange(self._x_range[0], self._x_range[1])
        
        r_f_a = self.recent_form_ave
        if r_f_a[0] == None:
            x_r_f_a = np.arange(self._x_range[0], self._x_range[1])[1:]
            r_f_a = r_f_a[1:]
        else:
            x_r_f_a = np.arange(self._x_range[0], self._x_range[1])
        
        running_ave = self.bar_axes.plot_line_graph(x_r_a, r_a, add_vertex_dots=False, line_color=BLUE)
        recent_form_ave = self.bar_axes.plot_line_graph(x_r_f_a, r_f_a, add_vertex_dots=False, line_color=RED)
        return [running_ave, recent_form_ave]
        
    def get_title(self):
        title = Text(f"{self.player_name} Career")
        title.next_to(self.bar_axes, UP)
        return title

    # def construct(self):
        
        
        
    #     # axes = Axes(
    #     #     x_range=(_x_range[0], _x_range[1], _x_range[2]),
    #     #     y_range=(_y_range[0], _y_range[1], _y_range[2]),
    #     #     tips=False,
    #     #     axis_config={"include_numbers": True},
    #     #     #x_axis_config={
    #     #     #    "numbers_to_include": np.arange(_x_range[0],_x_range[1], _x_range[2])
    #     #     #},
    #     #     #y_axis_config={
    #     #     #    "numbers_to_include": np.arange(_y_range[0],_y_range[1], _y_range[2])
    #     #     #}
    #     # )
        
    
    #     #Create grid
        

    #     #Additional scence components
        
    #     top_line = axes.plot(lambda x: self._y_range[1], color=WHITE)
    #     area_blank = axes.get_area(top_line, x_range=[23,23], color=YELLOW, opacity=0.2)
    #     area = axes.get_area(top_line, x_range=[23,47], color=YELLOW, opacity=0.2)
        
    #     #Create Animation
    #     self.play(Create(axes), Create(grid), Write(title))
    #     self.play(Create(running_ave), Create(recent_form_ave), Write(not_outs), run_time=1.5)
    #     self.wait(2)
    #     #self.play(Create(area_blank))
    #     #self.play(Transform(area_blank, area))
    #     self.play(Write(area))
    #     self.wait(2)

    #     #self.add(axes, running_ave, recent_form_ave, title, grid)


class BarGraph(Scene):
    def construct(self):
        chart = BarChart(
            values=[100,1500,1860,600,320,2000],
            bar_names=["cover drive", "flick", "pull", "cut", "sweep", "backfoot drive"],
            y_range=[0, 2000, 100],
            y_length=10,
            x_length=20
        )
        chart2 = BarChart(
            values=[0,0,0,0,0,0],
            bar_names=["cover drive", "flick", "pull", "cut", "sweep", "backfoot drive"],
            y_range=[0, 2000, 100],
            y_length=10,
            x_length=20
        )

        chart3 = BarChart(
            values=[100,1500,2000],
            bar_names=["cover drive", "flick", "backfoot drive"],
            y_range=[0, 2000, 100],
            y_length=10,
            x_length=10
        )

        self.play(Write(chart2))
        self.play(Transform(chart2, chart, replace_mobject_with_target_in_scene=True)) #This gets us the animation that we want, of the bars
        self.wait(2)
        self.play(ReplacementTransform(chart, chart3))
        self.wait(3)
    

class LineGraphExample(Scene):
    def construct(self):
        plane = NumberPlane(
            x_range = (0, 300),
            y_range = (0, 200),
            axis_config={"include_numbers": True},
        )
        plane.scale_to_fit_width(10)
        line_graph = plane.plot_line_graph(
            x_values = [0, 1.5, 2, 2.8, 4, 6.25],
            y_values = [1, 3, 2.25, 4, 2.5, 1.75],
            line_color=GOLD_E,
            vertex_dot_style=dict(stroke_width=3,  fill_color=PURPLE),
            stroke_width = 4,
        )
        self.add(plane, line_graph)

class ScatterPlot(Axes):
    def __init__(
        self,
        values: MutableSequence[tuple[float]], 
        coord_names: Sequence[str] | None = None,
        y_range: Sequence[float] | None = None,
        x_range: Sequence[float] | None = None,
        y_length: float | None = None,
        x_length: float | None = None,
        coord_colours: Iterable[str] = [
            "#FFFFFF"
        ],
        dot_radius = DEFAULT_DOT_RADIUS,
        only_create_coords=False,
        **kwargs
    ):
        self.values = values
        self.coord_names = coord_names
        self.coord_colours = coord_colours

        #Setup y-axis
        if y_length is None:
            y_length = min(max(self.values, key=lambda x:x[1])[1], config.frame_width - 2)
        else:
            y_length = y_length

        max_y = abs(max(self.values, key=lambda x:abs(x[1]))[1])
        if min(self.values, key=lambda x:x[1])[1] < 0:
            min_y = -max_y
        else:
            min_y = 0

        if y_range is None:
            y_range = [
                min_y,
                max_y,
                round(max_y / y_length, 2),
            ]

        elif len(y_range) == 2:
            y_range = [*y_range, round(max(self.values, key=lambda x:x[1])[1] / y_length, 2)]
        
        y_axis_config = {"font_size": 24, "label_constructor": Tex}
        self._update_default_configs(
            (y_axis_config,), (kwargs.pop("y_axis_config", None),)
        )

        #Setup x-axis
        if x_length is None:
            x_length = min(max(self.values, key=lambda x:x[0])[0], config.frame_width - 2)
        else:
            x_length = x_length

        max_x = abs(max(self.values, key=lambda x:abs(x[0]))[0])
        if min(self.values, key=lambda x:x[0])[0] < 0:
            min_x = -max_x
        else:
            min_x = 0

        if x_range is None:
            x_range = [
                min_x,
                max_x,
                round(max_x / x_length, 2),
            ]

        elif len(x_range) == 2:
            x_range = [*x_range, round(max(self.values, key=lambda x:x[0])[0] / x_length, 2)]

        x_axis_config = {"font_size": 24, "label_constructor": Tex}
        self._update_default_configs(
            (x_axis_config,), (kwargs.pop("x_axis_config", None),)
        )

        self.dot_radius = dot_radius
        self.coords = VGroup()

        super().__init__(
            x_range=x_range,
            y_range=y_range,
            x_length=x_length,
            y_length=y_length,
            x_axis_config=x_axis_config,
            tips=kwargs.pop("tips", False),
            **kwargs,
        )

        self._add_coords(only_create=only_create_coords)
        self.x_axis.add_numbers()
        self.y_axis.add_numbers()

    def _update_colours(self):
        self.coords.set_color_by_gradient(*self.coord_colours)

    def _create_coord(self, value, i):
        
        if len(self.coord_colours) == len(self.values):
            colour = self.coord_colours[i]
        else:
            colour = self.coord_colours[i % len(self.coord_colours)]
        
        return Dot(self.coords_to_point(value[0], value[1]), radius=self.dot_radius, color=colour)
    
    def _add_coords(self, only_create=False):
        return_group = VGroup()

        for i,c in enumerate(self.values):
            temp_coord = self._create_coord(c, i)
            self.coords.add(temp_coord)
            return_group.add(temp_coord)

        if len(self.coord_colours) == len(self.values):
            self._update_colours()
            return_group.set_color_by_gradient(self.coord_colours)
        
        #self.add_to_back(self.coords)
        if not only_create:
            self.add(self.coords)

        return return_group

    def sort_coords(self):
        """Sorts coords and places them back into self.coords"""
        sorted_coords = VGroup()
        coord_squares = []
        origin = self.c2p(self.x_axis.x_min, self.y_axis.x_min)

        for i,c in enumerate(self.coords):
            normalized_point = c.arc_center-origin
            # We calculate the distance from the origin of all the coords, we will later sort by this distance
            coord_squares.append((np.linalg.norm(normalized_point), i))
        
        coord_squares = sorted(coord_squares, key=lambda x: x[0])

        #Re add all the coords in sorted order, NOTE: c[1] references the original index of the coord
        for c in coord_squares:
            sorted_coords.add(self.coords[c[1]])

        self.coords = sorted_coords

    def get_coords(self):
        return self.coords

    # def add_coords(self, coords):
    #     if isinstance(coords, list):
    #         for cg in self.coords:
    #             self.add(cg)
    #     else:
    #         self.add(self.coords)
   
class LineGraph(Axes):
    
    def __init__(
        self,
        x_values: MutableSequence[list[float]],
        y_values: MutableSequence[list[list[float]]], 
        line_names: Sequence[str] | None = None,
        y_range: Sequence[float] | None = None,
        x_range: Sequence[float] | None = None,
        y_length: float | None = None,
        x_length: float | None = None,
        line_colours: Iterable[str] = [
            "#003f5c",
            "#58508d",
            "#bc5090",
            "#ff6361",
            "#ffa600",
        ],
        only_create_lines=False,
        x_axis_is_years=False,
        **kwargs
    ):
        self.x_values = x_values
        if isinstance(y_values, tuple): #Single tuple
            self.y_values=[y_values]
        elif isinstance(y_values[0], list): #list of lists
            self.y_values=y_values
        elif isinstance(y_values[0], tuple): #list of tuples
            self.y_values=y_values
        else:
            self.y_values = [y_values]

        self.line_names = line_names
        self.line_colours = line_colours
        self.line_config = kwargs.pop("line_config", {})
        self.line_configs = self._handle_line_configs()  

        #Setup y-axis
        temp_y = [[float(y) for y in ylist if y is not None] for ylist in self.y_values]
        max_y = abs(max(max(temp_y, key=lambda x:abs(max(x))), key=lambda x: abs(x)))

        if y_length is None:
            y_length = min(max_y, config.frame_width - 2)
        else:
            y_length = y_length

        if max(max(temp_y, key=lambda x:abs(max(x))), key=lambda x: abs(x)) < 0:
            min_y = -max_y
        else:
            min_y = 0

        if y_range is None:
            y_range = [
                min_y,
                max_y,
                round((max_y - min_y) / y_length, 2),
            ]

        elif len(y_range) == 2:
            y_range = [*y_range, round((y_range[1]-y_range[0]) / y_length, 2)]
        
        y_axis_config = {"font_size": 24, "label_constructor": Tex}
        self._update_default_configs(
            (y_axis_config,), (kwargs.pop("y_axis_config", None),)
        )

        #Setup x-axis
        max_x = abs(max(self.x_values))
        min_x = min(min(x_values), 0)
        if x_length is None:
            x_length = min(max_x, config.frame_width - 2)
        else:
            x_length = x_length

        if x_range is None:
            x_range = [
                min_x,
                max_x,
                round((max_x - min_x) / x_length, 2),
            ]

        elif len(x_range) == 2:
            x_range = [*x_range, round((x_range[1]-x_range[0]) / x_length, 2)]

        decimal_number_config = {}
        if x_axis_is_years:
            decimal_number_config = {'group_with_commas':False, 'num_decimal_places':0}
        x_axis_config = {"font_size": 24, "label_constructor": Tex, 'decimal_number_config':decimal_number_config}
        self._update_default_configs(
            (x_axis_config,), (kwargs.pop("x_axis_config", None),)
        )
      
        self.lines = VGroup()

        super().__init__(
            x_range=x_range,
            y_range=y_range,
            x_length=x_length,
            y_length=y_length,
            x_axis_config=x_axis_config,
            tips=kwargs.pop("tips", False),
            **kwargs,
        )

        self._add_lines(only_create=only_create_lines)
        self.x_axis.add_numbers()
        self.y_axis.add_numbers()

    def _create_line(self, y, i, line_config = {}):
        if len(self.line_colours) == len(self.y_values):
            colour = self.line_colours[i]
        else:
            colour = self.line_colours[i%len(self.line_colours)]  

        add_vertex_dots = self.line_config.pop('add_vertex_dots', False)

        x_values = [x for i,x in enumerate(self.x_values) if y[i] is not None]
        y = [_y for _y in y if _y is not None]
        line = self.plot_line_graph(
            x_values=x_values,
            y_values=y,
            line_color=colour,
            **self.line_config
        )

        vertices = line['vertex_dots']
        line_group = VGroup()
        if line_config.pop('dashed', False):
            line_contructor = DashedLine
        else:
            line_contructor = Line

        for i in range(1, len(vertices)):
            line_group.add(line_contructor(vertices[i-1].get_center(), vertices[i].get_center(), color=colour, **line_config))
        
        if not add_vertex_dots:
            line.remove('vertex_dots')

        line['line_graph'] = line_group

        return line

    def _update_colours(self):
        """Initialize the colors of the lines of the chart.

        Sets the color of ``self.lines`` via ``self.line_colours``.

        Primarily used when the lines are initialized with ``self._add_lines``
        or updated via ``self.change_line_values``.
        """

        self.lines.set_color_by_gradient(*self.line_colours)

    def _add_lines(self, 
    only_create=False):
        return_lines = VGroup()
        
        for i,y in enumerate(self.y_values):
            tmp_line = self._create_line(y, i, self.line_configs[i])
            self.lines.add(tmp_line)
            return_lines.add(tmp_line)

        # if len(self.line_colours) == len(self.y_values):
        #     self._update_colours()         
        #     return_lines.set_color_by_gradient(self.line_colours)

        if not only_create:
            self.add(self.lines)

        return return_lines

    def _handle_line_configs(self):
        configs = []
        global_config = self.line_config
        for i,line in enumerate(self.y_values):
            tmp_config = {}
            if isinstance(line, tuple):
                tmp_config = line[1]
                self.y_values[i] = line[0]
            configs.append({**global_config, **tmp_config})

        return configs
    
    def _get_line_final_value_pos(self, i):
        line = self.y_values[i]
        x = len(line) - 1
        y = line[-1]
        point = self.c2p(x,y)
        return point

    def get_legend(
        self,
        values,
        colour = None,
        font_size = 24,
        buff = MED_SMALL_BUFF,
        label_constructor = Tex,
        pos = RIGHT,
        **kwargs
    ):
        # constr_args = kwargs.get('constr_args', {})
        # if not isinstance(constr_args, list):
        #     constr_args = [constr_args]*len(self.lines)
        # elif len(constr_args) > len(self.lines):
        #     raise Exception('Too many label definitions for number of bars in graph')

        # if len(values) != len(self.lines):
        #     if len(values) < len(self.lines):
        #         values += ['']*(len(self.lines) - len(values))
        #     else:
        #         raise Exception('Too many values provided for number of lines in plot')
        # _values = values
        legend = VGroup()
        labels = self.get_line_labels(values=values, colour=colour)
        labels.arrange(DOWN, aligned_edge=LEFT)
        legend.add(labels)

        lines = VGroup()
        for i,label in enumerate(labels):
            #create a line with the same style as the line on the graph
            line_colour = self.lines[i]['line_graph'][0].color
            line_config = self.line_configs[i]
            if line_config.pop('dashed', False):
                line_contructor = DashedLine
            else:
                line_contructor = Line
            start = self.c2p(0,0)
            end = self.c2p(self.x_range[2]/2,0)
            line = line_contructor(start=start, end=end, color=line_colour, **line_config)
            line.next_to(label, LEFT)
            lines.add(line)
        
        legend.add(lines)

        legend_border_height = legend.get_top()[1] - legend.get_bottom()[1] + (2*MED_SMALL_BUFF)
        legend_border_width = legend.get_right()[0] - legend.get_left()[0] + lines[0].width
        legend_border = Rectangle(height=legend_border_height, width=legend_border_width)
        legend_border.move_to(legend.get_center())
        legend.add(legend_border)
        
        return legend



    def get_line_labels(
        self,
        values,
        colour = None,
        font_size = 24,
        buff = MED_SMALL_BUFF,
        label_constructor = Tex,
        pos = RIGHT,
        **kwargs
    ):
        constr_args = kwargs.get('constr_args', {})
        if not isinstance(constr_args, list):
            constr_args = [constr_args]*len(self.lines)
        elif len(constr_args) > len(self.lines):
            raise Exception('Too many label definitions for number of bars in graph')

        if len(values) != len(self.lines):
            if len(values) < len(self.lines):
                values += ['']*(len(self.lines) - len(values))
            else:
                raise Exception('Too many values provided for number of lines in plot')
        _values = values 

        line_labels = VGroup()
        for i, t in enumerate(zip(self.lines, _values, constr_args)):
            line = t[0] 
            value = t[1] 
            c_args = t[2]
            if c_args.pop('no_val', False):
                line_lbl = label_constructor(**c_args)    
            else:
                line_lbl = label_constructor(str(value), **c_args)

            if colour is None:
                line_lbl.set_color(line.submobjects[0].submobjects[0].get_color())
            else:
                line_lbl.set_color(colour)

            line_lbl.font_size = font_size

            pos = pos
            line_lbl.next_to(self._get_line_final_value_pos(i), pos, buff=buff)
            line_labels.add(line_lbl)

        return line_labels



class ScatterPlotScene(Scene):
    
    def construct(self):
        
        plot = ScatterPlot(
            values=[(1992,100), (1991,200), (1993,500)],
            x_length=10,
            y_length=5,
            y_range=[0,600,100],
            x_range=[1990,1994,1],
            coord_colours=[BLUE, WHITE, RED],
            x_axis_config = {'decimal_number_config':{'group_with_commas':False, 'num_decimal_places':0}},
            only_create_coords=True
        )
        
        plot.sort_coords()
        coords = plot.get_coords()
        # extra_coord = Dot(plot.coords_to_point(1994,600), color=YELLOW)
        self.play(Write(plot))
        self.play(Create(coords))

class LineGraphScene(Scene):

    def construct(self):

        plot = LineGraph(
            x_values=[1,2,3,4,5,8],
            y_values=[[5,6.8,6,9,8,6], ([5,None,None,8,7,4], {'dashed':True})],
            #y_values=([1,2,3,4,5], {'r':True}),
            x_length=10,
            y_length=5,
            only_create_lines=True
        )

        lines = plot.lines
        # plot.add(line)

        self.play(Create(plot))
        for line in lines:
            self.play(Create(line))
            self.wait(1)
        self.wait(3)

class LineAnimations(Scene):

    def construct(self):
        line = Line()
        title = Text("TitleScreen")
        self.play(Create(line), Write(title))
        self.wait()

if __name__ == "__main__":
    # scene = CareerGraph('253802', player_age='30:')
    # scene.render()

    # scene = BarGraph()
    # scene.render()

    # scene = ScatterPlotScene()
    # scene.render()

    # scene = LineGraphScene()
    # scene.render()

    scene = LineAnimations()
    scene.render()

    # scene = LineGraphExample()
    # scene.render()

