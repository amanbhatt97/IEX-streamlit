# %%
######################
#### dependencies ####
######################

# dataframe operations
import pandas as pd
import numpy as np
import pickle
import requests, json
from datetime import *
import streamlit as st
import plotly.graph_objects as go

# visualization
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (10, 4)    # setting default figure size

# ignore warnings
import warnings
warnings.filterwarnings('ignore')

# setting timezone
import sys, time, os
os.environ['TZ'] = 'Asia/Calcutta'
time.tzset() 



# %%
start_date = datetime.now().date() + timedelta(days=-25)   
end_date =  datetime.now().date() + timedelta(days=2)   

start_date_str = start_date.strftime("%d-%m-%Y")    
end_date_str = end_date.strftime("%d-%m-%Y")


file_path = '/home/shikhar/dam_data'
if os.path.exists(file_path):
    data = pd.read_pickle('/home/shikhar/dam_data')
    rtm_data = pd.read_pickle('/home/shikhar/rtm_data')

else:    
    # %% [markdown]
    # ### Day-Ahead

    # %%
    def get_token(base_url):
        """ This method returns access token to fetch dam, rtm data """
        try:
            url = base_url + 'login'
            email = 'apiuser2@epf-test.com'
            password = '123456'
            data = {'email': email, 'password': password}

            req = requests.post(url=url, data=data, verify=True).json()
            token = req['access_token']
            return token
        
        except Exception as e:
            print("Error occurred while retrieving the access token:", str(e))


    def get_dam_api(base_url, start_date_str, end_date_str, token):
        """ This method makes GET request to api endpoint to get dam data """ 
        try:
            url = base_url + 'getMarketVolume'
            headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

            params = {
                "start_date": start_date_str,
                "end_date": end_date_str,
            }

            r = requests.get(url=url, headers=headers, params=params)
            return r.json()
        
        except Exception as e:
            print("Error occurred while retrieving data:", str(e))   

            
    def get_dam_actual():
        """ This method fetches actual dam data, process and save it """
        
        base_url = "https://api.energy-price.climate-connect.com/api/"
        token = get_token(base_url)
        data_dict = get_dam_api(base_url, start_date_str, end_date_str, token)
        df = pd.DataFrame(data_dict['data'])

        df = df[['mcp']]
        for column in df.columns:
            df[column] = pd.to_numeric(df[column])

        df = df.rename(columns={'mcp': 'mcp_dam'})

        dates = pd.date_range(start=start_date, end=end_date, freq='15min')[:-1]
        dam = pd.DataFrame({'datetime': dates})
        dam = pd.concat([dam, df], axis=1).dropna()
        
        return dam

    # %%
    dam_actual = get_dam_actual()

    # %%
    dam_actual = dam_actual.rename(columns = {'mcp_dam':'actual'})

    # %%
    base_url = "https://api.energy-price.climate-connect.com/api/"
    def getToken():
        try:
            url = base_url + 'login'
            email = 'technology@climate-connect.com'
            password = 'tech@123'

            data = {'email': email, 'password': password}
            req = requests.post(url = url, data = data, verify = True).json()
            token = json.loads(json.dumps(req))
            return token
        except Exception as e:
            raise e

    def getData():
        try:
            url = base_url + 'getPriceForecast'
            t = getToken()
            token = t['access_token']
            headers = {'Authorization': 'Bearer ' + str(token), 'Content-Type': 'application/json'}
            params = {"start_date":start_date_str,
            "end_date":end_date_str,
            }
            r = requests.get(url = url, headers = headers, params = params)
            return r.json()
        except Exception as e:
            raise e

    # %%
    dam_forecast = pd.DataFrame(getData()['data'])
    dam_forecast = dam_forecast[dam_forecast['label'] == 'forecast']

    # %%
    dam_forecast['time'] = dam_forecast['time_block'].str.split('-').str[0]

    # Merge date and time to create the datetime column
    dam_forecast['datetime'] = pd.to_datetime(dam_forecast['date'] + ' ' + dam_forecast['time'], format='%d-%m-%Y %H:%M')
    dam_forecast = dam_forecast[['datetime', 'price']]
    dam_forecast = dam_forecast.rename(columns = {'price': 'forecast'})

    # %%
    data = pd.merge(dam_actual, dam_forecast, on='datetime', how='right')

    # %%
    data.set_index('datetime').plot()

    # %% [markdown]
    # ### Real-Time

    # %%
    def get_rtm_api(base_url, start_date_str, end_date_str, token):
        """ This method makes GET request to api endpoint to get rtm data """ 
        try:
            url = base_url + 'getRTMMarketVolume'
            headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

            params = {
                "start_date": start_date_str,
                "end_date": end_date_str,
            }

            r = requests.get(url=url, headers=headers, params=params)
            return r.json()
        
        except Exception as e:
            print("Error occurred while retrieving data:", str(e))

    # %%
    def get_rtm_actual():
        """ This method fetches actual rtm data, process and save it """

        base_url = "https://api.energy-price.climate-connect.com/api/"
        token = get_token(base_url)
        data_dict = get_rtm_api(base_url, start_date_str, end_date_str, token)
        df = pd.DataFrame(data_dict['data'])

        df['time'] = df['time_block'].str.split('-').str[0]
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%d-%m-%Y %H:%M')
        
        df = df[['datetime', 'mcp']]

        for column in df.columns[1:]:
            df[column] = pd.to_numeric(df[column])

        df = df.rename(columns={'mcp': 'actual'})

        return df

    # %%
    rtm_actual = get_rtm_actual()

    # %%
    def getData():
        try:
            url = base_url + 'getRTMPriceForecast'
            t = getToken()
            token = t['access_token']
            headers = {'Authorization': 'Bearer ' + str(token), 'Content-Type': 'application/json'}
            params = {"start_date":start_date_str,
            "end_date":end_date_str,
            }
            r = requests.get(url = url, headers = headers, params = params)
            return r.json()
        except Exception as e:
            raise e

    # %%
    rtm_forecast = pd.DataFrame(getData()['data'])

    # %%
    rtm_forecast['time'] = rtm_forecast['time_block'].str.split('-').str[0]

    # Merge date and time to create the datetime column
    rtm_forecast['datetime'] = pd.to_datetime(rtm_forecast['date'] + ' ' + rtm_forecast['time'], format='%d-%m-%Y %H:%M')
    rtm_forecast = rtm_forecast[['datetime', 'rtm_priceforecast']]
    rtm_forecast = rtm_forecast.rename(columns = {'rtm_priceforecast': 'forecast'})

    # %%
    rtm_data = pd.merge(rtm_actual, rtm_forecast, on='datetime', how='right')

    # data.dropna(inplace=True)
    # rtm_data.dropna(inplace=True)

