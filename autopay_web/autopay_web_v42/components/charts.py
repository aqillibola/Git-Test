import plotly.express as px
import streamlit as st


def card_section_start(title, subtitle=""):
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='chart-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='chart-sub'>{subtitle}</div>", unsafe_allow_html=True)


def card_section_end():
    st.markdown("</div>", unsafe_allow_html=True)


def chart_card_open():
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)


def chart_card_close():
    st.markdown("</div>", unsafe_allow_html=True)


def service_pie(df, colors, title):
    fig = px.pie(
        df,
        names=df.columns[0],
        values=df.columns[1],
        hole=0.58,
        color=df.columns[0],
        color_discrete_map=colors,
    )
    fig.update_traces(
        textinfo="percent+label",
        textfont_size=11,
        pull=[0.03] + [0 for _ in range(len(df)-1)],
        sort=False,
    )
    fig.update_layout(
        title=title,
        height=320,
        margin=dict(l=10, r=10, t=70, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.24, xanchor="center", x=0.5, title=""),
        paper_bgcolor="#F7FAFC",
        plot_bgcolor="#F7FAFC",
        font=dict(color="#1F2340"),
        transition=dict(duration=700, easing="cubic-in-out"),
    )
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode="hide")
    return fig


def service_bar(df, colors, title, x_title, y_title):
    fig = px.bar(
        df,
        x=df.columns[0],
        y=df.columns[1],
        color=df.columns[0],
        color_discrete_map=colors,
        text=df.columns[1],
    )
    fig.update_traces(
        textposition="outside",
        marker_line_width=0,
        opacity=0.92,
        cliponaxis=False,
        hovertemplate="%{x}<br>%{y:,.2f}<extra></extra>",
    )
    fig.update_layout(
        title=title,
        height=320,
        margin=dict(l=10, r=10, t=85, b=20),
        showlegend=False,
        xaxis_title=x_title,
        yaxis_title=y_title,
        paper_bgcolor="#F7FAFC",
        plot_bgcolor="#F7FAFC",
        font=dict(color="#1F2340"),
        transition=dict(duration=700, easing="cubic-in-out"),
    )
    return fig


def hourly_line(df, x_col, y_col, text_col, title, x_title, y_title, line_color, marker_color):
    fig = px.line(df, x=x_col, y=y_col, markers=True)
    fig.update_traces(
        mode="lines+markers+text",
        text=df[text_col],
        textposition="top center",
        line=dict(color=line_color, width=3, shape="spline"),
        marker=dict(color=marker_color, size=7),
    )
    fig.update_layout(
        title=title,
        height=320,
        margin=dict(l=10, r=10, t=70, b=20),
        xaxis_title=x_title,
        yaxis_title=y_title,
        paper_bgcolor="#F7FAFC",
        plot_bgcolor="#F7FAFC",
        font=dict(color="#1F2340"),
        transition=dict(duration=700, easing="cubic-in-out"),
    )
    return fig
