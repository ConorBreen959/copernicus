from scipy import stats
import plotly.express as px


def build_graph(data, graph_type):
    columns = parse_columns(data)

    graph_types = {
        "scatter": scatter_plot
    }
    graph_func = graph_types[graph_type]
    fig = graph_func(data, columns, stats=True)
    fig.update_xaxes(
        ticks='outside',
        showline=True,
        linewidth=2,
        linecolor='black'
    )
    fig.update_yaxes(
        ticks='outside',
        showline=True,
        linewidth=2,
        linecolor='black'
    )
    return fig


def scatter_plot(data, columns, stats=False):
    fig = px.scatter(
        data,
        x=columns["x_column"],
        y=columns["y_column"],
        template="simple_white"
    )
    if stats:
        label = stats_label(data[columns["x_column"]], data[columns["y_column"]])
        fig = px.scatter(
            data,
            x=columns["x_column"],
            y=columns["y_column"],
            template="plotly_white",
            trendline="ols",
            trendline_color_override="#440154"
        )
        fig.add_annotation(
            text=label,
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.05,
            y=0.95,
            font=dict(
                weight="bold",
                size=20
            )
        )
    fig.update_traces(marker_size=2, marker=dict(color="#4682b4"))
    return fig

def parse_columns(data):
    columns = {}
    columns["x_column"] = data.columns[0]
    columns["y_column"] = data.columns[1]
    if len(data.columns) == 3:
        columns["group_column"] = data[3]
    return columns


def stats_label(x, y):
    list_x = list(x)
    list_y = list(y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        list_x, list_y
    )
    stats_label = f"y = {round(intercept, 4)} + {round(slope, 4)}x<br>R<sup>2</sup> = {round((r_value ** 2), 4)}"
    return stats_label
