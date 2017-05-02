
# coding: utf-8

# ### Preprocessing data

# In[1]:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("all_data.csv", index_col = 0)


# In[2]:

# Look at the data
data.head()


# In[3]:

# test for NAN
print pd.isnull(data).any()
# fill NAN with 0 in "fraud" column
data = data.fillna(0)
data.head()


# In[4]:

# only keep the data after 28 days
df = data[data["date"]>"2010-01-28"]
# only extract the label and features columns
df = df.iloc[:,9:]
print df.shape
df.head()


# In[5]:

# split lables and features
labels = df["fraud"]
features = df.iloc[:,1:]

print sum(labels)
print len(labels)
print sum(labels)/len(labels)


# In[6]:

# import neccessary sklearn packages
from sklearn.preprocessing import scale
from sklearn.linear_model import LogisticRegression
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.base import clone


# In[7]:

# pre-process dataset with z-scaling
df[df.columns[1:]] = scale(df[df.columns[1:]])
features = scale(features)


# In[8]:

df


# In[9]:

features


# In[16]:

# train-testing split with 2 to 1 proportion
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.33333, random_state=10)
print "Training set:"
print "Number of Frauds: ",
print sum(y_train)
print "Total number of records: ",
print len(y_train)
print "Fraud rate: ",
print sum(y_train) / len(y_train)
print "\nTesting set:"
print "Number of Frauds: ",
print sum(y_test)
print "Total number of records: ",
print len(y_test)
print "Fraud rate: ",
print sum(y_test) / len(y_test)


# ### Feature Selction Based on Mutual Information

# In[10]:

# MI feature selection
MI = mutual_info_classif(features,labels)
print MI

get_ipython().magic(u'matplotlib inline')
plt.bar(range(1,len(MI)+1), MI)
plt.title("Mutual Information Plot")
plt.xlabel("Variable Index")
plt.ylabel("Mutual Information")


# In[11]:

# select only variables with MI larger than 0.003
selected = np.array(range(len(MI)))[MI > 0.003]
features_sub = features[:,selected]
clf = LogisticRegression()
clf.fit(features_sub, labels)
score = clf.score(features_sub, labels)
print "Accuracy score is", score

predictions = clf.predict(features_sub)
print "AUC score is", roc_auc_score(labels, predictions)

matrix = confusion_matrix(labels, predictions)
print "FDR is", matrix[1,1]/sum(labels)


# In[23]:

def mi_selection(threshold):
    '''
    threshold: threshold on the MI to select features
    output: AUC score
    '''
    selected = np.array(range(len(MI)))[MI > threshold]
    features_sub = X_train[:,selected]
    clf = LogisticRegression()
    clf.fit(features_sub, y_train)
    predictions_train = clf.predict(features_sub)
    predictions_test = clf.predict(X_test[:,selected])
    return (roc_auc_score(y_train, predictions_train), roc_auc_score(y_test, predictions_test))


# In[29]:

threshold_lst = np.arange(0.0025, 0.0035, 0.0002)
auc_list_train = []
auc_list_test = []
for threshold in threshold_lst:
    auc_list_train.append(mi_selection(threshold)[0])
    auc_list_test.append(mi_selection(threshold)[1])
    
plt.plot(threshold_lst, auc_list_train, label="training set")
plt.plot(threshold_lst, auc_list_test, label="test set")
plt.title("AUC score with different MI thresholds")
plt.xlabel("Threshold")
plt.ylabel("AUC score")
plt.legend(loc="center left")
plt.show()


# In[37]:

def mi_selection(threshold, clf):
    '''
    threshold: threshold on the MI to select features
    clf: classifier used
    output: AUC score
    '''
    clf_clone = clone(clf)
    selected = np.array(range(len(MI)))[MI > threshold]
    features_sub = X_train[:,selected]
    clf_clone.fit(features_sub, y_train)
    predictions_train = clf_clone.predict(features_sub)
    predictions_test = clf_clone.predict(X_test[:,selected])
    return (roc_auc_score(y_train, predictions_train), roc_auc_score(y_test, predictions_test))

