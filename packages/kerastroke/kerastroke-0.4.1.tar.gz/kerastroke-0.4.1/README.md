# Stroke
While reading about the concept of dropout, I thought about removing weights between layers instead of removing data. So I created a custom Keras callback called "Stroke", which randomizes a set percentage of weights in a model or one of its layers, sort of replicating what happens when a human has a stroke. The goal of the Stroke callback is to re-initialize weights that have begun to contribute to overfitting.

Parameters of the callback are:

* `model` - the model used in training (Required)
* `minweight` - the minimum value of the random weights to be generated. (default value = -.05)
* `maxweight` - the maximum value of the random weights to be generated. (default value = .05)
* `volatility_ratio` - the percentage of weights you would like to re-initialize. (default value = .1)
* `index` - the index of a layer within the model that you'd like to randomize the weights of. This will prevent randomization of all other layers. (default value = None)
* `verbose` - defaults to False. If set to True, will print the model/layer name and the percentage of weights that were randomized.

An implementation of the Stroke callback on an MNIST classification model can be seen below:

```python
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPool2D, Flatten
from kerastroke import Stroke

model = Sequential()

model.add(Conv2D(32, 3, 3, input_shape = (28,28, 1), activation = 'relu'))
model.add(MaxPool2D(pool_size = (2,2)))

model.add(Conv2D(32,3,3, activation = 'relu'))
model.add(MaxPool2D(pool_size = (2,2)))

model.add(Flatten())

model.add(Dense(output_dim = 128, init = 'uniform', activation = 'relu'))

model.add(Dense(10, init = 'uniform', activation = 'sigmoid'))

model.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = ['accuracy'])

_ = model.fit(x_train, y_train,
          batch_size=64,
          epochs=1,
          steps_per_epoch=5,
          verbose=0,
          callbacks=[Stroke(model)])
