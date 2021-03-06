#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
# This file is part of Kuaa.
#
# Kuaa is a framework for the automation of machine learning experiments.
#
# It provides a workflow-based standardized environment for easy evaluation of
# feature descriptors, normalization techniques, classifiers and fusion
# approaches.
#
# Techniques of each kind can be easily plugged into the framework as they can
# be implemented as plugins, with standardized inputs and outputs.
# The framework also provides a recommendation module in order to help
# inexperienced researchers in choosing adequate or alternative techniques for
# experiments.
#
# Copyright (C) 2016 under the GNU General Public License Version 3.
#
# This framework was developed during the research collaboration of Institute
# of Computing (University of Campinas, Brazil) and Samsung Eletrônica da
# Amazônia Ltda. entitled "Pattern recognition and classification by feature
# engineering, *-fusion, open-set recognition, and meta-recognition", which was
# sponsored by Samsung.
#
# This framework is provided "as is" without any guarantees or warranty. The
# authors make no warranties, express of implied, that they are free of error,
# or they will meet your requirements for any particular application.
#
# The framework was developed to be used for educational and research purposes.
# It is expressly prohibited to use for any commercial purposes.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

#Python imports
import os
import sys
import numpy
from sklearn import preprocessing
from sklearn.externals import joblib
from subprocess import call

#Framework Imports
dirname = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(dirname)
SVM_path = os.path.join(dirname, 'SVM')
sys.path.append(SVM_path)
call(["./prepareLibSVM.sh", "clean"], cwd="{0}".format(SVM_path))
call(["./prepareLibSVM.sh"], cwd="{0}".format(SVM_path))
call(["./prepareLib1VS.sh", "clean"], cwd="{0}".format(SVM_path))
call(["./prepareLib1VS.sh"], cwd="{0}".format(SVM_path))
import Classifier
import SVM
import svmutil

#CONSTANTS
POS_CLASSES = 0
POS_FV = 1
INDEX_ZERO = 0

def svm_approach(string):
    """
    Function to translate the string of the approach to a string recognized by
    the plugin.
    """
    
    if string == 'One vs All':
        return 'OVA'
    elif string == 'One vs One':
        return 'OVO'
    else:
        return 'OVA'

def classify(images, classes_list, train_set, test_set, pos_fold, descriptor,
        parameters):
    """
    Performs the classification of the test_set according to the train_set.
    
    Implementation of Support Vector Machine classifier using sklearn.
    """
    
    print "Classification: SVMDBC"
    
    #Get parameters
    SVMDBC_approach = svm_approach(parameters['Approach'])
    
    #Paths
    dirname = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    temp_path = os.path.abspath(os.path.join(dirname, "..", "..", "temp"))
    model_path = os.path.join(temp_path, "iteration:" + str(iteration) + \
            "-SVMDBC_" + str(pos_fold) + ".model")
    
    #Preprocess each class to a unique value to the classification
    label_encoder = preprocessing.LabelEncoder()
    label_encoder.fit(classes_list)
    
    #SVMDBC is a binary classifier, it cannot have more than two classes
    print label_encoder.classes_
    if len(label_encoder.classes_) != 2:
        print "Classifier needs exactly 2 classes"
        return None, None, None, None, None
    
    #Read the train list and save the list of class and the list
    #of feature vectors
    list_class = []
    list_fv = []
    
    for img in train_set:
        list_class.append(images[img][POS_CLASSES][INDEX_ZERO])
        list_fv.append(images[img][POS_FV][INDEX_ZERO])
    
    list_train = numpy.array(list_fv)
    list_train_class = numpy.array(list_class)
    
    #Given a list of classes, transform each value in this list to a integer
    list_train_class = label_encoder.transform(list_train_class)
    print "List of classes of this experiment:", label_encoder.classes_
    
    #Read the test list and save the list of class and the list
    #of feature vectors
    list_img = test_set
    list_class = []
    list_fv = []
    
    for img in test_set:
        list_class.append(images[img][POS_CLASSES][INDEX_ZERO])
        list_fv.append(numpy.array(images[img][POS_FV][INDEX_ZERO]))
    
    list_test = numpy.array(list_fv)
    list_test_class = numpy.array(list_class)
    
    #Classification
    #--------------------------------------------------------------------------
    svmdbc = SVM.SVMDBC(approach=SVMDBC_approach)
    
    #SVMDBC Fit
    print "\tFit: Beginning"
    svmdbc.fit(list_train, list_train_class)
    print "\tFit: Done!"
    
    #Save configuration of the SVMDBC
    print svmdbc
    model_paths = []
    
    #Predict
    print "\tPredict: Beginning"
    list_predict = svmdbc.classify(list_test)
    print "\tPredict: Done"
    
    #Mapping the results into integers
    list_predict = [int(item) if item is not None else
            int(label_encoder.transform([None])) for item in list_predict]
    #Returning the result to strings
    list_predict = label_encoder.inverse_transform(list_predict)
    
    list_result = []
    for predict in list_predict:
        img_result = [0] * len(label_encoder.classes_)
        #Find all predict in the list label_encoder.classes_ and grab the
        #first index
        pos = label_encoder.classes_.tolist().index(predict)
        img_result[pos] = 1
        list_result.append(img_result)
    #--------------------------------------------------------------------------
    
    return list_img, list_test_class, list_result, label_encoder.classes_, \
            model_paths
