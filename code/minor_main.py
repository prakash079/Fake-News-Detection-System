# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 22:47:36 2019

@author: dell
"""
# Include Libraries

import pandas as pd
from sklearn.model_selection import train_test_split
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from matplotlib import pyplot as plt
from sklearn.linear_model import PassiveAggressiveClassifier
#from sklearn.feature_extraction.text import HashingVectorizer
import itertools
import numpy as np

# Importing dataset using pandas dataframe

df = pd.read_csv("fake_or_real_news.csv")

# Print first lines of `df` 
df.head()

# Set index 
df = df.set_index("Unnamed: 0")

# Print first lines of `df` 
df.head()

#set up training and test datasets

y = df.label   # Separate the labels
df.drop("label", axis=1) 

# Make training and test sets 
X_train, X_test, y_train, y_test = train_test_split(df['text'], y, test_size=0.33, random_state=53)

# Building the Count and Tfidf Vectors

count_vectorizer = CountVectorizer(stop_words='english') # Initialize the `count_vectorizer` 

count_train = count_vectorizer.fit_transform(X_train)  # Fit and transform the training data 

count_test = count_vectorizer.transform(X_test)  # Transform the test set 

tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7) # Initialize the `tfidf_vectorizer` 
                                                                     # This removes words which appear in more than 70% of the articles

# Fit and transform the training data 
tfidf_train = tfidf_vectorizer.fit_transform(X_train) 

# Transform the test set 
tfidf_test = tfidf_vectorizer.transform(X_test)

"""# Get the feature names of `tfidf_vectorizer` 
#print(tfidf_vectorizer.get_feature_names()[-10:]) 
                                                    #we dont have to print this is just for testing pupose
# Get the feature names of `count_vectorizer` 
#print(count_vectorizer.get_feature_names()[:10])"""
                                                    
count_df = pd.DataFrame(count_train.A, columns=count_vectorizer.get_feature_names())

tfidf_df = pd.DataFrame(tfidf_train.A, columns=tfidf_vectorizer.get_feature_names())

difference = set(count_df.columns) - set(tfidf_df.columns)

print(difference)


# Check whether the DataFrames are equal
print(count_df.equals(tfidf_df))

print(count_df.head())

print(tfidf_df.head())

#--------------------------------------------------------------
# Function to plot the confusion matrix 


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


#--------------------------------------------------------------
# Naive Bayes classifier for Multinomial model 

#on tf-idf vectorizer
    
clf = MultinomialNB() 

clf.fit(tfidf_train, y_train)                       # Fit Naive Bayes classifier according to X, y

pred = clf.predict(tfidf_test)                     # Perform classification on an array of test vectors X.
score = metrics.accuracy_score(y_test, pred)
print("accuracy:   %0.3f" % score)
cm = metrics.confusion_matrix(y_test, pred, labels=['FAKE', 'REAL'])
plot_confusion_matrix(cm, classes=['FAKE', 'REAL'])
print(cm)

# on count vectorizer
clf = MultinomialNB()

clf.fit(count_train, y_train)

pred = clf.predict(count_test)
score = metrics.accuracy_score(y_test, pred)
print("accuracy:   %0.3f" % score)
cm = metrics.confusion_matrix(y_test, pred, labels=['FAKE', 'REAL'])
plot_confusion_matrix(cm, classes=['FAKE', 'REAL'])
print(cm)


#--------------------------------------------------------------
# Applying Passive Aggressive Classifier


#on tf-idf vectorizer

linear_clf = PassiveAggressiveClassifier()

linear_clf.fit(tfidf_train, y_train)
pred = linear_clf.predict(tfidf_test)
score = metrics.accuracy_score(y_test, pred)
print("accuracy:   %0.3f" % score)
cm = metrics.confusion_matrix(y_test, pred, labels=['FAKE', 'REAL'])
plot_confusion_matrix(cm, classes=['FAKE', 'REAL'])
print(cm)


clf = MultinomialNB(alpha=0.1)               # Additive (Laplace/Lidstone) smoothing parameter

last_score = 0
for alpha in np.arange(0,1,.1):
    nb_classifier = MultinomialNB(alpha=alpha)
    nb_classifier.fit(tfidf_train, y_train)
    pred = nb_classifier.predict(tfidf_test)
    score = metrics.accuracy_score(y_test, pred)
    if score > last_score:
        clf = nb_classifier
    print("Alpha: {:.2f} Score: {:.5f}".format(alpha, score))

def most_informative_feature_for_binary_classification(vectorizer, classifier, n=100):      # inspect the top 30 vectors for fake and real news
    """
    
    Identify most important features if given a vectorizer and binary classifier. Set n to the number
    of weighted features you would like to show. 
    """

    class_labels = classifier.classes_
    feature_names = vectorizer.get_feature_names()                                     # Array mapping from feature integer indices to feature name
    topn_class1 = sorted(zip(classifier.coef_[0], feature_names))[:n]
    topn_class2 = sorted(zip(classifier.coef_[0], feature_names))[-n:]

    for coef, feat in topn_class1:
        print(class_labels[0], coef, feat)

    print()

    for coef, feat in reversed(topn_class2):
        print(class_labels[1], coef, feat)

most_informative_feature_for_binary_classification(tfidf_vectorizer, linear_clf, n=30)
feature_names = tfidf_vectorizer.get_feature_names()

### Most real
sorted(zip(clf.coef_[0], feature_names), reverse=True)[:20]

### Most fake
sorted(zip(clf.coef_[0], feature_names))[:20]                               # clearly there are certain
                                                                             #words which might show political intent and source in the top fake features .

tokens_with_weights = sorted(list(zip(feature_names, clf.coef_[0])))



#--------------------------------------------------------------
# HashingVectorizer : require less memory and are faster 
#(because they are sparse and use hashes rather than tokens)


"""hash_vectorizer = HashingVectorizer(stop_words='english')
hash_train = hash_vectorizer.fit_transform(X_train)
hash_test = hash_vectorizer.transform(X_test)

#--------------------------------------------------------------
# Naive Bayes classifier for Multinomial model 

clf = MultinomialNB(alpha=.01)

clf.fit(hash_train, y_train)
pred = clf.predict(hash_test)
score = metrics.accuracy_score(y_test, pred)
print("accuracy:   %0.3f" % score)
cm = metrics.confusion_matrix(y_test, pred, labels=['FAKE', 'REAL'])
plot_confusion_matrix(cm, classes=['FAKE', 'REAL'])
print(cm)


#--------------------------------------------------------------
# Applying Passive Aggressive Classifier

clf = PassiveAggressiveClassifier()    

clf.fit(hash_train, y_train)
pred = clf.predict(hash_test)
score = metrics.accuracy_score(y_test, pred)
print("accuracy:   %0.3f" % score)
cm = metrics.confusion_matrix(y_test, pred, labels=['FAKE', 'REAL'])
plot_confusion_matrix(cm, classes=['FAKE', 'REAL'])
print(cm)"""




