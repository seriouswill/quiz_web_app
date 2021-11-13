def create_bar_chart():
    p = figure(title="Daily Scores",
               x_axis_label='Days', y_axis_label='Scores')
    p.vbar(x=days2, top=day_scores, legend_label="User1",
           width=0.5, bottom=0, color="red")

    # display legend in top left corner (default is top right corner)
    p.legend.location = "top_left"

    # add a title to your legend
    p.legend.title = "Obervations"

    # change appearance of legend text
    p.legend.label_text_font = "times"
    p.legend.label_text_font_style = "italic"
    p.legend.label_text_color = "navy"

    # change border and background of legend
    p.legend.border_line_width = 3
    p.legend.border_line_color = "navy"
    p.legend.border_line_alpha = 0.8
    p.legend.background_fill_color = "navy"
    p.legend.background_fill_alpha = 0.2
    show(p)