def mi_plot(threshold_lst, clf, plot_title, location):
    auc_list_train = []
    auc_list_test = []
    for threshold in threshold_lst:
        auc_list_train.append(mi_selection(threshold, clf)[0])
        auc_list_test.append(mi_selection(threshold, clf)[1])
    
    plt.plot(threshold_lst, auc_list_train, label="training set")
    plt.plot(threshold_lst, auc_list_test, label="test set")
    plt.title(plot_title)
    plt.xlabel("Threshold")
    plt.ylabel("AUC score")
    plt.legend(loc=location)
    plt.show()


# In[45]:

clf = LogisticRegression()
threshold_lst = np.arange(0, 0.006, 0.0005)
mi_plot(threshold_lst, clf, "AUC score with different MI thresholds (Logistic Regression)", "upper right")


# In[39]:

clf = GaussianNB()
threshold_lst = np.arange(0, 0.006, 0.0005)
mi_plot(threshold_lst, clf, "AUC score with different MI thresholds (Gaussian Naive Bayes)", "lower left")


# In[41]:

clf = RandomForestClassifier(n_estimators = 25, max_depth = 20, min_samples_split = 5, random_state = 42, n_jobs = 3)
threshold_lst = np.arange(0, 0.006, 0.0005)
mi_plot(threshold_lst, clf, "AUC score with different MI thresholds (Random Forest)", "center left")


# In[42]:

clf = SVC()
threshold_lst = np.arange(0, 0.006, 0.0005)
mi_plot(threshold_lst, clf, "AUC score with different MI thresholds (SVM)", "lower left")


# In[43]:

clf = MLPClassifier()
threshold_lst = np.arange(0, 0.006, 0.0005)
mi_plot(threshold_lst, clf, "AUC score with different MI thresholds (Neural Network)", "lower left")


# In[48]:

print len(np.array(range(len(MI)))[MI > 0.003])
print len(np.array(range(len(MI)))[MI > 0.004])
print len(np.array(range(len(MI)))[MI > 0.005])


# In[51]:

df.columns.values[[i+1 for i in np.array(range(len(MI)))[MI > 0.005]]]


# In[52]:

MI[np.array(range(len(MI)))[MI > 0.005]]


# In[49]:

# select only variables with MI larger than 0.005
selected = np.array(range(len(MI)))[MI > 0.005]
features_sub = features[:,selected]

clf = GaussianNB()
clf.fit(features_sub, labels)
score = clf.score(features_sub, labels)
print "_________NB________"
print "Accuracy score is", score
predictions = clf.predict(features_sub)
print "AUC score is", roc_auc_score(labels, predictions)
matrix = confusion_matrix(labels, predictions)
print "FDR is", matrix[1,1]/sum(labels)

clf = LogisticRegression()
clf.fit(features_sub, labels)
score = clf.score(features_sub, labels)
print "_________LR________"
print "Accuracy score is", score
predictions = clf.predict(features_sub)
print "AUC score is", roc_auc_score(labels, predictions)
matrix = confusion_matrix(labels, predictions)
print "FDR is", matrix[1,1]/sum(labels)

clf = RandomForestClassifier(n_estimators = 25, max_depth = 20, min_samples_split = 5, random_state = 42, n_jobs = 3)
clf.fit(features_sub, labels)
score = clf.score(features_sub, labels)
print "_________RF________"
print "Accuracy score is", score
predictions = clf.predict(features_sub)
print "AUC score is", roc_auc_score(labels, predictions)
matrix = confusion_matrix(labels, predictions)
print "FDR is", matrix[1,1]/sum(labels)

clf = SVC()
clf.fit(features_sub, labels)
score = clf.score(features_sub, labels)
print "_________SVM________"
print "Accuracy score is", score
predictions = clf.predict(features_sub)
print "AUC score is", roc_auc_score(labels, predictions)
matrix = confusion_matrix(labels, predictions)
print "FDR is", matrix[1,1]/sum(labels)

