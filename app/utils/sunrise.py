from pytz import timezone
from datetime import datetime, timedelta
from skyfield import almanac
from skyfield.api import N, E, wgs84, load
import pandas as pd
from timezonefinder import TimezoneFinder
import altair as alt
from altair import datum


class SunriseGraph:
    def __init__(self):
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
            # "Astronomical dawn": "#016792",
            # "Astronomical dusk": "#016792",
            # "Nautical dawn": "#74d4cc",
            # "Nautical dusk": "#74d4cc",
            # "Civil dawn": "#efeebc",
            # "Civil dusk": "#efeebc",
            # "Day": "#fee154",
            "Night": "#39304A",
            "Astronomical dawn": "#693f59",
            "Astronomical dusk": "#693f59",
            "Nautical dawn": "#b56576",
            "Nautical dusk": "#b56576",
            "Civil dawn": "#eaac8b",
            "Civil dusk": "#eaac8b",
            "Day": "#ffd27d",
        }

    def set_timezone(self, city_dict):
        self.city = city_dict["city_name"]
        string_timezone = TimezoneFinder().timezone_at(lng=city_dict["longitude"], lat=city_dict["latitude"])
        self.timezone = timezone(string_timezone)
        location = wgs84.latlon(float(city_dict["latitude"]) * N, float(city_dict["longitude"]) * E)
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

        data = []
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
            if end_date > start_date:
                date_diff = (end_date - start_date).days
                if date_diff > 1:
                    data_dict = {
                        "Date": start_date,
                        "Event": twilight_event,
                        "Starts": start_time,
                        "Ends": self.max_time,
                    }
                    data.append(data_dict)
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
                        data.append(data_dict)
                        if date_diff == count:
                            break
                data_dict = {
                    "Date": start_date,
                    "Event": twilight_event,
                    "Starts": start_time,
                    "Ends": self.max_time,
                    "Next Date": end_date,
                    "Next Starts": self.min_time,
                    "Next Ends": end_time,
                }
            else:
                data_dict = {
                    "Date": start_date,
                    "Event": twilight_event,
                    "Starts": start_time,
                    "Ends": end_time,
                }
            data.append(data_dict)
        sunrise_df = pd.DataFrame.from_dict(data)
        sunrise_df["Next Date"] = pd.to_datetime(sunrise_df["Next Date"])
        return sunrise_df

    def create_graph(self, sunrise_data):
        def background():
            theme = {
                "config": {
                    "view": {
                        "height": 300,
                        "width": 300,
                        "fill": "#39304A"
                    },
                    "title": {
                        "anchor": "start",
                        "dy": -15,
                        "fontSize": 16,
                        "fontWeight": 600,
                    },
                    "area": {
                        "fill": "#909090"
                    },
                    # "axis": {
                    #     "domainColor": "#FFFFFF",
                    #     "gridColor": "#FFFFFF",
                    #     "tickColor": "#FFFFFF",
                    #     "labelColor": "#FFFFFF",
                    # },

                }
            }
            return theme

        alt.themes.register("background", background)
        alt.themes.enable("background")

        chart = alt.LayerChart(title=f"Sunrise Chart: {self.city}")
        legend_y_position = 50

        y_scale = alt.Scale(domain=['1900-01-01T00:00:00', '1900-01-02T00:00:00'])

        for event_type, fill in self.event_types.items():
            if event_type != "Night":
                event_chart = alt.Chart(sunrise_data).mark_area(color=fill).encode(
                    x='Date:T',
                    y=alt.Y('Starts:T', scale=y_scale),
                    y2='Ends:T',
                    tooltip=["Date", "Starts", "Ends"]
                ).transform_filter(
                    datum.Event == event_type
                )
                next_chart = alt.Chart(sunrise_data).mark_area(color=fill).encode(
                    x='Date:T',
                    y=alt.Y('Next Starts:T', scale=y_scale),
                    y2='Next Ends:T',
                    tooltip=["Date", "Starts", "Ends"]
                ).transform_filter(
                    datum.Event == event_type
                )
                
                legend_y_position += 25
    
                if any(string in event_type for string in ["dawn", "Day"]):
                    text = alt.Chart({'values': [{}]}).mark_text(
                        color="#000000",
                        align="left",
                        baseline="top",
                        fontWeight="bold"
                    ).encode(
                        x=alt.value(850),  # pixels from left
                        y=alt.value(legend_y_position + 10),  # pixels from top
                        text=alt.value([event_type]))
                
                    box = alt.Chart({'values': [{}]}).mark_rect(color=fill, cornerRadius=5).encode(
                        x=alt.value(825),
                        x2=alt.value(845),
                        y=alt.value(legend_y_position + 5),
                        y2=alt.value(legend_y_position + 25))
    
                    chart += box + text
            
                chart += event_chart + next_chart

        chart = chart.encode(
            alt.X(axis=alt.Axis(format="%b")).title("Date"),
            alt.Y(axis=alt.Axis(format="%H:%M", tickCount=6)).title("Hour"),
        )
        chart = chart.configure_axis(
            grid=False
        ).configure_view(
            stroke=None
        )
        chart = chart.properties(
            width=800,
            height=450
        )
        chart = chart.interactive()
        return chart
    
    def create_date_chart(self, date, sunrise_data):
        date_df = sunrise_data.loc[sunrise_data["Date"] == date]
        night = sunrise_data.loc[date_df.index[0] - 1]
        night["Date"] = datetime.strptime(date, "%Y-%m-%d")
        night["Starts"] = night["Next Starts"]
        night["Ends"] = night["Next Ends"]
        night = night.to_frame().T
        
        date_df_with_night = pd.concat([
            night,
            date_df,
        ])
        date_df_with_night = date_df_with_night.infer_objects()
        chart = None
        for event_type, fill in self.event_types.items():
            event_chart = alt.Chart(date_df_with_night).mark_bar(size=50, color=fill).encode(
                x='Starts:T',
                x2='Ends:T',
                y='Date:T',
            ).transform_filter(
                datum.Event == event_type
            )
            if not chart:
                chart = event_chart
            else:
                chart = chart + event_chart
        chart = chart.encode(
            alt.X(axis=alt.Axis(format="%H")).title("Hour"),
            alt.Y('Date').axis(None),
        )
        chart = chart.properties(
            width=300,
            height=50
        )
        chart = chart.interactive()
        return chart
    
    def add_date_line(self, date, chart):
        formatted_date = datetime.strptime(date, "%Y-%m-%d")
        date_dict = {
            "Date": [formatted_date, formatted_date],
            "Starts": [datetime.strptime(time, "%H:%M") for time in ["00:00", "23:59"]]
        }
        date_df = pd.DataFrame(data=date_dict)
        date_line_chart = alt.Chart(date_df).mark_line(color="#FFFFFF").encode(
            x="Date:T",
            y="Starts:T"
        )
        chart += date_line_chart
        return chart

    def format_time(self, time):
        time_string = str(time.astimezone(self.timezone))[:16]
        date_x, time_x = time_string.split(" ")
        date_object = datetime.strptime(date_x, "%Y-%m-%d")
        date_object = date_object.replace(hour=0, minute=0, second=0, microsecond=0)
        time_object = datetime.strptime(time_x, "%H:%M")
        return date_object, time_object
