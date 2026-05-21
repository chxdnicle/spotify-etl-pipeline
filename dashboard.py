import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import requests

# ============================================================
# COLOUR PALETTES  (module-level constants)
# ============================================================

GCOLS  = ["#1DB954", "#F4B942", "#9B59B6", "#E74C3C", "#3498DB", "#777"]
ACOLS  = ["#1DB954", "#3498DB", "#E74C3C", "#F39C12", "#9B59B6"]
ALCOLS = {"album": "#1DB954", "single": "#7FD16E", "ep": "#B3B3B3", "compilation": "#444"}

# ============================================================
# HELPER: format minutes → "Xh Ym"
# ============================================================

def fmt_t(m):
    h, mn = int(m // 60), int(m % 60)
    return f"{h}h {mn}m" if h else f"{mn}m"

# ============================================================
# HELPER: legend item
# ============================================================

def legend_item(label, pct, color):
    return html.Div([
        html.Div(className="ld-dot", style={"background": color}),
        html.Div(label.title(), className="ld-label"),
        html.Div(f"{pct}%", className="ld-pct"),
    ], className="ld-item")

# ============================================================
# MAIN DATA + LAYOUT BUILDER  (called on load AND on refresh)
# ============================================================

def build_dashboard():

    # ── load ────────────────────────────────────────────────
    df = pd.read_csv("master_spotify_data.csv")
    df["played_at"] = pd.to_datetime(df["played_at"])

    TRACK_COL = next((c for c in ["track_name", "song_name", "name", "title"] if c in df.columns), None)
    ALBUM_COL  = next((c for c in ["album_name", "album", "release"] if c in df.columns), None)

    # ── KPIs ────────────────────────────────────────────────
    total_tracks = len(df)
    uniq_artists = df["artist_name"].nunique()
    uniq_albums  = df[ALBUM_COL].nunique() if ALBUM_COL else "–"
    tot_mins     = df["duration_mins"].sum()
    tot_h        = int(tot_mins // 60)
    tot_m        = int(tot_mins % 60)
    avg_dur      = round(df["duration_mins"].mean(), 2)

    # ── daily activity ──────────────────────────────────────
    daily = df.groupby(df["played_at"].dt.date).size().reset_index(name="n")

    # SPARKLINE  –  smooth spline
    fig_spark = go.Figure(go.Scatter(
        y=daily["n"].tolist(), mode="lines",
        line=dict(color="#1DB954", width=1.5, shape="spline", smoothing=1.3),
        fill="tozeroy", fillcolor="rgba(29,185,84,0.18)"
    ))
    fig_spark.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False
    )

    # LISTENING OVER TIME  –  smooth spline
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(
        x=daily["played_at"], y=daily["n"], mode="lines",
        fill="tozeroy",
        line=dict(color="#1DB954", width=2.5, shape="spline", smoothing=1.3),
        fillcolor="rgba(29,185,84,0.18)"
    ))
    fig_time.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#888", size=10, family="Figtree"),
        margin=dict(l=35, r=8, t=8, b=30),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)",
                   zeroline=False, tickfont=dict(size=10)),
    )

    # ── top genres  –  colourful donut ──────────────────────
    gen = (df.groupby("song_genre")["duration_mins"].sum()
             .reset_index().sort_values("duration_mins", ascending=False).head(6))
    gen["pct"] = (gen["duration_mins"] / gen["duration_mins"].sum() * 100).round(1)

    fig_genre = go.Figure(go.Pie(
        labels=gen["song_genre"], values=gen["duration_mins"],
        hole=0.64, marker=dict(colors=GCOLS[:len(gen)]),
        textinfo="none", sort=False
    ))
    fig_genre.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"),
        margin=dict(l=0, r=0, t=0, b=0), showlegend=False
    )

    genre_legend = [legend_item(r["song_genre"], f"{r['pct']:.0f}", GCOLS[i])
                    for i, (_, r) in enumerate(gen.iterrows())]

    # ── top artists ─────────────────────────────────────────
    top_art = (df.groupby("artist_name")["duration_mins"].sum()
                 .reset_index().sort_values("duration_mins", ascending=False).head(5))
    top_art["h"] = (top_art["duration_mins"] // 60).astype(int)
    top_art["m"] = (top_art["duration_mins"] % 60).astype(int)
    max_art = top_art["duration_mins"].max()

    def artist_row(i, row):
        pct   = int(row["duration_mins"] / max_art * 100)
        init  = "".join(w[0].upper() for w in row["artist_name"].split()[:2])
        color = ACOLS[i % len(ACOLS)]
        return html.Div([
            html.Div(str(i + 1), className="ar-rank"),
            html.Div(init, className="ar-avatar", style={"background": color}),
            html.Div([
                html.Div(row["artist_name"], className="ar-name"),
                html.Div(
                    html.Div(className="ar-fill", style={"width": f"{pct}%", "background": color}),
                    className="ar-bar"
                )
            ], className="ar-info"),
            html.Div(f"{row['h']}h {row['m']}m", className="ar-time")
        ], className="ar-row")

    artist_rows = [artist_row(i, r) for i, (_, r) in enumerate(top_art.iterrows())]

    # ── top tracks ──────────────────────────────────────────
    if TRACK_COL:
        grp = [TRACK_COL, "artist_name"] + ([ALBUM_COL] if ALBUM_COL else [])
        tt  = (df.groupby(grp)["duration_mins"].sum()
                 .reset_index().sort_values("duration_mins", ascending=False).head(5))
        _ac = ALBUM_COL if (ALBUM_COL and ALBUM_COL in tt.columns) else None
    else:
        tt  = pd.DataFrame()
        _ac = None

    def track_row(i, row):
        return html.Div([
            html.Div(str(i + 1), className="tr-rank"),
            html.Div(row.get(TRACK_COL, "–"), className="tr-name"),
            html.Div(row["artist_name"], className="tr-artist"),
            html.Div(row.get(_ac, "–") if _ac else "–", className="tr-album"),
            html.Div(fmt_t(row["duration_mins"]), className="tr-time"),
        ], className="tr-row" + (" tr-alt" if i % 2 else ""))

    tr_header = html.Div([
        html.Div("#",          className="tr-rank  tr-hdr"),
        html.Div("TRACK NAME", className="tr-name  tr-hdr"),
        html.Div("ARTIST",     className="tr-artist tr-hdr"),
        html.Div("ALBUM",      className="tr-album  tr-hdr"),
        html.Div("PLAY TIME",  className="tr-time   tr-hdr"),
    ], className="tr-row tr-header-row")

    tr_rows_html = ([tr_header] + [track_row(i, r) for i, (_, r) in enumerate(tt.iterrows())]
                    if not tt.empty
                    else [html.Div(
                        "Add a track_name or song_name column to your CSV to enable this section.",
                        style={"color": "#666", "padding": "16px 4px", "fontSize": "12px"}
                    )])

    # ── album type breakdown ─────────────────────────────────
    alb = df["album_type"].value_counts().reset_index()
    alb.columns = ["album_type", "count"]
    alb["pct"] = (alb["count"] / alb["count"].sum() * 100).round(0).astype(int)

    fig_alb = go.Figure(go.Pie(
        labels=alb["album_type"], values=alb["count"], hole=0.66,
        marker=dict(colors=[ALCOLS.get(t.lower(), "#555") for t in alb["album_type"]]),
        textinfo="none", sort=False
    ))
    fig_alb.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"),
        margin=dict(l=0, r=0, t=0, b=0), showlegend=False
    )

    alb_legend = [legend_item(r["album_type"], r["pct"], ALCOLS.get(r["album_type"].lower(), "#555"))
                  for _, r in alb.iterrows()]

    # ── assemble layout ─────────────────────────────────────
    return html.Div([

        # HEADER
        html.Div([
            html.Div([
                html.H1([
                    html.Span("May ", className="green"),
                    "Recap",
                    html.Button(
                        "⟳",
                        id="refresh-btn",
                        className="refresh-btn",
                        title="Refresh data",
                        n_clicks=0
                    ),
                ], className="h-title"),
                html.P("here's what Rishabh has listened to in May", className="h-sub"),
            ], className="h-left"),
            html.Div([
                html.Div(
                    '"Music washes away from the soul the dust of everyday life."',
                    className="quote"
                ),
                html.Div("– BERTHOLD AUERBACH", className="quote-auth"),
                html.Div("▎▍▌▋█▋▌▍▎▏▎▍▌▋▌▍▎", className="waveform"),
            ], className="h-right"),
        ], className="header"),

        # KPI ROW
        html.Div([
            html.Div([
                html.Div("TOTAL TRACKS PLAYED", className="kl"),
                html.Div(str(total_tracks), className="kv"),
                dcc.Graph(figure=fig_spark, config={"displayModeBar": False},
                          style={"height": "42px", "marginTop": "6px"}),
            ], className="kpi card"),
            html.Div([
                html.Div("UNIQUE ARTISTS", className="kl"),
                html.Div([html.Span(str(uniq_artists), className="kv"), html.Span("👥", className="ki")],
                         className="kv-row"),
            ], className="kpi card"),
            html.Div([
                html.Div("UNIQUE ALBUMS", className="kl"),
                html.Div([html.Span(str(uniq_albums), className="kv"), html.Span("💿", className="ki")],
                         className="kv-row"),
            ], className="kpi card"),
            html.Div([
                html.Div("TOTAL PLAY TIME", className="kl"),
                html.Div([html.Span(f"{tot_h}h {tot_m}m", className="kv"), html.Span("🕐", className="ki")],
                         className="kv-row"),
                html.Div(f"Avg. Track Duration: {avg_dur} mins", className="ks"),
            ], className="kpi card"),
        ], className="kpi-row"),

        # ROW 1 : Timeline | Genres | Artists
        html.Div([
            html.Div([
                html.Div("LISTENING OVER TIME", className="ct"),
                html.Div("Tracks played by day", className="cs"),
                dcc.Graph(figure=fig_time, config={"displayModeBar": False},
                          style={"height": "220px"}),
            ], className="card chart-card"),
            html.Div([
                html.Div("TOP GENRES", className="ct"),
                html.Div("By % of total play time", className="cs"),
                html.Div([
                    dcc.Graph(figure=fig_genre, config={"displayModeBar": False},
                              style={"height": "190px", "width": "170px", "flexShrink": "0"}),
                    html.Div(genre_legend, className="legend"),
                ], className="donut-row"),
            ], className="card chart-card"),
            html.Div([
                html.Div("TOP ARTISTS", className="ct"),
                html.Div("By total play time", className="cs"),
                html.Div(artist_rows, className="ar-list"),
            ], className="card chart-card"),
        ], className="row1"),

        # ROW 2 : Tracks | Album breakdown
        html.Div([
            html.Div([
                html.Div("TOP TRACKS", className="ct"),
                html.Div("By total play time", className="cs"),
                html.Div(tr_rows_html, className="tr-list"),
                html.Div("View All Tracks →", className="view-all"),
            ], className="card tracks-card"),
            html.Div([
                html.Div("ALBUM TYPE BREAKDOWN", className="ct"),
                html.Div("By % of total albums", className="cs"),
                html.Div([
                    dcc.Graph(figure=fig_alb, config={"displayModeBar": False},
                              style={"height": "165px", "width": "160px", "flexShrink": "0"}),
                    html.Div(alb_legend, className="legend"),
                ], className="donut-row"),
            ], className="card chart-card"),
        ], className="row2"),

        # FOOTER
        html.Div([
            html.Span("🎵", style={"fontSize": "17px", "color": "#1DB954", "marginRight": "8px"}),
            html.Span("Data is based on the tracks played in May.", className="ft"),
        ], className="footer"),

    ], className="dash")


# ============================================================
# DASH APP
# ============================================================

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div(id="page-content", children=build_dashboard()),
])


@app.callback(
    Output("page-content", "children"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_dashboard(_n):
    return build_dashboard()

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