clf = MLPClassifier()
clf.fit(features_sub, labels)
score = clf.score(features_sub, labels)
print "_________NN________"
print "Accuracy score is", score
predictions = clf.predict(features_sub)
print "AUC score is", roc_auc_score(labels, predictions)
matrix = confusion_matrix(labels, predictions)
print "FDR is", matrix[1,1]/sum(labels)


# ### Forward Feature Selection

# In[11]:

# forward selection algorithm
def forward_selection(feature, label, clf, criteria):
    '''
    feature: ndarray of all the feature
    label: series of fraud label
    clf: classifier
    criteria: "accuracy", "AUC" or "FDR"
    
    print the whole feature selection process and feature selected in the end
    
    return the index list of features selected
    '''
    
    # initialize counter and comparison flag
    max_accuracy = 0
    added_features = []
    count = 0
    print "Starting........ Selection criteria is {crit}, baseline score is {baseline}".format(
        crit = criteria,
        baseline = max_accuracy)
    # loop until all the new models give a worse result
    while True:
        count += 1
        accuracy = {}
        # feature_lst is the list for all the feature indice except those features have been selected in previous round
        feature_lst = [i for i in range(feature.shape[1]) if i not in added_features]
        # add one feature in feature_list each time
        for i in feature_lst:
            feature_sub = feature[:,added_features+[i]]
            if count == 1:
                # change the shape of ndarray to make it acceptable for sklearn
                feature_sub = feature_sub.reshape(feature_sub.shape[0],1)
            # loop over to create a dict accuracy with feature index as key, and correponding accuracy as value
            clf_clone = clone(clf)
            clf_clone.fit(feature_sub, label)
            if criteria == "accuracy":
                accuracy[i] = clf_clone.score(feature_sub, label)
            elif criteria == "AUC":
                prediction = clf_clone.predict(feature_sub)
                accuracy[i] = roc_auc_score(label, prediction)
            elif criteria == "FDR":
                prediction = clf_clone.predict(feature_sub)
                matrix = confusion_matrix(label, prediction)
                accuracy[i] = matrix[1,1]/sum(label)
        # when the accuracy dict is empty, indicating it's the last round with no left features, end the loop
        if accuracy == {}:
            print "Forward selection ended."
            print "Selected features are ",
            print final_feature_lst
            return feature_index
            break
        # if it's not the last round, calculate the best result in current round
        current_max = max(accuracy.values())
        # if a not worse best result is generated, update added_features list
        if current_max >= max_accuracy:
            max_index = accuracy.keys()[accuracy.values().index(current_max)]
            added_features.append(max_index)
            feature_name = df.columns.values[max_index+1]
            # do not updated the final_feature_list until a better result is generated (always make sure fewer features)
            if current_max > max_accuracy:
                final_feature_lst = list(df.columns.values[[i+1 for i in added_features]])
                feature_index = list(added_features)
            # update maximum record
            max_accuracy = current_max
            print "Round number: {count_num}, the added feature is: {feature_selected}, maximum score is: {max_acc}\n".format(
            count_num = count,
            feature_selected = feature_name,
            max_acc = max_accuracy)
        # otherwise, all the results are worse, end the loop
        else:
            print "Forward selection ended."
            print "Selected features are ",
            print final_feature_lst
            return feature_index
            break


# In[50]:

def test_comparison(feature_selected, clf):
    X_train_sub = X_train[:,feature_selected]
    clf.fit(X_train_sub, y_train)
    prediction_train = clf.predict(X_train_sub)
    matrix = confusion_matrix(y_train, prediction_train)
    train_acc = clf.score(X_train_sub, y_train)
    train_auc = roc_auc_score(y_train, prediction_train)
    train_fdr = matrix[1,1]/sum(y_train)
    
    X_test_sub = X_test[:,feature_selected]
    prediction_test = clf.predict(X_test_sub)
    matrix = confusion_matrix(y_test, prediction_test)
    test_acc = clf.score(X_test_sub, y_test)
    test_auc = roc_auc_score(y_test, prediction_test)
    test_fdr = matrix[1,1]/sum(y_test)
    
    comparison_df = pd.DataFrame({ "Accuracy": [train_acc, test_acc],
                                  "AUC score": [train_auc, test_auc],
                                  "FDR": [train_fdr, test_fdr]},
                                 index = ["Training", "Testing"])
    return comparison_df


