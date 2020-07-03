from datetime import datetime
import pandas as pd
import numpy as np
import pickle
import sys
from feature_extraction import generate_url_dataset
from sklearn.model_selection import train_test_split





#-------------------------------------------------------------------

dataset=pd.read_csv("F:\python\Phishingweb\dataset.csv")


file_out=open("dataset.pickle","wb")
pickle.dump(dataset, file_out)
file_in= open("dataset.pickle",'rb')
x=pickle.load(file_in)
x.set_index(['index'],inplace=True)


target=x['Result'].values
data=x.iloc[:,:-1].values
data.shape

x_train, x_test, y_train, y_test= train_test_split(data,target)





#------------------------------------------------------------------


from sklearn.tree import DecisionTreeClassifier 
dtree_model = DecisionTreeClassifier(max_depth = 2).fit(x_train, y_train) 
dtree_predictions = dtree_model.predict(x_test) 
dtree_predictions
from sklearn.metrics import accuracy_score
acc=accuracy_score(dtree_predictions,y_test)
print("accurac DTC-> ",acc)





#------------------------------------------------------------------
# training a linear SVM classifier 
from sklearn.svm import SVC 
svm_model_linear = SVC(kernel = 'poly', C = 4).fit(x_train, y_train) 
svm_predictions = svm_model_linear.predict(x_test) 
  
# model accuracy for x_test on SVM classifier   
accuracy = svm_model_linear.score(x_test, y_test) 
print("accuracy SVM-> ",accuracy)



#------------------------------------------------------------------
# training a KNN classifier 
from sklearn.neighbors import KNeighborsClassifier 
from sklearn.metrics import confusion_matrix 
knn = KNeighborsClassifier(n_neighbors = 7).fit(x_train, y_train) 
  
# accuracy on X_test 
accuracy = knn.score(x_test, y_test) 
print("accuracy KNN-> ",accuracy)
  
# creating a confusion matrix 
knn_predictions = knn.predict(x_test)  
cm = confusion_matrix(y_test, knn_predictions) 
cm

#------------------------------------------------------------------
#  training a Naive Bayes classifier 
from sklearn.naive_bayes import GaussianNB 
gnb = GaussianNB().fit(x_train, y_train) 
gnb_predictions = gnb.predict(x_test) 
  
# accuracy on X_test 
accuracy = gnb.score(x_test, y_test) 
  
# creating a confusion matrix 
cm = confusion_matrix(y_test, gnb_predictions) 
cm

#------------------------------------------------------------------


from sklearn.ensemble  import RandomForestClassifier
randomForest=RandomForestClassifier(n_estimators=16, )
randomForest.fit(x_train,y_train)
predictions=randomForest.predict(x_test)

# accuracy on X_test 
accuracy = randomForest.score(x_test, y_test) 
accuracy  
cm = confusion_matrix(y_test,predictions ) 
cm
from sklearn.metrics import f1_score
f1_score=f1_score(y_test,predictions)
f1_score



file_out= open('R-F-model.pkl',"wb")
pickle.dump(randomForest,file_out)
file_out.close

file_in=open("R-F-model.pkl",'rb')
model=pickle.load(file_in)

'''from sklearn.metrics import  roc_curve
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
roc_acc=roc_auc_score(y_test,predictions)
fpr,tpr,threshold = roc_curve(y_test,randomForest.predict_proba(x_test)[:,1])


plt.figure()
plt.plot(fpr,tpr,label="random forest (area= .2f)"% roc_acc)
plt.xlabel("Fale positive rate")
plt.ylabel("True positive rate")
plt.plot([0,1],[0,1],'r--')
plt.show()

from sklearn.metrics import classification_report
print(classification_report(y_test,predictions))
