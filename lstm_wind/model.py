import pandas as pd
from lstm_wind.functions import prepro
from lstm_wind.config import config
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Input
from tensorflow import keras
import joblib


from pathlib import Path
BASE_DIR = Path(__file__).resolve(strict=True).parent


def train():
	print("############")
	print("loading data")
	print(" ")
	file = Path(BASE_DIR).joinpath(config.data_path)



	all_data = pd.read_csv(file,sep=";",decimal=",")
	trunc_days = config.days
	trunc_mins = trunc_days*24*60

	my_data = pd.DataFrame(prepro(all_data,config.station),columns = ["y"]).values


	n_future = config.n_future 
	n_past = config.n_past
	y_col = my_data.shape[1]-1

	data_X = []
	data_Y = []
	data_p_X = []
	data_p_Y = []

	for i in range(n_past, len(my_data) - n_future + 1):
	    data_X.append(my_data[i - n_past:i, 0:my_data.shape[1]])
	    data_Y.append(my_data[i:i + n_future, y_col])
	data_X, data_Y = np.array(data_X), np.array(data_Y)


	train_X, test_X, train_Y, test_Y = train_test_split(data_X, data_Y, test_size=0.33, random_state=42, shuffle=False)


	keras.backend.clear_session()
	lstm_model = Sequential()
	lstm_model.add(Input(shape=[train_X.shape[-2], train_X.shape[-1]]))
	lstm_model.add(Dense(10))
	lstm_model.add(LSTM(100, activation='tanh', input_shape=(train_X.shape[-1], train_X.shape[-2]), return_sequences=True))
	lstm_model.add(Dense(30))
	lstm_model.add(Dropout(0.2))
	lstm_model.add(LSTM(100, activation='tanh', return_sequences=False))
	lstm_model.add(Dense(10))
	lstm_model.add(Dense(train_Y.shape[1]))
	lstm_model.compile(optimizer='adam', loss='mape')
	history = lstm_model.fit(train_X, train_Y, epochs = config.epochs, batch_size = config.batch, validation_data=(test_X, test_Y), verbose=0)

	joblib.dump(lstm_model, Path(BASE_DIR).joinpath(config.model_file))
	keras.backend.clear_session()


	outputs = {'mape_train': history.history['loss'][-1],
	           'mape_val': history.history['val_loss'][-1],
	           'epochs': config.epochs,
	           'batch_size': config.batch
               
               
    }
	return outputs    

	
	

def predict(inputs):

	lstm_model = joblib.load(Path(BASE_DIR).joinpath(config.model_file))
	outputs = lstm_model.predict(np.array(inputs).reshape(-1,1))
    
	return pd.Series(outputs[-1]).to_dict()