# ### Gaussian Naive Bayes

# In[13]:

clf = GaussianNB()
criteria = "AUC"
NB_features = forward_selection(X_train, y_train, clf, criteria)


# In[51]:

clf = GaussianNB()
test_comparison(NB_features, clf)


# **Gaussian Naive Bayes** Classifer does moderately well, and does not seem to suffer a lot from overfitting.

# In[108]:

features_sub = df[['zip_with_merchnum_7', 'card_amount_to_median_28', 'merchant_amount_to_median_28', 'state_with_merchnum_3', 'merchLag3Cum', 'cardLag7Cum']]
clf = GaussianNB()
clf.fit(features_sub, labels)
print "accuracy is", clf.score(features_sub, labels)
prediction = clf.predict(features_sub)
matrix = confusion_matrix(labels, prediction)
print "\n"
print matrix
print "\n"
print  "FDR is", matrix[1,1]/sum(labels)


# ### Logistic Regression

# In[16]:

clf = LogisticRegression()
criteria = "AUC"
LR_features = forward_selection(X_train, y_train, clf, criteria)


# In[123]:

clf = LogisticRegression()
test_comparison(LR_features, clf)


# **Logistic Regression Model** performs poor. Althrough it's accuracy is not very low, it missed many frauds.

# In[124]:

features_sub = df[['zip_with_merchnum_14', 'card_amount_to_median_7', 'card_amount_to_max_3', 'card_amount_to_avg_28', 'state_with_merchnum_7', 'cardDaily', 'merchant_amount_to_median_3', 'merchant_amount_to_max_7', 'cardLag7Cum', 'card_amount_to_total_3', 'card_amount_to_max_14', 'merchant_amount_to_avg_14', 'merchant_amount_to_max_28', 'merchant_amount_to_avg_28', 'merchant_amount_to_median_28', 'merchLag7Cum', 'merchnum_per_card_28', 'merchLag14Cum', 'state_with_merchnum_28', 'merchant_amount_to_median_7', 'card_amount_to_max_28', 'merchant_amount_to_total_7', 'merchant_amount_to_avg_3', 'card_amount_to_avg_3', 'card_amount_to_median_3', 'card_amount_to_max_7', 'card_amount_to_median_14', 'card_amount_to_total_7', 'merchant_amount_to_max_14', 'merchant_amount_to_total_3', 'card_amount_to_median_28', 'card_amount_to_total_28', 'merchDaily', 'merchLag28Cum', 'cardLag14Cum', 'zip_with_merchnum_3', 'state_with_merchnum_3', 'merchnum_per_card_3', 'zip_with_merchnum_28', 'merchnum_per_card_14', 'merchLag3Cum', 'card_amount_to_avg_7']]
clf = LogisticRegression()
clf.fit(features_sub, labels)
print "accuracy is", clf.score(features_sub, labels)
prediction = clf.predict(features_sub)
matrix = confusion_matrix(labels, prediction)
print "\n"
print matrix
print "\n"
print  "FDR is", matrix[1,1]/sum(labels)


# In[36]:

# poor FDR, what if we set FDR as forward selection criteria
clf = LogisticRegression()
criteria = "FDR"
LR_features_fdr = forward_selection(X_train, y_train, clf, criteria)


# In[110]:

clf = LogisticRegression()
test_comparison(LR_features_fdr, clf)


# When you set FDR as the criteria, performance does not improve much, so just stick to AUC criteria.

# In[111]:

