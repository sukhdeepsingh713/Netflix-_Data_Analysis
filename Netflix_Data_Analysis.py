"""
Netflix Catalog Dashboard
Streamlit + Plotly

Run:
    pip install -r requirements.txt
    streamlit run app.py

Expects "netflix1.csv" in the same folder (columns: show_id, type, title,
director, country, date_added, release_year, rating, duration, listed_in).
If the file isn't found, a sidebar uploader lets you pick one.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Netflix Catalog Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# THEME / PALETTE  ("Streaming Noir")
# ----------------------------------------------------------------------------
BG          = "#0A0A0F"
SURFACE     = "#161420"
SURFACE_2   = "#1E1B2A"
BORDER      = "#2C2838"
TEXT        = "#F3F0EA"
TEXT_DIM    = "#A39EB0"
TEXT_FAINT  = "#6E6980"

CRIMSON = "#E63950"
GOLD    = "#F2B441"
TEAL    = "#35C4B4"
VIOLET  = "#9B7EDE"
ROSE    = "#E85D75"
AMBER   = "#D98E3F"
SEAFOAM = "#5FD0C0"
LILAC   = "#B9A3E8"

SERIES = [CRIMSON, TEAL, GOLD, VIOLET, ROSE, SEAFOAM, AMBER, LILAC]

PLOTLY_LAYOUT = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(family="Inter, sans-serif", color=TEXT_DIM, size=12),
    title_font=dict(family="Inter, sans-serif", color=TEXT, size=15),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM)),
    margin=dict(l=10, r=10, t=40, b=10),
    hoverlabel=dict(bgcolor=SURFACE_2, font_color=TEXT, bordercolor=BORDER, font_family="monospace"),
    colorway=SERIES,
)
AXIS_STYLE = dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER, color=TEXT_DIM)


def style_fig(fig, height=380, polar=False):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    if not polar:
        fig.update_xaxes(**AXIS_STYLE)
        fig.update_yaxes(**AXIS_STYLE)
    else:
        fig.update_polars(
            bgcolor=SURFACE,
            radialaxis=dict(gridcolor=BORDER, linecolor=BORDER, color=TEXT_DIM),
            angularaxis=dict(gridcolor=BORDER, linecolor=BORDER, color=TEXT_DIM),
        )
    return fig


# ----------------------------------------------------------------------------
# CSS INJECTION
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    .stApp {{
        background: {BG};
        background-image:
            radial-gradient(ellipse 80% 50% at 20% -10%, rgba(230,57,80,0.10), transparent),
            radial-gradient(ellipse 60% 40% at 100% 10%, rgba(53,196,180,0.06), transparent);
        color: {TEXT};
    }}
    section[data-testid="stSidebar"] {{
        background: {SURFACE};
        border-right: 1px solid {BORDER};
    }}
    .brand-mark {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 30px;
        letter-spacing: 1px;
        color: {CRIMSON};
        line-height: 1;
        margin-bottom: 0px;
    }}
    .brand-sub {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10.5px;
        color: {TEXT_FAINT};
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 18px;
    }}
    .page-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 36px;
        letter-spacing: .5px;
        line-height: 1;
        color: {TEXT};
        margin-bottom: 2px;
    }}
    .page-desc {{
        color: {TEXT_DIM};
        font-size: 13.5px;
        margin-bottom: 18px;
    }}
    .card-title {{
        font-size: 14.5px;
        font-weight: 600;
        color: {TEXT};
        margin-bottom: 0px;
    }}
    .card-sub {{
        font-size: 11.5px;
        color: {TEXT_FAINT};
        margin-bottom: 6px;
    }}
    .card-tag {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: .8px;
        color: {TEXT_FAINT};
        background: {SURFACE_2};
        border: 1px solid {BORDER};
        padding: 3px 7px;
        border-radius: 4px;
        float: right;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {SURFACE};
        border: 1px solid {BORDER} !important;
        border-radius: 12px;
        padding: 4px 6px;
    }}
    .filter-status {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: {TEXT_FAINT};
    }}
    .filter-status b {{ color: {GOLD}; font-weight: 500; }}
    .kpi-label {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: {TEXT_FAINT};
        margin-bottom: 4px;
    }}
    .kpi-value {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 30px;
        letter-spacing: .5px;
        line-height: 1.1;
    }}
    .kpi-sub {{
        font-size: 11px;
        color: {TEXT_DIM};
        margin-top: 2px;
    }}
    hr {{ border-color: {BORDER}; }}
    div[role="radiogroup"] label {{
        background: {SURFACE_2};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 6px 10px !important;
        margin-bottom: 4px !important;
    }}
    .stSlider label, .stSelectbox label {{
        color: {TEXT_FAINT} !important;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10.5px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file)

    def first_country(c):
        if not isinstance(c, str) or not c.strip():
            return "Unknown"
        return c.split(",")[0].strip()

    def genre_list(g):
        if not isinstance(g, str) or not g.strip():
            return ["Unknown"]
        return [x.strip() for x in g.split(",") if x.strip()]

    def parse_leading_number(x):
        if not isinstance(x, str):
            return np.nan
        token = x.strip().split(" ")[0]
        return int(token) if token.isdigit() else np.nan

    def parse_year_added(x):
        try:
            return int(str(x).split("/")[-1])
        except Exception:
            return np.nan

    df["country_primary"] = df["country"].apply(first_country)
    df["genres"] = df["listed_in"].apply(genre_list)
    df["duration_val"] = df["duration"].apply(parse_leading_number)
    df["year_added"] = df["date_added"].apply(parse_year_added)
    df["rating"] = df["rating"].fillna("Unrated")
    df["rating"] = df["rating"].replace("", "Unrated")
    df["release_year"] = df["release_year"].astype(int)
    return df


DATA_PATH = "netflix1.csv"
try:
    raw = load_data(DATA_PATH)
except FileNotFoundError:
    st.sidebar.warning("netflix1.csv not found next to app.py")
    uploaded = st.sidebar.file_uploader("Upload the Netflix CSV", type="csv")
    if uploaded is None:
        st.title("🎬 Netflix Catalog Dashboard")
        st.info("Upload your Netflix CSV in the sidebar to get started.")
        st.stop()
    raw = load_data(uploaded)

# ----------------------------------------------------------------------------
# SIDEBAR — BRAND, MENU, FILTERS
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand-mark">CATALOG//</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Netflix Library Analytics</div>', unsafe_allow_html=True)

    section = st.radio(
        "Menu",
        ["Overview", "Content Mix", "Geography", "Genres", "Ratings", "Trends"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<div class="brand-sub" style="margin-bottom:8px;">FILTERS</div>', unsafe_allow_html=True)

    type_filter = st.selectbox("Type", ["All", "Movie", "TV Show"])

    country_counts = raw[~raw["country_primary"].isin(["Unknown", "Not Given"])]["country_primary"].value_counts()
    country_options = ["All"] + country_counts.head(30).index.tolist()
    country_filter = st.selectbox("Country", country_options)

    rating_counts = raw["rating"].value_counts()
    rating_options = ["All"] + rating_counts.index.tolist()
    rating_filter = st.selectbox("Rating", rating_options)

    genre_counts = raw.explode("genres")["genres"].value_counts()
    genre_options = ["All"] + genre_counts.head(30).index.tolist()
    genre_filter = st.selectbox("Genre", genre_options)

    year_min, year_max = int(raw["release_year"].min()), int(raw["release_year"].max())
    year_range = st.slider("Release Year", year_min, year_max, (year_min, year_max))

    if st.button("Reset filters", width='stretch'):
        st.rerun()

# ----------------------------------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------------------------------
df = raw.copy()
if type_filter != "All":
    df = df[df["type"] == type_filter]
if country_filter != "All":
    df = df[df["country_primary"] == country_filter]
if rating_filter != "All":
    df = df[df["rating"] == rating_filter]
if genre_filter != "All":
    df = df[df["genres"].apply(lambda g: genre_filter in g)]
df = df[(df["release_year"] >= year_range[0]) & (df["release_year"] <= year_range[1])]

st.sidebar.markdown(
    f'<div class="filter-status">Showing <b>{len(df):,}</b> of {len(raw):,} titles</div>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------

def card_header(title, tag, sub):
    st.markdown(
        f'<span class="card-tag">{tag}</span><div class="card-title">{title}</div>'
        f'<div class="card-sub">{sub}</div>',
        unsafe_allow_html=True,
    )


def exploded_genres(frame):
    return frame.explode("genres")


def kpi_card(col, label, value, sub="", color=TEXT):
    with col.container(border=True):
        st.markdown(
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="color:{color};">{value}</div>'
            f'<div class="kpi-sub">{sub}</div>',
            unsafe_allow_html=True,
        )


def render_kpis(frame):
    total = len(frame)
    movies = int((frame["type"] == "Movie").sum())
    tv = int((frame["type"] == "TV Show").sum())
    countries = frame[~frame["country_primary"].isin(["Unknown", "Not Given"])]["country_primary"].nunique()
    genres_n = exploded_genres(frame)["genres"].nunique()
    avg_dur = frame[(frame["type"] == "Movie") & frame["duration_val"].notna()]["duration_val"].mean()
    avg_dur_txt = f"{avg_dur:,.0f} min" if pd.notna(avg_dur) else "—"

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi_card(c1, "Total Titles", f"{total:,}", "in current view", TEXT)
    kpi_card(c2, "Movies", f"{movies:,}", f"{(movies/total*100 if total else 0):.0f}% of view", CRIMSON)
    kpi_card(c3, "TV Shows", f"{tv:,}", f"{(tv/total*100 if total else 0):.0f}% of view", TEAL)
    kpi_card(c4, "Countries", f"{countries:,}", "producing titles", GOLD)
    kpi_card(c5, "Genres", f"{genres_n:,}", "distinct tags", VIOLET)
    kpi_card(c6, "Avg Movie Runtime", avg_dur_txt, "across filtered movies", ROSE)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# KPI CARDS (shown above every section)
# ----------------------------------------------------------------------------
render_kpis(df)

# ----------------------------------------------------------------------------
# SECTION: OVERVIEW
# ----------------------------------------------------------------------------
if section == "Overview":
    st.markdown('<div class="page-title">Overview</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-desc">A first pass across the whole catalog &mdash; '
        "what's on Netflix, and how it's grown.</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1.container(border=True):
        card_header("Movies vs TV Shows", "Doughnut", "Share of catalog by content type")
        type_counts = df["type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig = px.pie(type_counts, names="type", values="count", hole=0.62,
                     color="type", color_discrete_map={"Movie": CRIMSON, "TV Show": TEAL})
        fig.update_traces(textfont_color=TEXT, marker=dict(line=dict(color=SURFACE, width=3)))
        st.plotly_chart(style_fig(fig), width='stretch')

    with c2.container(border=True):
        card_header("Titles Added Per Year", "Line", "Catalog additions by year added to Netflix")
        added = df.dropna(subset=["year_added"]).groupby("year_added").size().reset_index(name="count")
        fig = px.area(added, x="year_added", y="count")
        fig.update_traces(line_color=GOLD, fillcolor="rgba(242,180,65,0.15)", mode="lines+markers",
                           marker=dict(color=GOLD, size=5))
        st.plotly_chart(style_fig(fig), width='stretch')

    with st.container(border=True):
        card_header("Top 12 Genres", "Horizontal Bar", "Most common genre tags across all titles")
        g = exploded_genres(df)["genres"].value_counts().head(12).sort_values()
        fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h", marker_color=CRIMSON))
        st.plotly_chart(style_fig(fig, height=420), width='stretch')

# ----------------------------------------------------------------------------
# SECTION: CONTENT MIX
# ----------------------------------------------------------------------------
elif section == "Content Mix":
    st.markdown('<div class="page-title">Content Mix</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-desc">How long titles run, and how the movie/TV balance '
        "has shifted over time.</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1.container(border=True):
        card_header("Movie Duration", "Bar", "Distribution of movie runtimes (minutes)")
        movies = df[(df["type"] == "Movie") & df["duration_val"].notna()].copy()
        bins = [0, 30, 60, 90, 120, 150, 180, 9999]
        labels = ["<30", "30-60", "60-90", "90-120", "120-150", "150-180", "180+"]
        movies["bucket"] = pd.cut(movies["duration_val"], bins=bins, labels=labels, right=False)
        counts = movies["bucket"].value_counts().reindex(labels).fillna(0)
        fig = go.Figure(go.Bar(x=labels, y=counts.values, marker_color=TEAL))
        st.plotly_chart(style_fig(fig), width='stretch')

    with c2.container(border=True):
        card_header("TV Show Seasons", "Bar", "Number of seasons per TV show")
        tv = df[(df["type"] == "TV Show") & df["duration_val"].notna()].copy()
        tv["season_bucket"] = tv["duration_val"].apply(lambda x: "6+" if x >= 6 else str(int(x)))
        order = ["1", "2", "3", "4", "5", "6+"]
        counts = tv["season_bucket"].value_counts().reindex(order).fillna(0)
        fig = go.Figure(go.Bar(x=[f"{o} season{'' if o=='1' else 's'}" for o in order],
                                y=counts.values, marker_color=VIOLET))
        st.plotly_chart(style_fig(fig), width='stretch')

    with st.container(border=True):
        card_header("Movies vs TV Shows Added Over Time", "Stacked Area",
                     "Yearly additions split by content type")
        ta = df.dropna(subset=["year_added"]).groupby(["year_added", "type"]).size().reset_index(name="count")
        pivot = ta.pivot(index="year_added", columns="type", values="count").fillna(0).sort_index()
        fig = go.Figure()
        if "Movie" in pivot.columns:
            fig.add_trace(go.Scatter(x=pivot.index, y=pivot["Movie"], name="Movies", stackgroup="one",
                                      line_color=CRIMSON, fillcolor="rgba(230,57,80,0.35)"))
        if "TV Show" in pivot.columns:
            fig.add_trace(go.Scatter(x=pivot.index, y=pivot["TV Show"], name="TV Shows", stackgroup="one",
                                      line_color=TEAL, fillcolor="rgba(53,196,180,0.35)"))
        st.plotly_chart(style_fig(fig, height=380), width='stretch')

# ----------------------------------------------------------------------------
# SECTION: GEOGRAPHY
# ----------------------------------------------------------------------------
elif section == "Geography":
    st.markdown('<div class="page-title">Geography</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Where Netflix content is produced.</div>', unsafe_allow_html=True)

    with st.container(border=True):
        card_header("Top 10 Producing Countries", "Bar", "Titles by primary country of production")
        cc = df[~df["country_primary"].isin(["Unknown", "Not Given"])]["country_primary"] \
            .value_counts().head(10)
        fig = go.Figure(go.Bar(x=cc.index, y=cc.values, marker_color=GOLD))
        st.plotly_chart(style_fig(fig), width='stretch')

    with st.container(border=True):
        card_header("Movie / TV Split by Country", "Stacked Bar",
                     "Content type breakdown across the top 8 countries")
        top8 = cc.head(8).index.tolist()
        sub = df[df["country_primary"].isin(top8)]
        ct = sub.groupby(["country_primary", "type"]).size().reset_index(name="count")
        pivot = ct.pivot(index="country_primary", columns="type", values="count").reindex(top8).fillna(0)
        fig = go.Figure()
        if "Movie" in pivot.columns:
            fig.add_trace(go.Bar(x=pivot.index, y=pivot["Movie"], name="Movies", marker_color=CRIMSON))
        if "TV Show" in pivot.columns:
            fig.add_trace(go.Bar(x=pivot.index, y=pivot["TV Show"], name="TV Shows", marker_color=TEAL))
        fig.update_layout(barmode="stack")
        st.plotly_chart(style_fig(fig, height=380), width='stretch')

# ----------------------------------------------------------------------------
# SECTION: GENRES
# ----------------------------------------------------------------------------
elif section == "Genres":
    st.markdown('<div class="page-title">Genres</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">The tags that define the catalog.</div>', unsafe_allow_html=True)

    with st.container(border=True):
        card_header("Top 15 Genres", "Horizontal Bar",
                     "Most frequent genre tags (titles can carry multiple)")
        g = exploded_genres(df)["genres"].value_counts().head(15).sort_values()
        colors = [SERIES[i % len(SERIES)] for i in range(len(g))]
        fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h", marker_color=colors))
        st.plotly_chart(style_fig(fig, height=460), width='stretch')

    with st.container(border=True):
        card_header("Leading Genres — Shape Comparison", "Radar",
                     "Relative weight of the top 6 genres")
        top6 = exploded_genres(df)["genres"].value_counts().head(6).index.tolist()
        movie_counts = [df[(df["type"] == "Movie") & df["genres"].apply(lambda gl: gg in gl)].shape[0]
                         for gg in top6]
        tv_counts = [df[(df["type"] == "TV Show") & df["genres"].apply(lambda gl: gg in gl)].shape[0]
                      for gg in top6]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=movie_counts + [movie_counts[0]], theta=top6 + [top6[0]],
                                       fill="toself", name="Movies", line_color=CRIMSON,
                                       fillcolor="rgba(230,57,80,0.18)"))
        fig.add_trace(go.Scatterpolar(r=tv_counts + [tv_counts[0]], theta=top6 + [top6[0]],
                                       fill="toself", name="TV Shows", line_color=TEAL,
                                       fillcolor="rgba(53,196,180,0.18)"))
        st.plotly_chart(style_fig(fig, height=440, polar=True), width='stretch')

# ----------------------------------------------------------------------------
# SECTION: RATINGS
# ----------------------------------------------------------------------------
elif section == "Ratings":
    st.markdown('<div class="page-title">Ratings</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Audience and maturity ratings across the catalog.</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1.container(border=True):
        card_header("Rating Distribution", "Bar", "Titles per content rating")
        rc = df["rating"].value_counts()
        fig = go.Figure(go.Bar(x=rc.index, y=rc.values, marker_color=ROSE))
        st.plotly_chart(style_fig(fig), width='stretch')

    with c2.container(border=True):
        card_header("Rating Share", "Polar Area", "Proportional view of top ratings")
        rc8 = df["rating"].value_counts().head(8)
        fig = go.Figure(go.Barpolar(r=rc8.values, theta=rc8.index,
                                     marker_color=[SERIES[i % len(SERIES)] for i in range(len(rc8))]))
        st.plotly_chart(style_fig(fig, height=380, polar=True), width='stretch')

    with st.container(border=True):
        card_header("Ratings by Content Type", "Stacked Bar",
                     "How rating categories split between movies and TV shows")
        top_ratings = df["rating"].value_counts().head(8).index.tolist()
        sub = df[df["rating"].isin(top_ratings)]
        rt = sub.groupby(["rating", "type"]).size().reset_index(name="count")
        pivot = rt.pivot(index="rating", columns="type", values="count").reindex(top_ratings).fillna(0)
        fig = go.Figure()
        if "Movie" in pivot.columns:
            fig.add_trace(go.Bar(x=pivot.index, y=pivot["Movie"], name="Movies", marker_color=GOLD))
        if "TV Show" in pivot.columns:
            fig.add_trace(go.Bar(x=pivot.index, y=pivot["TV Show"], name="TV Shows", marker_color=VIOLET))
        fig.update_layout(barmode="stack")
        st.plotly_chart(style_fig(fig, height=380), width='stretch')

# ----------------------------------------------------------------------------
# SECTION: TRENDS
# ----------------------------------------------------------------------------
elif section == "Trends":
    st.markdown('<div class="page-title">Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Release patterns and how runtime relates to release year.</div>',
                unsafe_allow_html=True)

    with st.container(border=True):
        card_header("Titles by Release Year", "Line", "Original release year of catalog titles")
        rl = df.groupby("release_year").size().reset_index(name="count")
        fig = px.area(rl, x="release_year", y="count")
        fig.update_traces(line_color=CRIMSON, fillcolor="rgba(230,57,80,0.12)")
        st.plotly_chart(style_fig(fig), width='stretch')

    with st.container(border=True):
        card_header("Movie Runtime vs Release Year", "Scatter", "Each point is one movie")
        movies = df[(df["type"] == "Movie") & df["duration_val"].notna()]
        if len(movies) > 1800:
            movies = movies.sample(1800, random_state=42)
        fig = px.scatter(movies, x="release_year", y="duration_val",
                          labels={"release_year": "Release Year", "duration_val": "Duration (min)"})
        fig.update_traces(marker=dict(color=TEAL, opacity=0.55, size=6))
        st.plotly_chart(style_fig(fig, height=420), width='stretch')