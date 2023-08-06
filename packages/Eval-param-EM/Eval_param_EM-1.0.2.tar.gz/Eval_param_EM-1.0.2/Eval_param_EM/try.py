# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 09:36:55 2020

@author: Eshika Mahajan
"""

import Eval_param
import pandas as pd
data = [[1,5],[2,6],[4,3]]
df = pd.DataFrame(data,columns=['Actual','Predicted'])


dataa=[1,2,3]
obj=Eval_param.Regression_Eval_Param(df)

obj.rmse(dataa,df['Actual'])
obj.rmse(dataa,df['Predicted'])
obj.rmse(df['Actual'],dataa)
obj.rmse(df['Actual'],df['Predicted'])