features_sub = df[['zip_with_merchnum_14', 'card_amount_to_median_7', 'card_amount_to_avg_3', 'card_amount_to_avg_28', 'state_with_merchnum_7', 'card_amount_to_max_3', 'card_amount_to_avg_7', 'card_amount_to_median_28', 'card_amount_to_total_14', 'card_amount_to_total_3', 'merchant_amount_to_avg_3', 'merchant_amount_to_max_3', 'merchant_amount_to_median_3', 'merchant_amount_to_total_3', 'merchant_amount_to_avg_7', 'merchant_amount_to_max_7', 'merchant_amount_to_median_7', 'merchant_amount_to_total_7', 'merchant_amount_to_median_28', 'merchant_amount_to_avg_28', 'merchant_amount_to_max_28', 'zip_with_merchnum_3', 'card_amount_to_total_7', 'cardLag7Cum', 'card_amount_to_max_7', 'card_amount_to_avg_14', 'card_amount_to_median_14', 'card_amount_to_max_28', 'merchant_amount_to_total_28', 'merchLag3Cum', 'merchLag7Cum', 'merchnum_per_card_7', 'card_amount_to_median_3', 'card_amount_to_max_14', 'merchant_amount_to_avg_14', 'merchant_amount_to_max_14', 'merchant_amount_to_median_14', 'merchDaily', 'merchLag14Cum', 'merchnum_per_card_28', 'cardnum_per_merch_7', 'state_with_merchnum_14']]
clf = LogisticRegression()
clf.fit(features_sub, labels)
print "accuracy is", clf.score(features_sub, labels)
prediction = clf.predict(features_sub)
matrix = confusion_matrix(labels, prediction)
print "\n"
print matrix
print "\n"
print  "FDR is", matrix[1,1]/sum(labels)


# ### Decision Tree

# In[20]:

clf = DecisionTreeClassifier()
criteria = "AUC"
DT_features = forward_selection(X_train, y_train, clf, criteria)


# In[112]:

clf = DecisionTreeClassifier()
test_comparison(DT_features, clf)


# **Single Decision Tree Classsifier** gives extremely overfitted output...

# ### Random Forest

# In[31]:

clf = RandomForestClassifier(n_jobs = 3)
criteria = "AUC"
RF_features = forward_selection(X_train, y_train, clf, criteria)


# In[114]:

clf = RandomForestClassifier(n_jobs = 3)
test_comparison(RF_features, clf)


# **Random Forest** with default setting overally performs well, althrough still suffers from overfitting to some extent.

# In[115]:

features_sub = df[['card_amount_to_avg_14', 'merchant_amount_to_max_28', 'cardLag3Cum', 'merchDaily', 'cardnum_per_merch_28', 'merchLag28Cum', 'cardnum_per_merch_7', 'merchnum_per_card_28', 'merchant_amount_to_median_14']]
clf = RandomForestClassifier(n_jobs = 3)
clf.fit(features_sub, labels)
print "accuracy is", clf.score(features_sub, labels)
prediction = clf.predict(features_sub)
matrix = confusion_matrix(labels, prediction)
print "\n"
print matrix
print "\n"
print  "FDR is", matrix[1,1]/sum(labels)


# In[161]:

clf = RandomForestClassifier(n_estimators = 25, max_depth = 20, min_samples_split = 5, random_state = 42, n_jobs = 3)
criteria = "AUC"
RF_features = forward_selection(X_train, y_train, clf, criteria)


# In[162]:

clf = RandomForestClassifier(n_estimators = 25, max_depth = 20, min_samples_split = 5, random_state = 42, n_jobs = 3)
test_comparison(RF_features, clf)


# Tunned a little bit, and FDR on testing data improved.

# In[163]:

features_sub = df[['merchant_amount_to_median_28', 'cardLag7Cum', 'zip_with_merchnum_28', 'merchLag28Cum', 'cardDaily', 'merchant_amount_to_max_14', 'cardnum_per_merch_14']]
clf = RandomForestClassifier(n_estimators = 25, max_depth = 20, min_samples_split = 5, random_state = 42, n_jobs = 3)
clf.fit(features_sub, labels)
print "accuracy is", clf.score(features_sub, labels)
prediction = clf.predict(features_sub)
matrix = confusion_matrix(labels, prediction)
print "\n"
print matrix
print "\n"
print  "FDR is", matrix[1,1]/sum(labels)


