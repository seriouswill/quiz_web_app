from flask import Flask, render_template

import datetime
# graph Bokeh imports
from bokeh.plotting import figure, show
from bokeh.models.glyphs import VBar
from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource

# global variables
ready = False
q_index = 0
score = 0
day_scores = [4, 7, 4, 3, 9, 1, 8]
days2 = [1, 2, 3, 4, 5, 6, 7]
wrong = 0
days_completed = 0
days = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]
day = 0
weekday = datetime.datetime.today().weekday()

# graph testing section

x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

# chart tester


@app.route('/chart/')
def chart():
    global days2, day_scores
    # create a new plot with a title and axis labels
    p = figure(title="Multiple glyphs example",
               x_axis_label="x", y_axis_label="y")
    p.vbar(x=days2, top=day_scores, legend_label="Scores",
           width=0.5, bottom=0, color="red")
    # show(p)
    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    cdn_css = CDN.css_files

    return render_template('chart.html', script1=script1, div1=div1, cdn_js=cdn_js, cdn_css=cdn_css)


@app.route('/chart/')
def chart():
    global day_scores, days

    data = {"days": days, "scores": day_scores}
    for day in days:
        data['days'].append(day)

    hover = create_hover_tool()
    plot = create_bar_chart(data, "Scores by Day", "days",
                            "scores", hover)
    script, div = components(plot)

    return render_template('chart.html', days=days,
                           the_div=div, the_script=script)


def create_bar_chart(data, title, x_name, y_name, hover_tool=None,
                     width=1200, height=300):
    """Creates a bar chart plot with the exact styling for the centcom
    dashboard. Pass in data as a dictionary, desired plot title,
    name of x axis, y axis and the hover tool HTML.
    """
    source = ColumnDataSource(data)
    xdr = FactorRange(factors=data[x_name])
    ydr = Range1d(start=0, end=max(data[y_name])*1.5)

    tools = []
    if hover_tool:
        tools = [hover_tool, ]

    plot = figure(title=title, x_range=xdr, y_range=ydr, plot_width=width,
                  plot_height=height, h_symmetry=False, v_symmetry=False,
                  min_border=0, toolbar_location="above", tools=tools,
                  responsive=True, outline_line_color="#666666")

    glyph = VBar(x=x_name, top=y_name, bottom=0, width=.8,
                 fill_color="#e12127")
    plot.add_glyph(source, glyph)

    xaxis = LinearAxis()
    yaxis = LinearAxis()

    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
    plot.toolbar.logo = None
    plot.min_border_top = 0
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = "#999999"
    plot.yaxis.axis_label = "Bugs found"
    plot.ygrid.grid_line_alpha = 0.1
    plot.xaxis.axis_label = "Days after app deployment"
    plot.xaxis.major_label_orientation = 1
    return plot


def create_hover_tool():
    """Generates the HTML for the Bokeh's hover data tool on our graph."""
    hover_html = """
    <div>
        <span class="hover-tooltip">$x</span>
    </div>
    <div>
        <span class="hover-tooltip">@bugs bugs</span>
    </div>
    <div>
        <span class="hover-tooltip">$@costs{0.00}</span>
    </div>
    """
    return HoverTool(tooltips=hover_html)
