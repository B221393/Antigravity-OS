import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Pareto Plot", page_icon="📉")
st.title("📉 Pareto Analysis Tool")

st.write("Upload CSV (Column 1: Category, Column 2: Value) or enter manual data.")

input_mode = st.radio("Input Source", ["Manual", "CSV"])

data = {}

if input_mode == "Manual":
    txt = st.text_area("Data (Name, Value per line)", "Defect A, 50\nDefect B, 30\nDefect C, 10\nDefect D, 5")
    for line in txt.split('\n'):
        if ',' in line:
            parts = line.split(',')
            try:
                data[parts[0].strip()] = float(parts[1].strip())
            except: pass
else:
    f = st.file_uploader("Upload CSV", type="csv")
    if f:
        df = pd.read_csv(f)
        try:
            # Assume first two columns
            for idx, row in df.iterrows():
                data[str(row[0])] = float(row[1])
        except:
            st.error("CSV format error. Ensure 2 columns.")

if data:
    df = pd.DataFrame(list(data.items()), columns=['Category', 'Value'])
    df = df.sort_values('Value', ascending=False)
    
    df['Cumulative'] = df['Value'].cumsum()
    df['Cumulative%'] = 100 * df['Cumulative'] / df['Value'].sum()
    
    st.dataframe(df)
    
    # Pareto Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Category'], y=df['Value'], name='Value'))
    fig.add_trace(go.Scatter(x=df['Category'], y=df['Cumulative%'], name='Cumulative %', yaxis='y2', mode='lines+markers'))
    
    fig.update_layout(
        title='Pareto Chart',
        yaxis=dict(title='Value'),
        yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 110]),
        template='plotly_dark'
    )
    
    st.plotly_chart(fig)