# ### Support Vector Machine

# In[38]:

clf = SVC()
criteria = "AUC"
SVM_features = forward_selection(X_train, y_train, clf, criteria)


# In[116]:

clf = SVC()
test_comparison(SVM_features, clf)


# **SVM** performs moderatelly well. Not much overfitting seen.

# In[117]:

features_sub = df[['zip_with_merchnum_14', 'card_amount_to_median_7', 'cardLag7Cum', 'merchant_amount_to_median_14', 'merchant_amount_to_avg_14', 'merchant_amount_to_median_28', 'merchnum_per_card_28', 'cardLag3Cum', 'merchant_amount_to_median_7', 'merchLag14Cum', 'cardnum_per_merch_28', 'cardDaily', 'cardnum_per_merch_3', 'cardLag28Cum', 'card_amount_to_median_14', 'merchant_amount_to_max_28', 'merchnum_per_card_3', 'cardnum_per_merch_7', 'merchant_amount_to_max_3']]
clf = SVC()
clf.fit(features_sub, labels)
print "accuracy is", clf.score(features_sub, labels)
prediction = clf.predict(features_sub)
matrix = confusion_matrix(labels, prediction)
print "\n"
print matrix
print "\n"
print  "FDR is", matrix[1,1]/sum(labels)


# ### Neural Network (Multi-Layer Perceptron Classifier)

# In[45]:

clf = MLPClassifier(activation = "logistic")
criteria = "AUC"
NN_features = forward_selection(X_train, y_train, clf, criteria)


# In[49]:

clf = MLPClassifier()
criteria = "AUC"
NN_features = forward_selection(X_train, y_train, clf, criteria)


# In[120]:

clf = MLPClassifier()
test_comparison(NN_features, clf)


# **Neural Network** performs quite impressive compared to other models.

# In[30]:

features_sub = df[['zip_with_merchnum_28', 'state_with_merchnum_7', 'card_amount_to_median_3', 'cardLag3Cum', 'card_amount_to_median_28', 'cardnum_per_merch_7', 'merchDaily', 'merchant_amount_to_median_28', 'merchnum_per_card_28', 'merchant_amount_to_median_7', 'card_amount_to_max_3']]
clf = MLPClassifier()
clf.fit(features_sub, labels)
print "accuracy is", clf.score(features_sub, labels)
prediction = clf.predict(features_sub)
matrix = confusion_matrix(labels, prediction)
print "\n"
print matrix
print "\n"
print  "FDR is", matrix[1,1]/sum(labels)
print "Number of Layers is", clf.n_layers_


# ### Save scores

# In[141]:

# NB
features_sub = df[['zip_with_merchnum_7', 'card_amount_to_median_28', 'merchant_amount_to_median_28', 'state_with_merchnum_3', 'merchLag3Cum', 'cardLag7Cum']]
clf = GaussianNB()
clf.fit(features_sub, labels)
NB_scores = clf.predict_proba(features_sub)[:,1]
NB_scores_df = pd.DataFrame({"NB": NB_scores})

