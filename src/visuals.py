import plotly.express as px
import plotly.graph_objects as go

def create_historical_fcf_chart(df_hist):
    fig = px.bar(
        df_hist,
        x="Year",
        y="Free Cash Flow",
        title="Historical Free Cash Flow",
        labels={"Free Cash Flow": "FCF (millions)", "Year": ""},
        color_discrete_sequence=["#FF1744"]
    )
    fig.update_layout(
        plot_bgcolor="#181c24",
        paper_bgcolor="#232936",
        font=dict(color="#e0e6ed"),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        hoverlabel=dict(bgcolor="#fff", font_size=12, font_color="#232936")
    )
    return fig

def create_projected_fcf_chart(df_proj):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_proj["Year"],
        y=df_proj["Projected FCF"],
        name="Projected FCF",
        marker_color="#90caf9",
        opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=df_proj["Year"],
        y=df_proj["Discounted FCF"],
        name="Discounted FCF",
        mode="lines+markers",
        marker=dict(color="#FF1744", size=8),
        line=dict(width=3, color="#FF1744")
    ))
    fig.update_layout(
        title="Projected vs Discounted FCF",
        xaxis_title="",
        yaxis_title="FCF (millions)",
        plot_bgcolor="#181c24",
        paper_bgcolor="#232936",
        font=dict(color="#e0e6ed"),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        hoverlabel=dict(bgcolor="#fff", font_size=12, font_color="#232936")
    )
    return fig
