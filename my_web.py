import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
import warnings
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
sns.set_style('darkgrid')
matplotlib.rcParams['font.size'] = 14
matplotlib.rcParams['figure.figsize'] = (9, 5)
matplotlib.rcParams['figure.facecolor'] = '#00000000'
from keras.models import load_model
warnings.simplefilter(action='ignore', category=FutureWarning)
from datetime import datetime
#import mpld3
import streamlit.components.v1 as components


koneksi_mongodb = "mongodb+srv://midya123:1234567890@cluster0.wsuei7i.mongodb.net/test"
cluster = MongoClient(koneksi_mongodb)
db = cluster['iklim'] 
collection = db['dataiklim2'] 

data = collection.find()
df = pd.json_normalize(data)
dfIklim = pd.DataFrame(df)
# menghapus data id
df = dfIklim.drop(columns = ['_id'])
#mengubah tipe data tanggal
df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d-%m-%Y') 

df_geo = pd.DataFrame({'lat': [-8.75000], 'lon': [115.17000]})

option = st.sidebar.selectbox(
    'Silakan pilih:',
    ('Home','Exploratory Data Analysis','Prediksi Matahari','Prediksi Angin','Estimasi')
)

if option == 'Home' or option == '':
    st.write("""# Dashboard Prediksi Penyinaran Matahari dan Kecepatan Angin""") #menampilkan halaman utama
    st.text("Lokasi Pengambilan Sumber Data Penelitian")
    st.map(df_geo)
    st.text("Stasiun Metereologi Kelas I Ngurah Rai")
elif option == 'Prediksi Matahari':
    st.title("Prediksi Penyinaran Matahari") #menampilkan judul halaman 

    #upload file
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        dataframe = pd.read_csv(uploaded_file)
        st.write("Data telah berhasil di load, berikut adalah data yang digunakan untuk proses prediksi") 
        st.write(dataframe) 

        #dataframe['Tanggal'] = pd.to_datetime(dataframe['Tanggal'], format='%d-%m-%Y') 
        dataframe = dataframe.set_index('Tanggal')
        df2 = dataframe.dropna()

        #plot df asli
        st.write("Visualisasi Data")
        st.line_chart(df2)

        #creating lag 1 and rolling window feature
        df2['lag_1'] = df2['ss'].shift(1)
        rolling = df2['ss'].rolling(window=30)
        rolling_sum = rolling.sum()
        df2 = pd.merge(df2,rolling_sum,on='Tanggal')
        df2 = df2.dropna()
        
        #membagi x dan y
        from sklearn.model_selection import train_test_split
        X= df2.drop('ss_x', axis=1)
        y= df2['ss_x']
        
        #minmaxscaler
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)
        #scaled =pd.DataFrame(scaled)

        scaler2 = MinMaxScaler()
        y = y.to_numpy()
        test1 = y.reshape(-1,1)
        y = scaler2.fit_transform(test1)

        #X= X.to_numpy()
        n_features = 5
        n_seq = 1
        n_steps = 1
        X = X.reshape((X.shape[0], n_seq, n_steps, n_features))

        #Loading Model
        model = load_model('new_5feature_cnngru.h5')


        #Testing Model
        predictions = model.predict(X).flatten()


        #save prediction result
        pred = predictions.reshape(-1,1)
        pred = scaler2.inverse_transform(pred)
        

        #menampilkan hasil prediksi dalam bentuk tabel
        st.header('Prediksi rata-rata harian dengan CNN-BiLSTM')


        #menyimpan data aktual matahari
        df_pred = pd.DataFrame(pred, columns =['prediksi(jam)'])


        #menampilkan hasil prediksi
        st.subheader('Visualisasi Prediksi Intensitas Penyinaran Matahari')

        chart_width = st.expander(label="chart width").slider("", 10, 32, 14)

        fig2 = plt.figure(figsize = (chart_width,10))
        plt.plot(df_pred);

        #st.write(fig2)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        st.pyplot(fig2)

        st.write(df_pred) 

    else:
        st.text("Silahkan Upload file")    