# LR
features_sub = df[['zip_with_merchnum_14', 'card_amount_to_median_7', 'card_amount_to_max_3', 'card_amount_to_avg_28', 'state_with_merchnum_7', 'cardDaily', 'merchant_amount_to_median_3', 'merchant_amount_to_max_7', 'cardLag7Cum', 'card_amount_to_total_3', 'card_amount_to_max_14', 'merchant_amount_to_avg_14', 'merchant_amount_to_max_28', 'merchant_amount_to_avg_28', 'merchant_amount_to_median_28', 'merchLag7Cum', 'merchnum_per_card_28', 'merchLag14Cum', 'state_with_merchnum_28', 'merchant_amount_to_median_7', 'card_amount_to_max_28', 'merchant_amount_to_total_7', 'merchant_amount_to_avg_3', 'card_amount_to_avg_3', 'card_amount_to_median_3', 'card_amount_to_max_7', 'card_amount_to_median_14', 'card_amount_to_total_7', 'merchant_amount_to_max_14', 'merchant_amount_to_total_3', 'card_amount_to_median_28', 'card_amount_to_total_28', 'merchDaily', 'merchLag28Cum', 'cardLag14Cum', 'zip_with_merchnum_3', 'state_with_merchnum_3', 'merchnum_per_card_3', 'zip_with_merchnum_28', 'merchnum_per_card_14', 'merchLag3Cum', 'card_amount_to_avg_7']]
clf = LogisticRegression()
clf.fit(features_sub, labels)
LR_scores = clf.predict_proba(features_sub)[:,1]
LR_scores_df = pd.DataFrame({"LR": LR_scores})


# In[172]:

# RF
features_sub = df[['merchant_amount_to_median_28', 'cardLag7Cum', 'zip_with_merchnum_28', 'merchLag28Cum', 'cardDaily', 'merchant_amount_to_max_14', 'cardnum_per_merch_14']]
clf = RandomForestClassifier(n_estimators = 25, max_depth = 20, min_samples_split = 5, random_state = 42, n_jobs = 3)
clf.fit(features_sub, labels)
RF_scores = clf.predict_proba(features_sub)[:,1]
RF_scores_df = pd.DataFrame({"RF": RF_scores})


# In[153]:

# SVM
features_sub = df[['zip_with_merchnum_14', 'card_amount_to_median_7', 'cardLag7Cum', 'merchant_amount_to_median_14', 'merchant_amount_to_avg_14', 'merchant_amount_to_median_28', 'merchnum_per_card_28', 'cardLag3Cum', 'merchant_amount_to_median_7', 'merchLag14Cum', 'cardnum_per_merch_28', 'cardDaily', 'cardnum_per_merch_3', 'cardLag28Cum', 'card_amount_to_median_14', 'merchant_amount_to_max_28', 'merchnum_per_card_3', 'cardnum_per_merch_7', 'merchant_amount_to_max_3']]
clf = SVC()
clf.fit(features_sub, labels)
SVM_scores = clf.predict(features_sub)
SVM_scores_df = pd.DataFrame({"SVM": SVM_scores})


# In[169]:

# NN
features_sub = df[['zip_with_merchnum_28', 'state_with_merchnum_7', 'card_amount_to_median_3', 'cardLag3Cum', 'card_amount_to_median_28', 'cardnum_per_merch_7', 'merchDaily', 'merchant_amount_to_median_28', 'merchnum_per_card_28', 'merchant_amount_to_median_7', 'card_amount_to_max_3']]
clf = MLPClassifier()
clf.fit(features_sub, labels)
NN_scores = clf.predict_proba(features_sub)[:,1]
NN_scores_df = pd.DataFrame({"NN": NN_scores})


# In[175]:

score_df = pd.concat([NB_scores_df, LR_scores_df, RF_scores_df, SVM_scores_df, NN_scores_df], axis=1)


# In[180]:

score_df.index = df.index


# In[181]:

score_df


# In[182]:

score_df.to_csv("Fraud Scores.csv")


# In[122]:

# store all the variables for subsequent use
get_ipython().magic(u'store data')
get_ipython().magic(u'store df')
get_ipython().magic(u'store features')
get_ipython().magic(u'store labels')
get_ipython().magic(u'store X_train')
get_ipython().magic(u'store X_test')
get_ipython().magic(u'store y_train')
get_ipython().magic(u'store y_test')
get_ipython().magic(u'store data')
get_ipython().magic(u'store NB_features')
get_ipython().magic(u'store LR_features')
get_ipython().magic(u'store DT_features')
get_ipython().magic(u'store RF_features')
get_ipython().magic(u'store SVM_features')
get_ipython().magic(u'store NN_features')


# In[ ]:



