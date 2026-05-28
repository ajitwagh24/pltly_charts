import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------
# Load data
# -------------------------------
df = pd.read_excel("C://Users//WaghA4//Downloads//baseline_output (18).xlsx",
    sheet_name=0
)

# -------------------------------
# Step 1: Clean & Rename columns
# -------------------------------
df.columns = df.columns.str.strip()

df.rename(columns=lambda x: x.replace("(Organisational)", "")
                           .replace("(Contractual)", "")
                           .strip(), inplace=True)

df.rename(columns={
    "Total_Respondents": "Respondents",
    "Customer Needs": "Customer Focus",
    "Challenge Status Quo": "Challenge Status",
    "Manager Effectiveness > Manager Helps To Improve My Performance": "Feedback"
}, inplace=True)

# -------------------------------
# Step 2: Wide → Long format
# -------------------------------
behaviour_cols = ["Customer Focus", "Empowerment", "Challenge Status", "Feedback"]

df = df.melt(
    id_vars=["Market", "Respondents", "Sample_flag"],
    value_vars=behaviour_cols,
    var_name="Behaviour",
    value_name="Score"
)

# -------------------------------
# Step 3: Create Impact
# -------------------------------
market_avg = df.groupby("Market")["Score"].mean().rename("Market_Avg")
df = df.merge(market_avg, on="Market")

df["Impact"] = df["Score"] - df["Market_Avg"]

# -------------------------------
# Step 4: Quadrant lines
# -------------------------------
x_mean = df["Score"].mean()
y_mean = df["Impact"].mean()

# -------------------------------
# Step 5: Add Quadrant column ✅ (IMPORTANT)
# -------------------------------
def assign_quadrant(row):
    if row["Score"] >= x_mean and row["Impact"] >= y_mean:
        return "High Perf / High Impact"
    elif row["Score"] < x_mean and row["Impact"] >= y_mean:
        return "Low Perf / High Impact"
    elif row["Score"] < x_mean and row["Impact"] < y_mean:
        return "Low Perf / Low Impact"
    else:
        return "High Perf / Low Impact"

df["Quadrant"] = df.apply(assign_quadrant, axis=1)

# -------------------------------
# ✅ SAVE FINAL DATASET
# -------------------------------
df.to_excel(
    "quadrant_output.xlsx",
    index=False
)

# Optional summary (VERY USEFUL)
summary = df.groupby(["Behaviour", "Quadrant"]) \
            .size() \
            .reset_index(name="Count")

summary.to_excel(
    "C://Users//WaghA4//Downloads//quadrant_summary.xlsx",
    index=False
)

# -------------------------------
# Step 6: Plot
# -------------------------------
fig = px.scatter(
    df,
    x="Score",
    y="Impact",
    color="Market",
    size="Respondents",
    size_max=20
)

# -------------------------------
# ✅ Clean Hover (only 4 fields)
# -------------------------------
# fig.update_traces(
#     hovertemplate=
#     "<b>Market:</b> %{customdata[0]}<br>" +
#     "<b>Behaviour:</b> %{customdata[1]}<br>" +
#     "<b>Score:</b> %{x:.2f}<br>" +
#     "<b>Impact:</b> %{y:.2f}<extra></extra>",
#     customdata=df[["Market", "Behaviour"]]
# )

fig = px.scatter(
    df,
    x="Score",
    y="Impact",
    color="Market",
    #size="Respondents",
    size_max=20,
    hover_name="Behaviour",
    hover_data={
        "Market": True,
        "Score":":.2f",
        "Impact":":.2f"
    }
)


# -------------------------------
# Quadrant lines
# -------------------------------
fig.add_vline(x=x_mean, line_dash="dash", line_color="black")
fig.add_hline(y=y_mean, line_dash="dash", line_color="black")

# -------------------------------
# Quadrant shading
# -------------------------------
fig.add_shape(type="rect", x0=df["Score"].min(), x1=x_mean, y0=y_mean, y1=df["Impact"].max(),
              fillcolor="lightgreen", opacity=0.08, layer="below", line_width=0)

fig.add_shape(type="rect", x0=x_mean, x1=df["Score"].max(), y0=y_mean, y1=df["Impact"].max(),
              fillcolor="lightblue", opacity=0.08, layer="below", line_width=0)

fig.add_shape(type="rect", x0=df["Score"].min(), x1=x_mean, y0=df["Impact"].min(), y1=y_mean,
              fillcolor="lightpink", opacity=0.08, layer="below", line_width=0)

fig.add_shape(type="rect", x0=x_mean, x1=df["Score"].max(), y0=df["Impact"].min(), y1=y_mean,
              fillcolor="lightyellow", opacity=0.08, layer="below", line_width=0)

# -------------------------------
# Behaviour centroid labels
# -------------------------------
cent = df.groupby("Behaviour", as_index=False)[["Score", "Impact"]].mean()

fig.add_trace(
    go.Scatter(
        x=cent["Score"],
        y=cent["Impact"],
        mode="text",
        text=cent["Behaviour"],
        textposition="top center",
        textfont=dict(size=13, color="black"),
        showlegend=False
    )
)

# -------------------------------
# Styling
# -------------------------------
fig.update_traces(marker=dict(line=dict(width=1, color="white")))

fig.update_layout(
    title="Quadrant: Performance vs Relative Impact (Market Clustering View)",
    xaxis_title="Score (Performance)",
    yaxis_title="Relative Impact",
    template="plotly_white",
    legend_title="Market",
    hoverlabel=dict(bgcolor="white", font_size=12)
)

# -------------------------------
# Show Plot
# -------------------------------
fig.write_html("C://Users//WaghA4//Downloads//index.html")
#fig.show()