elif option == 'Prediksi Angin':
    st.title("Prediksi Kecepatan Angin") #menampilkan judul halaman 

    #upload file
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        dataframe = pd.read_csv(uploaded_file)
        st.write("Data telah berhasil di load, berikut adalah data yang digunakan untuk proses prediksi") 
        st.write(dataframe) 

        #dataframe['Tanggal'] = pd.to_datetime(dataframe['Tanggal'], format='%d-%m-%Y') 
        dataframe = dataframe.set_index('Tanggal')
        df2 = dataframe.dropna()
        #df_angin = df['ff_avg']

        #plot df asli
        st.write("Visualisasi Data")
        st.line_chart(df2)

        #creating lag 1 and rolling window feature
        df2['lag_1'] = df2['ff_avg'].shift(1)
        rolling = df2['ff_avg'].rolling(window=30)
        rolling_sum = rolling.sum()
        df2 = pd.merge(df2,rolling_sum,on='Tanggal')
        df2 = df2.dropna()
        
        #membagi x dan y
        from sklearn.model_selection import train_test_split
        X= df2.drop('ff_avg_x', axis=1)
        y= df2['ff_avg_x']
        
        #minmaxscaler
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)
        #scaled =pd.DataFrame(scaled)

        scaler2 = MinMaxScaler()
        y = y.to_numpy()
        test1 = y.reshape(-1,1)
        y = scaler2.fit_transform(test1)

        #X= X.to_numpy()
        n_features = 5
        n_seq = 1
        n_steps = 1
        X = X.reshape((X.shape[0], n_seq, n_steps, n_features))

        #Loading Model
        model = load_model('fulldata_cnn_bilstm.h5')


        #Testing Model
        predictions = model.predict(X).flatten()


        #save prediction result
        pred = predictions.reshape(-1,1)
        pred = scaler2.inverse_transform(pred)
        

        #menampilkan hasil prediksi dalam bentuk tabel
        st.header('Prediksi rata-rata harian dengan CNN-BiLSTM')


        #menyimpan data aktual matahari
        df_pred = pd.DataFrame(pred, columns =['prediksi(m/s)'])


        #menampilkan hasil prediksi
        st.subheader('Visualisasi Prediksi Intensitas Penyinaran Matahari')

        chart_width = st.expander(label="chart width").slider("", 10, 32, 14)

        fig2 = plt.figure(figsize = (chart_width,10))
        plt.plot(df_pred);

        #st.write(fig2)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        st.pyplot(fig2)

        st.write(df_pred) 

    else:
        st.text("Silahkan Upload file") 

elif option == 'Exploratory Data Analysis':
    st.write("""## Visualisasi Data yang Digunakan Pada Proses Training Model""") #menampilkan judul halaman 

    #membuat variabel chart data yang berisi data dari dataframe
    #data berupa angka acak yang di-generate menggunakan numpy
    #data terdiri dari 2 kolom dan 20 baris
    chart_data = pd.DataFrame(df, 
        columns=['ss','ff_avg']
    )
    st.write("### Keterangan")
    st.text("ss = Penyinaran Matahari")
    st.text("ff_avg = Rata-Rata Kecepatan Angin")
    #menampilkan data dalam bentuk chart
    st.line_chart(chart_data)
    
