import unittest
from littlenn.model import Sequential
from littlenn.layers import Dense, Dropout

model = Sequential(input_size=100)
model.add(Dense(256, "relu"))
model.add(Dropout(0.8))
model.add(Dense(128, "relu"))
model.summary()