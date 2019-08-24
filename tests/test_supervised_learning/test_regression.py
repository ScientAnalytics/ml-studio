# --------------------------------------------------------------------------- #
#                          TEST REGRESSION                                    #
# --------------------------------------------------------------------------- #
#%%
import math
import numpy as np
import pandas as pd
import pytest
from pytest import mark

from ml_studio.supervised_learning.regression import LinearRegression
from ml_studio.supervised_learning.regression import LassoRegression
from ml_studio.supervised_learning.regression import RidgeRegression
from ml_studio.supervised_learning.regression import ElasticNetRegression
from ml_studio.supervised_learning.regression import PolynomialRegression
from ml_studio.supervised_learning.regression import SGDRegression
from ml_studio.supervised_learning.regression import SGDLassoRegression
from ml_studio.supervised_learning.regression import SGDRidgeRegression
from ml_studio.supervised_learning.regression import SGDRidgeRegression
from ml_studio.supervised_learning.regression import SGDElasticNetRegression
from ml_studio.supervised_learning.regression import SGDPolynomialRegression

from ml_studio.operations.metrics import Scorer

class LinearRegressionTests:

    @mark.linear_regression    
    def test_linear_regression_training_solution(self, train_linear_regression,
                                                 analytical_solution_training_data):
        train_solution, = analytical_solution_training_data
        gd, X_train, _, y_train, _ = train_linear_regression
        y_pred = gd.predict(X_train)        
        assert all(np.isclose(gd.theta, train_solution, rtol=1e1)), "Solution is not close to analytical solution."
        assert all(np.isclose(y_train, y_pred, rtol=1e1)), "Train predictions are not close to true values."  

    @mark.linear_regression
    def test_linear_regression_test_scores(self, train_linear_regression, 
                                           regression_metric):        
        gd, _, X_test, _, y_test = train_linear_regression
        y_pred = gd.predict(X_test)        
        score = gd.score(X_test, y_test)
        assert all(np.isclose(y_test, y_pred, rtol=1e1)), "Test predictions are not close to true values."  
        r2s = r2_score(y_test, y_pred)
        print(r2s)
        if regression_metric == 'r2':
            assert score >= 0.6, "R2 score below 0.6"
        elif regression_metric == 'var_explained':
            assert score >= 0.6, "Var explained below 0.6"
        elif regression_metric == 'mean_absolute_error':
            assert score < 5, "Mean squared error greater than 5"            
        elif regression_metric == 'mean_squared_error':
            assert score < 25, "mean_squared_error > 25"            
        elif regression_metric == 'neg_mean_squared_error':
            assert score > -25, "neg_mean_squared_error > -25"            
        elif regression_metric == 'root_mean_squared_error':
            assert score < 5, "root_mean_squared_error > 5"                        
        elif regression_metric == 'neg_root_mean_squared_error':
            assert score > -5, "neg_root_mean_squared_error < -5"                                    
        elif regression_metric == 'median_absolute_error':
            assert score < 5, "median_absolute_error > 5"                                    