# %% [markdown]
# ### Dashboard

# %%
# Set page config
st.set_page_config(page_title='IEX Price Forecasting', layout='wide')

st.sidebar.info("Welcome to the dashboard! Explore the Day-Ahead and Real-Time Market data.")

# Define page layout
col1, col2 = st.columns([1, 4])
with col2:
    st.title('IEX Price Forecasting Dashboard')

# %%
# Create date range selectboxes
plot_list = ['Day-Ahead Market', 'Real-Time Market']
with st.sidebar:
    # Apply styling to sidebar
    st.sidebar.markdown('<h2 style="text-align: center;">Market Type</h2>', unsafe_allow_html=True)
    # st.markdown("---")
    plot_type_selected = st.selectbox('Select Market Type', plot_list, index=0)

# %%

# Display chart for selected date range
if plot_type_selected == 'Day-Ahead Market':
        date_list = pd.date_range(start=start_date, end=datetime.now()+timedelta(days=1), freq='D').date
        with st.sidebar:
            st.sidebar.markdown('<h2 style="text-align: center;">Date Range</h2>', unsafe_allow_html=True)
            start_date_selected = st.selectbox("Start Date", date_list, index=0)
            end_date_selected = st.selectbox("End Date", date_list, index=len(date_list)-1)
        data_filtered = data[(data.datetime.dt.date >= start_date_selected) & (data.datetime.dt.date <= end_date_selected)]
        if data_filtered.empty:
            st.header("Oops! End date should be more than start date.")
            st.subheader("Select the correct daterange.")
        else:
            chart_data = data_filtered[['datetime', 'forecast', 'actual']].set_index('datetime')
            
            fig = go.Figure()

            # Add forecast and actual data as separate traces

            fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['actual'], name='Actual', mode='lines',
                                # hovertemplate='Actual: %{y:.2f}',
                                line=dict(width=2,color='green'),  # Increase line width
                                marker=dict(size=6)))  # Reduce marker size

            fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['forecast'], name='Forecast', mode='lines',
                                    #  hovertemplate='Forecast: %{y:.2f}',
                                    line=dict(width=2,color='orange'),  # Increase line width
                                    marker=dict(size=6)))  # Reduce marker size
            
            # Add vertical lines for every date between the selected start and end dates
            date_range = pd.date_range(start=start_date_selected+timedelta(days=1), end=end_date_selected, freq='D')
            for date in date_range:
                fig.add_vline(x=date, line_dash="dot", line_color="black")

            # Update layout to display values on hover
            fig.update_layout(title='Day-Ahead Price Forecast vs Actual', xaxis_title='Date', yaxis_title='Price',
                            hovermode='x unified', showlegend=True, width=1100, height=500)

            # Calculate MAPE for each date
            data_filtered['mape'] = abs((data_filtered['actual'] - data_filtered['forecast']) / data_filtered['actual']) * 100
            mape_by_date = data_filtered.groupby(data_filtered['datetime'].dt.date)['mape'].mean()

            # Add MAPE annotations to the plot
            for date, mape_value in mape_by_date.items():
                if not pd.isnull(mape_value):  # Check if MAPE value is not NaN
                    date_average = data_filtered[data_filtered['datetime'].dt.date == date]['datetime'].mean()
                    fig.add_annotation(
                        x=date_average,
                        y=chart_data['forecast'].max() * 0.15,  # Adjust the Y position of the annotation to avoid overlap
                        text=f"MAPE: {mape_value:.2f}%",
                        showarrow=False,
                        font=dict(color="green", size=12),
                    )

            st.plotly_chart(fig)
            st.subheader("Forecast vs Actual Values")
            #data_filtered = data_filtered.sort_values(by='datetime', ascending=False).dropna(subset=['forecast', 'actual'], how='all')
            st.dataframe(data_filtered.set_index('datetime')[['actual', 'forecast']])
            

