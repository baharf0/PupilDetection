!pip install wget
import wget
import cv2
import glob
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tensorflow import keras
from keras import layers
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.callbacks import ModelCheckpoint
from google.colab.patches import cv2_imshow
from sklearn.model_selection import train_test_split

wget.download('https://www.bioid.com/uploads/BioID-FaceDatabase-V1.2.zip')
!unzip '/content/BioID-FaceDatabase-V1.2.zip' -d '/content/dataset'

path="/content/dataset/*"

x_total = []
for x_img in sorted(glob.glob(path+".pgm")):
  x_image = cv2.imread(x_img)
  x_total.append(x_image)
x_total = np.array(x_total)

y_total = pd.DataFrame()
for y_img in sorted(glob.glob(path+".eye")):
  y_image = pd.read_csv(y_img, sep='\t')
  y_total = y_total.append(y_image)

print(x_total[0].shape)
print(y_total.head(5))
cv2_imshow(x_total[3])

x_train, x_test, y_train, y_test = train_test_split(x_total, y_total,
                                                    train_size=0.7,
                                                    test_size=0.3,
                                                    random_state=122)

baseModel = ResNet50(weights='imagenet', include_top = False,
                      input_shape = (286, 384, 3)) 

headModel = keras.layers.GlobalAveragePooling2D()(baseModel.output)
headModel = layers.Flatten()(headModel)

output = keras.layers.Dense(4, activation='linear')(headModel)

model = keras.models.Model(inputs=baseModel.input, outputs=output)

model.compile(loss='mean_squared_error',
                        optimizer='adam', metrics=['accuracy'])

model.summary()

checkpoint = keras.callbacks.ModelCheckpoint("best.h5",
                                             monitor='val_loss', mode='min', 
                                             save_best_only=True)

model.fit(x_train,y_train, epochs=10, batch_size=16, validation_split=0.1,
          callbacks=[checkpoint])

model.evaluate(x_test,y_test)
model.save('model.h5')

output = pd.DataFrame()
print(x_total[50].shape)
output = model.predict(x_total[50])
x1 = output.iloc[0][2]
x2 = output.iloc[0][0]
y1 = output.iloc[0][3]
y2 = output.iloc[0][1]

print(x1)
print(x2)
print(y1)
print(y2)

pic = cv2.line(x_test[150], (x1,y1), (x2,y2),(0,255,255))
cv2_imshow(pic)

p1=y_total.iloc[30][0]
p2=y_total.iloc[30][1]
p3=y_total.iloc[30][2]
p4=y_total.iloc[30][3]

pupil = cv2.line(x_total[29], (p3,p4),(p1,p2), color=(0, 255, 0))

cv2_imshow(pupil)
