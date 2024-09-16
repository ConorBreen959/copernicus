import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import scipy.optimize
from skyfield.api import load, pi, tau
import plotly.graph_objects as go

ts = load.timescale()
eph = load("de421.bsp")

earth = eph["earth"]

objects = {
    "sun": eph["sun"],
    "mercury": eph["mercury"],
    "venus": eph["venus"],
    "mars": eph["mars"],
    "jupiter": eph["jupiter barycenter"],
    "saturn": eph["saturn barycenter"],
}
object_name = ["sun", "mercury", "venus", "mars", "jupiter", "saturn"]


def relative_longitude(t, body_1, body_2):
    "Compute how far away in longitude the two celestial objects are."
    e = earth.at(t)
    lat, lon, distance = e.observe(objects[body_1]).ecliptic_latlon()
    sl = lon.radians
    lat, lon, distance = e.observe(objects[body_2]).ecliptic_latlon()
    vl = lon.radians
    body_1_order = list(objects.keys()).index(body_1)
    body_2_order = list(objects.keys()).index(body_2)
    if body_1_order > body_2_order:
        relative_lon = (sl - vl + pi) % tau - pi
    else:
        relative_lon = (vl - sl + pi) % tau - pi
    return relative_lon


def calculate_conjunctions(year, body_1, body_2):
    def validate_year(year):
        okay = True
        if isinstance(year, str):
            okay = False
            if year.isnumeric():
                year = int(year)
                okay = True
        if okay and not 1900 <= year <= 2052:
            okay = False
        if not okay:
            print("ERROR: Please pick a year between 1900 and 2052")
            sys.exit(0)
        return year
    
    yy = validate_year(str(year))

    # Process monthly starting points spanning the chosen year
    t = ts.utc(yy, range(13))

    # Where in the sky were the two celestial objects on those dates?
    
    relative_lon = relative_longitude(t, body_1, body_2)

    opp_ndx = []
    conjunctions_per_year = []
    oppositions_per_year = []
    # Find where object B passed from being ahead of object A to being behind:
    conjunctionsInf = (relative_lon >= 0)[:-1] & (relative_lon < 0)[1:]
    # Find where object A passed from being ahead of object B to being behind:
    conjunctionsSup = (relative_lon < 0)[:-1] & (relative_lon >= 0)[1:]
    # ignore planets in opposition (only within conjunctionsSup) ...
    for i in conjunctionsSup.nonzero()[0]:
        if relative_lon[i+1] - relative_lon[i] > 5.0: 
            opp_ndx.append(i)
    # all conjunctions is the sum of both
    conjunctions = conjunctionsInf + conjunctionsSup


        # For each month that included a conjunction,
        # ask SciPy exactly when the conjunction occurred.
    for i in conjunctions.nonzero()[0]:
        t0 = ts.tt(jd=t[i].tt)

        t1 = ts.tt(jd=t[i + 1].tt)
        # print("Starting search at", t0.utc_jpl())
        jdt = scipy.optimize.brentq(
            relative_longitude, t0, t1, args=(body_1, body_2)
        )
        tt = ts.tt(jd=jdt)
        if i in opp_ndx:    # planets in opposition?
            if "sun" in [body_1, body_2]:  # ignore if planet is not in opposition to the sun
                # if j != 0 the planets are also theoretically "in opposition" in
                # that their apparent geocentric celestial longitudes differ by 180°
                oppositions_per_year.append((jdt, body_1, body_2))
        else:
            # append result as tuple to a list
            conjunctions_per_year.append((jdt, body_1, body_2))

    conjunctions_per_year.sort()  # sort tuples in-place by date
    oppositions_per_year.sort()
    
    for jdt, body_1, body_2 in conjunctions_per_year:
        print("Found conjunctions")
        tt = ts.tt(jd=jdt)
        # if int(tt.utc_strftime("%Y")) != yy: continue  # filter out incorrect years
        print(
            " {:7}-{:7}: {}".format(body_1, body_2, tt.utc_jpl())
        )

    for jdt, body_1, body_2 in oppositions_per_year:
        print("Found oppositions")
        tt = ts.tt(jd=jdt)
        # if int(tt.utc_strftime("%Y")) != yy: continue  # filter out incorrect years
        print(
            " {:7}-{:7}: {}".format(body_1, body_2, tt.utc_jpl())
        )


def calculate_retrogrades(year_zero, body):
    days = 7300
    base = datetime.strptime(str(year_zero), "%Y")
    years = [base + timedelta(days=x) for x in range(days)]
    ts = load.timescale()
    t = ts.utc(year_zero, 1, np.linspace(1, days, days))
    
    # thanks to @barrycarter's comment, do it the right way!
    eclat, eclon, ecd = earth.at(t).observe(objects[body]).ecliptic_latlon()
    
    eclondgs = (180./np.pi) * eclon.radians
    eclondel = eclondgs[1:] - eclondgs[:-1]
    
    eclondel[eclondel < -300] += 360. # this is a fudge for now
    eclondel[eclondel > +300] -= 360. # this is a fudge for now
    
    prograde   = eclondel > 0.
    
    eclon_prograde   = eclondgs.copy()[:-1]
    eclon_retrograde = eclondgs.copy()[:-1]
    
    eclon_prograde[~prograde]  = np.nan
    eclon_retrograde[prograde] = np.nan
    
    prograde = pd.DataFrame(data={"Year": years[:-1], "Position": eclon_prograde})
    prograde["Type"] = "Prograde"
    retrograde = pd.DataFrame(data={"Year": years[:-1], "Position": eclon_retrograde})
    retrograde["Type"] = "Retrograde"
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=prograde["Year"],
        y=prograde["Position"],
        mode="lines",
        hovertemplate="Type: Prograde<br>Date: %{x|%d-%b-%Y}<br>Position: %{y}"
    ))
    fig.add_trace(go.Scatter(
        x=retrograde["Year"],
        y=retrograde["Position"],
        mode="lines",
        hovertemplate="Type: Retrograde<br>Date: %{x|%d-%b-%Y}<br>Position: %{y}"
    ))
    
    # data = pd.concat([prograde, retrograde])
    
    # fig = px.line(data, x="Year", y="Position", color="Type", template="simple_white")
    # # fig.update_traces(hovertemplate="Date: %{x|%d-%b-%Y}<br>Position: %{y}<br>Type: %{color}")
    fig.update_layout(
        yaxis_range=[0,360],
        hovermode="x unified",
        template="simple_white"
    )
    rotation_dates = prograde.loc[prograde["Position"] < 1, "Year"]
    [fig.add_vline(x=date, line_width=4) for date in rotation_dates]
    return fig