if plot_type_selected == 'Real-Time Market':
        date_list = pd.date_range(start=start_date, end=datetime.now()+timedelta(minutes=80), freq='D').date
        with st.sidebar:
            st.markdown("---")
            st.sidebar.markdown('<h2 style="text-align: center;">Date Range</h2>', unsafe_allow_html=True)
            start_date_selected = st.selectbox("Start Date", date_list, index=0)
            end_date_selected = st.selectbox("End Date", date_list, index=len(date_list)-1)
        rtm_filtered = rtm_data[(rtm_data.datetime.dt.date >= start_date_selected) & (rtm_data.datetime.dt.date <= end_date_selected)]
        if rtm_filtered.empty:
            st.header("Oops! End date should be more than start date.")
            st.subheader("Select the correct daterange.")
        else:
            chart_data = rtm_filtered[['datetime', 'forecast', 'actual']].set_index('datetime')
            fig = go.Figure()

            # Add forecast and actual data as separate traces
            fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['actual'], name='Actual', mode='lines',
                                    #  hovertemplate='Actual: %{y:.2f}',
                                    line=dict(width=2,color='green'),  # Increase line width
                                    marker=dict(size=6)))  # Reduce marker size

            fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['forecast'], name='Forecast', mode='lines',
                                    #  hovertemplate='Forecast: %{y:.2f}',
                                    line=dict(width=2,color='orange'),  # Increase line width
                                    marker=dict(size=6)))  # Reduce marker size
            
            # Add vertical lines for every date between the selected start and end dates
            date_range = pd.date_range(start=start_date_selected, end=end_date_selected, freq='D')
            for date in date_range:
                fig.add_vline(x=date, line_dash="dot", line_color="black")

            # Update layout to display values on hover
            fig.update_layout(title='Real-Time Price Forecast vs Actual', xaxis_title='Date', yaxis_title='Price',
                            hovermode='x unified', showlegend=True, width=1100, height=500)
            
            # Calculate MAPE for each date
            rtm_filtered['mape'] = abs((rtm_filtered['actual'] - rtm_filtered['forecast']) / rtm_filtered['actual']) * 100
            mape_by_date = rtm_filtered.groupby(rtm_filtered['datetime'].dt.date)['mape'].mean()
            # Add MAPE annotations to the plot
            for date, mape_value in mape_by_date.items():
                if not pd.isnull(mape_value):  # Check if MAPE value is not NaN
                    date_average = rtm_filtered[rtm_filtered['datetime'].dt.date == date]['datetime'].mean()
                    fig.add_annotation(
                        x=date_average,
                        y=chart_data['forecast'].max() * 0.1,  # Adjust the Y position of the annotation to avoid overlap
                        text=f"MAPE: {mape_value:.2f}%",
                        showarrow=False,
                        font=dict(color="green", size=12),
                    )

            st.plotly_chart(fig)
            st.subheader("Forecast vs Actual Values")
            rtm_filtered = rtm_filtered.sort_values(by='datetime', ascending=False).dropna(subset=['forecast', 'actual'], how='all')
            st.dataframe(rtm_filtered.set_index('datetime')[['actual', 'forecast']]) 


with st.container():
    st.markdown("---")
    st.subheader("About the Dashboard")
    st.markdown("This dashboard provides Forecast V/S Actual prices for the IEX Day-Ahead and Real-Time Markets.")
    st.markdown("You can select the market type, date range, and explore the price forecast vs. actual data.")
    st.markdown("---")
    st.subheader("Contact Information")
    st.markdown("For more information, please contact at: [amanbhatt.1997.ab@gmail.com](mailto:support@example.com)")
