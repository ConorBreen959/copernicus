from pytz import timezone
from datetime import datetime, timedelta
from skyfield import almanac
from skyfield.api import N, E, wgs84, load
import pandas as pd
from timezonefinder import TimezoneFinder
import altair as alt
from altair import datum


class SunriseGraph:
    def __init__(self, city_dict, date):
        self.timescale = load.timescale()
        self.eph = load("de421.bsp")
        self.city = None
        self.timezone = None
        self.twilight_phases = None
        self.min_time = None
        self.max_time = None
        self.min_date = None
        self.max_date = None
        self.event_types = {
            "Night": "#39304A",
            "Astronomical dawn": "#693f59",
            "Astronomical dawn+1": "#693f59",
            "Astronomical dusk": "#693f59",
            "Nautical dawn": "#b56576",
            "Nautical dawn+1": "#b56576",
            "Nautical dusk": "#b56576",
            "Civil dawn": "#eaac8b",
            "Civil dawn+1": "#eaac8b",
            "Civil dusk": "#eaac8b",
            "Day": "#ffd27d",
        }
        self.set_timezone(city_dict)
        self.set_year(int(date[0:4]))
        self.sunrise_data = self.format_sunrise_data()

    def create_charts(self, date):
        sunrise_chart = self.create_graph(self.sunrise_data)
        date_line = self.add_date_line(date)
        sunrise_chart = sunrise_chart + date_line
        date_chart = self.create_date_chart(date, self.sunrise_data)
        daylight_summary = self.daylight_hours(date, self.sunrise_data)
        return sunrise_chart, date_chart, daylight_summary

    def set_timezone(self, city_dict):
        self.city = city_dict["city_name"]
        string_timezone = TimezoneFinder().timezone_at(
            lng=city_dict["longitude"], lat=city_dict["latitude"]
        )
        self.timezone = timezone(string_timezone)
        location = wgs84.latlon(
            float(city_dict["latitude"]) * N, float(city_dict["longitude"]) * E
        )
        self.twilight_phases = almanac.dark_twilight_day(self.eph, location)

    def set_year(self, year):
        days = 365
        if year % 4:
            days = 367
        now = self.timezone.localize(datetime(year, 1, 1))
        self.min_time = datetime(1900, 1, 1, 0, 0)
        self.max_time = datetime(1900, 1, 1, 23, 59, 59)
        self.min_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.max_date = self.min_date + timedelta(days=days)

    def format_sunrise_data(self):
        t0 = self.timescale.from_datetime(self.min_date)
        t1 = self.timescale.from_datetime(self.max_date)
        times, events = almanac.find_discrete(t0, t1, self.twilight_phases)

        twilight_data = []
        for index, (time, event) in enumerate(zip(times, events)):
            twilight_event = almanac.TWILIGHTS[event]
            start_date, start_time = self.format_time(time)
            if index == len(times) - 1:
                end_date, end_time = self.format_time(t1)
            else:
                end_date, end_time = self.format_time(times[index + 1])
            twilight_event = twilight_event.replace("twilight", "dawn")
            if start_time.hour > 12:
                twilight_event = twilight_event.replace("dawn", "dusk")
            data = self.process_twilight_data(
                twilight_event, start_date, start_time, end_date, end_time
            )
            twilight_data += data
        sunrise_df = pd.DataFrame.from_dict(twilight_data)
        return sunrise_df

    def process_twilight_data(
        self, twilight_event, start_date, start_time, end_date, end_time
    ):
        twilight_data = []
        data_dict = {
            "Date": start_date,
            "Event": twilight_event,
            "Starts": start_time,
            "Ends": end_time,
        }
        if end_date > start_date:
            data_dict = {
                "Date": start_date,
                "Event": twilight_event,
                "Starts": start_time,
                "Ends": self.max_time,
            }
            twilight_data.append(data_dict)
            date_diff = (end_date - start_date).days
            if date_diff > 1:
                count = 0
                while True:
                    count += 1
                    date = start_date + timedelta(days=count)
                    data_dict = {
                        "Date": date,
                        "Event": twilight_event,
                        "Starts": self.min_time,
                        "Ends": self.max_time,
                    }
                    twilight_data.append(data_dict)
                    if date_diff == count:
                        break
            twilight_event = twilight_event.replace("dusk", "dawn+1")
            data_dict = {
                "Date": end_date,
                "Event": twilight_event,
                "Starts": self.min_time,
                "Ends": end_time,
            }
        twilight_data.append(data_dict)
        return twilight_data

    def create_graph(self, sunrise_data):
        def background():
            theme = {
                "config": {
                    "view": {"height": 300, "width": 300, "fill": "#39304A"},
                    "title": {
                        "anchor": "start",
                        "dy": -15,
                        "fontSize": 24,
                        "fontWeight": 600,
                        "color": "#2f5275",
                    },
                    "area": {"fill": "#909090"},
                }
            }
            return theme

        alt.themes.register("background", background)
        alt.themes.enable("background")

        chart = alt.LayerChart(title=f"Sunrise Chart: {self.city}")
        legend_y_position = 40

        y_axis_limits = list(["1900-01-01T00:00:00", "1900-01-02T00:00:00"])
        y_scale = alt.Scale(domain=y_axis_limits, reverse=True)

        for event_type, fill in self.event_types.items():
            if event_type != "Night":
                event_chart = (
                    alt.Chart(sunrise_data)
                    .mark_area(color=fill)
                    .encode(
                        x="Date:T",
                        y=alt.Y("Starts:T", scale=y_scale),
                        y2="Ends:T",
                        tooltip=[
                            "Event",
                            "Date",
                            alt.Tooltip("Starts", format="%H:%M"),
                            alt.Tooltip("Ends", format="%H:%M"),
                        ],
                    )
                    .transform_filter(datum.Event == event_type)
                )
                legend_x_position = 820
                legend_y_position += 15

                if any(event_type.endswith(string) for string in ["dawn", "Day"]):
                    legend_box = self.add_legend_box(
                        [event_type],
                        fill,
                        (legend_x_position, legend_y_position),
                        25,
                        30,
                        font_size=16
                    )
                    chart += legend_box

                chart += event_chart

        chart = chart.encode(
            alt.X(axis=alt.Axis(format="%b")).title("Date"),
            alt.Y(axis=alt.Axis(format="%H:%M", tickCount=6)).title("Hour"),
        )
        chart = chart.configure_axis(
            labelFontSize=12,
            titleFontSize=16,
            labelColor = "#2f5275",
            titleColor = "#2f5275",
            tickColor = "#2f5275",
            grid=False,
        ).configure_view(stroke=None)
        chart = chart.properties(width=800, height=450)
        chart = chart.interactive()
        return chart

    def create_date_chart(self, date, sunrise_data):

        def add_date_chart_legend(chart, date_df):
            legend_x_position = -20
            legend_y_position = 150
            for event_type, fill in self.event_types.items():
                if any(
                    event_type.endswith(string) for string in ["dusk", "Day", "Night"]
                ):
                    event_type = event_type.split(" ")[0]
                    times_df = date_df.loc[
                        date_df["Event"].str.contains(event_type), ["Starts", "Ends"]
                    ]
                    text = [event_type]
                    for row in times_df.itertuples():
                        text.append(
                            f'{row.Starts.strftime("%H:%M")} - {row.Ends.strftime("%H:%M")}'
                        )
                    legend_box = self.add_legend_box(
                        text, fill, (legend_x_position, legend_y_position), 25, 35, font_size=16
                    )
                    chart += legend_box
                    legend_x_position += 150
            return chart

        date_df = sunrise_data.loc[
            sunrise_data["Date"] == date, ["Date", "Event", "Starts", "Ends"]
        ]
        date_object = datetime.strptime(date, "%Y-%m-%d")
        chart = alt.LayerChart().encode(
            alt.X(axis=alt.Axis(format="%H:%M", tickCount=9)).title("Hour"),
            alt.Y(axis=None),
        )
        chart = chart.properties(width=700, height=80)
        chart = chart.configure_axis(
            labelFontSize=12,
            titleFontSize=12,
        )
        chart = add_date_chart_legend(chart, date_df)

        date_chart = (
            alt.Chart(date_df)
            .mark_bar(size=80)
            .encode(
                x="Starts:T",
                x2="Ends:T",
                y="Date:T",
                color=alt.Color("Event:N")
                .scale(
                    domain=list(self.event_types.keys()),
                    range=list(self.event_types.values()),
                )
                .legend(None),
            )
        )

        date_text = [date_object.strftime(date_format) for date_format in ["%d", "%b"]]
        legend_box = self.add_legend_box(
            text=date_text,
            fill="#DBE2E9",
            legend_positions=(-80, 0),
            box_size=80.5,
            text_offset=40,
            align="center",
            font_size=20,
            corner_radius=5,
        )
        chart += date_chart + legend_box
        return chart

    def daylight_hours(self, date, sunrise_data):
        today = datetime.strptime(date, "%Y-%m-%d")
        yesterday = today - timedelta(1)
        tomorrow = today + timedelta(1)
        yesterday_length, today_length, tomorrow_length = (
            self.day_length(sunrise_data, day) for day in [yesterday, today, tomorrow]
        )
        styled_today_length = self.style_timedelta(today_length)
        shorter_html_string = '<span style="color: #a30000">shorter.</span>'
        longer_html_string = '<span style="color: #5081ec">longer.</span>'
        yesterday_difference = abs(today_length - yesterday_length)
        yesterday_diff_summary = (
            self.style_timedelta(yesterday_difference),
            shorter_html_string if today_length > yesterday_length else longer_html_string
        )
        tomorrow_difference = abs(today_length - tomorrow_length)
        tomorrow_diff_summary = (
            self.style_timedelta(tomorrow_difference),
            shorter_html_string if yesterday_length > today_length else longer_html_string
        )
        daylight_summary = f"<p>There are {styled_today_length} of daylight today.</p>"
        daylight_summary += f"<p>Yesterday was {yesterday_diff_summary[0]} {yesterday_diff_summary[1]}</p>"
        daylight_summary += f"<p>Tomorrow will be {tomorrow_diff_summary[0]} {tomorrow_diff_summary[1]}</p>"
        return daylight_summary

    def add_legend_box(
        self,
        text,
        fill,
        legend_positions,
        box_size,
        text_offset,
        align="left",
        font_size=12,
        corner_radius=5,
    ):
        x_position, y_position = legend_positions
        text = (
            alt.Chart()
            .mark_text(
                color="#08415C",
                align=align,
                baseline="top",
                fontWeight="bold",
                fontSize=font_size,
            )
            .encode(
                x=alt.value(x_position + text_offset),
                y=alt.value(y_position + (box_size / 4)),
                text=alt.value(text),
            )
        )

        box = (
            alt.Chart()
            .mark_rect(color=fill, cornerRadius=corner_radius)
            .encode(
                x=alt.value(x_position),
                x2=alt.value(x_position + box_size),
                y=alt.value(y_position),
                y2=alt.value(y_position + box_size),
            )
        )
        legend_box = box + text
        return legend_box

    def add_date_line(self, date):
        formatted_date = datetime.strptime(date, "%Y-%m-%d")
        date_dict = {
            "Date": [formatted_date, formatted_date],
            "Starts": [datetime.strptime(time, "%H:%M") for time in ["00:00", "23:59"]],
        }
        date_df = pd.DataFrame(data=date_dict)
        date_line_chart = (
            alt.Chart(date_df)
            .mark_line(color="#FFFFFF")
            .encode(x="Date:T", y="Starts:T")
        )
        text = date_line_chart.mark_text(
            align="center",
            baseline="top",
            dy=-15,
            fontWeight="bold",
            color="#08415C",
        ).encode(
            text="Date",
            opacity=alt.condition(
                alt.datum.Starts == alt.expr.toDate("1900-01-01T00:00"),
                alt.value(1),
                alt.value(0),
            ),
        )
        date_line_chart += text
        return date_line_chart

    def format_time(self, time):
        time_string = str(time.astimezone(self.timezone))[:19]
        date_x, time_x = time_string.split(" ")
        date_object = datetime.strptime(date_x, "%Y-%m-%d")
        date_object = date_object.replace(hour=0, minute=0, second=0, microsecond=0)
        time_object = datetime.strptime(time_x, "%H:%M:%S")
        return date_object, time_object

    def day_length(self, sunrise_data, date_object):
        date_string = date_object.strftime("%Y-%m-%d")
        date_df = sunrise_data.loc[
            (sunrise_data["Date"] == date_string) & (sunrise_data["Event"] == "Day")
        ]
        day_length = timedelta(0)
        for row in date_df.itertuples():
            day_length += row.Ends - row.Starts
        return day_length

    def style_timedelta(self, duration):
        total_seconds = duration.total_seconds()
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_string = ""
        for measure, name in zip(
            [hours, minutes, seconds], ["hour", "minute", "second"]
        ):
            if measure > 0:
                time_string += f"{int(measure)} {name}"
                if measure > 1:
                    time_string += "s"
                time_string += " "
        time_string = time_string.strip()
        return time_string
