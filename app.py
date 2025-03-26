import streamlit as st
import pandas as pd
import plotly.express as px

# Title và mô tả
st.title('🌤️ Dashboard Phân tích Chất lượng Không khí')
st.markdown('Ứng dụng tương tác hiển thị dữ liệu AQI và các yếu tố môi trường liên quan.')

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('aqi_selected_cities.csv', parse_dates=['timestamp'])
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    ## Tiền xử lý dữ liệu
    # Chuyển cột temperature sang kiểu string, loại bỏ "°C" và chuyển về kiểu số float
    data['temperature'] = data['temperature'].astype(str).str.replace('°C', '', regex=False)
    data['temperature'] = pd.to_numeric(data['temperature'], errors='coerce')

    # Tương tự với cột humidity (nếu chứa dấu "%")
    data['humidity'] = data['humidity'].astype(str).str.replace('%', '', regex=False)
    data['humidity'] = pd.to_numeric(data['humidity'], errors='coerce')

    # Tương tự với cột wind_speed " km/h"
    data['wind_speed'] = data['wind_speed'].astype(str).str.replace(' km/h', '', regex=False)
    data['wind_speed'] = pd.to_numeric(data['wind_speed'], errors='coerce')

    # Chuyển đổi đơn vị CO cho dữ liệu trước ngày 2025-03-07
    data.loc[(data["city"] == "Hà Nội") & (data["timestamp"] <= "2025-03-07"), "co"] = (
    data["co"] / 1145).round(1)

    ## Xử lý dữ liệu thiếu
    # Điền giá trị NaN bằng trung bình của từng cột
    cols_to_fill = ["so2", "co", "pm10", "o3", "no2", "pm25"]
    for col in cols_to_fill:
        data[col] = data[col].fillna(data.groupby("city")[col].transform("mean")).round(1)

    return data

df = load_data()

# Sidebar - Filters
st.sidebar.header('Chọn tham số')
city = st.sidebar.selectbox('Chọn thành phố:', df['city'].unique())
date_range = st.sidebar.date_input("Khoảng thời gian phân tích:", [df['timestamp'].min().date(), df['timestamp'].max().date()])

# Lọc dữ liệu
start_date, end_date = date_range
filtered_df = df[(df['city'] == city) & (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]

# Biểu đồ AQI theo thời gian
st.header('📈 AQI theo thời gian')
fig_aqi = px.area(filtered_df, x='timestamp', y='aqi', title='Chỉ số AQI theo thời gian', color_discrete_sequence=['#00A8E8'])
st.plotly_chart(fig_aqi)

# Hiển thị các chỉ số ô nhiễm
st.header('📊 Chỉ số chất lượng không khí chi tiết')
pollutants = ['pm25', 'pm10', 'no2', 'o3', 'so2', 'co']
selected_pollutant = st.selectbox('Chọn chỉ số:', pollutants)

fig_pollutant = px.area(filtered_df, x='timestamp', y=selected_pollutant, title=f'Chỉ số {selected_pollutant.upper()} theo thời gian', color_discrete_sequence=['#72B01D'])
st.plotly_chart(fig_pollutant)

# Tương quan giữa AQI và yếu tố thời tiết
st.header('🔍 Tương quan AQI và yếu tố thời tiết')
y_factor = st.selectbox('Chọn yếu tố thời tiết:', ['temperature', 'humidity', 'wind_speed'])

fig_corr = px.scatter(
    filtered_df, 
    x=y_factor, 
    y='aqi', 
    opacity=0.6,  # Làm trong suốt để tránh rối mắt
    trendline="ols",  # Thêm đường xu hướng
    color_discrete_sequence=['#FFA500'],  # Màu cam nổi bật
    title=f'Tương quan giữa AQI và {y_factor}'
)
fig_corr.update_layout(xaxis_showgrid=True, yaxis_showgrid=True)  # Hiển thị lưới

st.plotly_chart(fig_corr)


# Hiển thị dữ liệu thô
st.header('📋 Bảng dữ liệu chi tiết')

# Ẩn cột icon nếu tồn tại
if 'icon' in filtered_df.columns:
    display_df = filtered_df.drop(columns='icon')
else:
    display_df = filtered_df

# Hiển thị bảng sau xử lý
st.dataframe(display_df.reset_index(drop=True), use_container_width=True)


# Footer
st.markdown('---')
st.caption('Dashboard được xây dựng bằng Streamlit. Copyright DoThang 2025.')