#    from datetime import datetime
#    start_time = st.slider(
#    "When do you start?",
#        value=datetime(df,columns=['Tanggal']),
#        format="DD/MM/YY")
#    st.write("Start time:", start_time)
    #data dalam bentuk tabel
    chart_data

    st.write("### Histogram Persebaran Data")
    #menampilkan histogram penyinaran cahaya matahari
    x = pd.DataFrame(df, columns=['ss'])
    def plot_histogram(x):
        plt.hist(x, bins = 19, alpha=0.8, color = 'red', edgecolor = 'black')
    plt.title("Histogram dari frekuensi penyinaran cahaya matahari")
    plt.xlabel("Value")
    plt.ylabel("Frequency")

    fig= plot_histogram(x)

    #supaya tidak error
    st.set_option('deprecation.showPyplotGlobalUse', False)

    #menampilkan figure
    st.pyplot(fig)

    #menampilkan histogram kecepatan angin
    y = pd.DataFrame(df, columns=['ff_avg'])
    def plot_histogram(y):
        plt.hist(y, bins = 19, alpha=0.8, color = 'blue', edgecolor = 'black')
    plt.title("Histogram dari frekuensi rata-rata kecepatan angin")
    plt.xlabel("Value")
    plt.ylabel("Frequency")

    fig2= plot_histogram(y)

    #supaya tidak error
    st.set_option('deprecation.showPyplotGlobalUse', False)

    #menampilkan figure
    st.pyplot(fig2)      

    #PART DECOMPOSITION
    #st.subheader("Decomposition")
    #st.write(" ### Detected Anomalies Penyinaran Matahari dengan STL Decomposition")

    #tetep harus diisi dulu, pake interpolation
    #missing values imputation using interpolate penyinaran matahari
    #missing_values = ["", "na","--","NaN"]
    #data = df[['ss']].interpolate(method='linear',limit_direction='forward', axis=0, na_values=missing_values)

    #from statsmodels.tsa.seasonal import seasonal_decompose
    #series = data['ss']
    #result = seasonal_decompose(series, model='additive', period=30)
    #plt.title("Additive Decompose Penyinaran Matahari")
    #fig3= plot_histogram(result)
    #st.pyplot.rcParams.update({'figure.figsize': (12,10)})
    #st.pyplot(fig3)

    #fig3 = plt.figure(figsize=(30, 8))
    #_ = plt.plot_date(dfsensorIndexed.index, dfsensorIndexed.iloc[:, 0], linestyle='--', zorder=1)
    #_ = plt.scatter(dfanomali.index, dfanomali.iloc[:, 0], color='r', marker='X', zorder=2, s=250)
    #_ = plt.xticks(rotation=270)
    #series = data['ss']
    #result = seasonal_decompose(series, model='additive', period=30)
    #_ = plt.scatter(df['Tanggal'], series, color='orange', marker='o', zorder=2, s=250)
    #_ = plt.xlabel('Date')
    #_ = plt.ylabel('Value')
    #_ = plt.title('STL decomposition  Anomalies')
    #_ = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    #st.pyplot(fig3)


    #st.write(" ### Detected Anomalies Kecepatan Angin dengan STL Decomposition")

    #tetep harus diisi dulu, pake interpolation
    #missing values imputation using interpolate penyinaran matahari
    #missing_values = ["", "na","--","NaN"]
    #data_ff = df[['ff_avg']].interpolate(method='linear',limit_direction='forward', axis=0, na_values=missing_values)

    #from statsmodels.tsa.seasonal import seasonal_decompose
    #series = data['ss']
    #result = seasonal_decompose(series, model='additive', period=30)
    #plt.title("Additive Decompose Penyinaran Matahari")
    #fig3= plot_histogram(result)
    #st.pyplot.rcParams.update({'figure.figsize': (12,10)})
    #st.pyplot(fig3)

    #fig3 = plt.figure(figsize=(30, 8))
    #_ = plt.plot_date(dfsensorIndexed.index, dfsensorIndexed.iloc[:, 0], linestyle='--', zorder=1)
    #_ = plt.scatter(dfanomali.index, dfanomali.iloc[:, 0], color='r', marker='X', zorder=2, s=250)
    #_ = plt.xticks(rotation=270)
    #series = data_ff['ff_avg']
    #result = seasonal_decompose(series, model='additive', period=30)
    #_ = plt.scatter(df['Tanggal'], series, color='green', marker='o', zorder=2, s=250)
    #_ = plt.xlabel('Date')
    #_ = plt.ylabel('Value')
    #_ = plt.title('STL decomposition  Anomalies')
    #_ = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    #st.pyplot(fig3)

elif option == 'Estimasi':
    st.write("""## Estimasi Kecepatan Angin""") #menampilkan judul halaman 
    a = st.number_input('Masukkan Suhu Maksimum', key = "a")
    b = st.number_input('Masukkan Intensitas Penyinaran Matahari', key = "b")
    c = st.number_input('Masukkan Maksimum Kecepatan Angin', key = "c")
    
    import pickle
    regression = pickle.load(open("C:/python/Model_TA/streamlit/estimasi_angin.pickle", "rb"))

    estimation = regression.predict([[a, b, c]])
    st.text("Hasil Estimasi Kecepatan Angin (m/s) :")
    if a == 0 or b == 0 or c==0:
        st.text("0")
    else:
        st.text(estimation)


    st.write(""" """) 
    #estimasi matahari dengan suhu maksimum, suhu rata-rata, curah hujan
    st.write("""## Estimasi Intensitas Penyinaran Matahari""") 
    d = st.number_input('Masukkan Suhu Maksimum', key = "d")
    e = st.number_input('Masukkan Suhu Rata-Rata', key = "e")
    f = st.number_input('Masukkan Curah Hujan', key = "f")
    
    import pickle
    regression_sun = pickle.load(open("C:/python/Model_TA/streamlit/estimasi_matahari.pickle", "rb"))

    estimation_sun = regression_sun.predict([[d, e, f]])
    st.text("Hasil Estimasi Penyinaran Matahari(jam) :")
    if d == 0 or e == 0 or f==0:
        st.text("0") 
    else:
        st.text(estimation_sun)