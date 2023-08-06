# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 12:16:13 2020

@author: Eshika Mahajan
"""

import numpy as np
import pandas as pd

#class 1 for classification models
class Classification_Eval_Param():
    
    
    def __init__(self,confusion_matrix):
        
        self.cm=confusion_matrix
        try:
            #checks whether the confusion matrix is a 2x2 matrix or not
            if self.cm.shape==(2,2):
                self.TP=self.cm[0][0]#True Positive
                self.TN=self.cm[1][1]#True Negative
                self.FP=self.cm[0][1]#false positive
                self.FN=self.cm[1][0]#false negative
               
                '''
                #finding the summ of confusion matrix
                sum_Arr=0
                for i in range(0,2):
                   for k in range(0,2):
                       sum_Arr+=self.cm[i][k]
                    
                self.sum=sum_Arr'''
                
                #finding the summ of confusion matrix
                self.sum_cm=self.cm.sum()
            
        except:
            print('confusion matrix is not a 2D array.')
            
    # VARIOUS EVALUATION PARAMETERS FOR CLASSIFICATION MODELS WITH THE HELP OF CONFUSION MATRIX   
    def accuracy(self):
        accuracy=100*((self.TP+self.TN)/(self.sum_cm))
        print(accuracy)
        return accuracy
        
    def recall(self):
        recall=self.TP / (self.TP + self.FN)
        print(recall)
        return recall
        
    def precision(self):
        precision=self.TP / (self.TP + self.FP)
        print(precision)
        return precision
        
    def F_score(self):
        f_score=(2 * self.precision * self.recall )/ (self.precision + self.recall)
        print(f_score)
        return f_score
        
    def specificity(self):
        spec=self.TN/(self.TN+self.FP)
        print(spec)
        return spec
    
    def negative_prediction(self):
        neg_pred=self.TN/(self.TN+ self.FN)
        print(neg_pred)
        return neg_pred
   
#regression models evaluation parameters
class Regression_Eval_Param():
    def __init__(self,dataframe):
        self.df=dataframe.copy()
        
       
    def correlation(self):
        correl=self.df.corr()
        print(correl)
        return correl
        
    def r_square(self):
        r_2=(self.df.corr())**2
        print(r_2)
        return r_2
        
    def rmse(self,actual,predicted):
        self.df['act']=actual
        self.df['pred']=predicted
        rmse = np.sqrt(((self.df['act'] - self.df['pred']) ** 2).mean())
        print(rmse)
        return rmse
        
    def mse(self,actual,predicted):
        self.df['actual']=actual
        self.df['predicted']=predicted
        mse = ((self.df['actual'] - self.df['predicted']) ** 2).mean()
        print(mse)
        return mse
    
    def abs_accuracy(self,actual,predicted,perm_error):
        self.df['Actual']=actual
        self.df['Predicted']=predicted
        err=perm_error
        self.df['difference']=abs(self.df['Actual']-self.df['Predicted'])
        count=self.df['difference'].isin([err]).sum()
        count=(count*100)/(len(self.df.index))
        print(count)
        return count
    
    def accuracy(self,actual,predicted):
        self.df['Actual']=actual
        self.df['Predicted']=predicted
        self.df['differ']=(self.df['Actual']-self.df['Predicted'])
        acc=sum(self.df['differ'])
        acc=(acc*100)/(sum(self.df['Actual']))
        print('accuracy in decimals = ',(acc/100))
        print(acc)
        return acc
        
        
        