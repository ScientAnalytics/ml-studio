# --------------------------------------------------------------------------- #
#                     TEST LEARNING RATE SCHEDULES                            #
# --------------------------------------------------------------------------- #
#%%
import math
import numpy as np
import pytest
from pytest import mark

from ml_studio.supervised_learning.training.learning_rate_schedules import TimeDecay
from ml_studio.supervised_learning.training.learning_rate_schedules import StepDecay
from ml_studio.supervised_learning.training.learning_rate_schedules import NaturalExponentialDecay
from ml_studio.supervised_learning.training.learning_rate_schedules import ExponentialDecay
from ml_studio.supervised_learning.training.learning_rate_schedules import InverseScaling
from ml_studio.supervised_learning.training.learning_rate_schedules import PolynomialDecay
from ml_studio.supervised_learning.training.learning_rate_schedules import Adaptive
from ml_studio.supervised_learning.regression import LinearRegression

class LearningRateScheduleTests:

    # ----------------------------------------------------------------------- #
    #                             Time Decay                                  #
    # ----------------------------------------------------------------------- #

    @mark.time_decay_learning_rate
    @mark.learning_rate_schedules
    def test_time_decay_learning_rate_schedule_wo_staircase(self, get_regression_data):
        logs = {}
        exp_result = [0.0909090909,	0.0833333333,	0.0769230769,	0.0714285714,	0.0666666667]
        act_result = []        
        lrs = TimeDecay(learning_rate=0.1, decay_rate=0.5, decay_steps=5)
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Time decay not working"
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Time decay not working in model"

    @mark.learning_rate_schedules
    def test_time_decay_learning_rate_schedule_w_staircase(self, get_regression_data):
        logs = {}
        exp_result = [0.1000000000,	0.1000000000,	0.1000000000,	0.1000000000,	0.0666666667]
        act_result = []        
        lrs = TimeDecay(learning_rate=0.1, decay_steps=5, decay_rate=0.5, staircase=True)
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Time decay with step not working"
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Time decay with step not working in model"

    # ----------------------------------------------------------------------- #
    #                             Step Decay                                  #
    # ----------------------------------------------------------------------- #

    @mark.step_decay_learning_rate
    @mark.learning_rate_schedules
    def test_step_decay_learning_rate_schedule(self, get_regression_data):
        logs = {}
        exp_result = [0.1000000000,	0.1000000000,	0.1000000000,	0.0500000000,	0.0500000000]
        act_result = []        
        lrs = StepDecay(learning_rate=0.1, decay_rate=0.5, decay_steps=5)
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Step decay not working"
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Step decay not working in model"        

    # ----------------------------------------------------------------------- #
    #                     Natural Exponential Decay                           #
    # ----------------------------------------------------------------------- #

    @mark.learning_rate_schedules
    def test_nat_exp_decay_learning_rate_schedule_wo_staircase(self, get_regression_data):
        logs = {}
        exp_result = [0.0904837418,0.0818730753,0.0740818221,0.0670320046,0.0606530660]
        act_result = []        
        lrs = NaturalExponentialDecay(learning_rate=0.1, decay_rate=0.5, decay_steps=5)
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Natural exponential decay not working"
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Natural exp decay not working in model"        

    @mark.learning_rate_schedules
    def test_nat_exp_decay_learning_rate_schedule_w_staircase(self, get_regression_data):
        logs = {}
        exp_result = [0.1000000000,	0.1000000000,	0.1000000000,	0.1000000000,	0.0606530660]
        act_result = []        
        lrs = NaturalExponentialDecay(learning_rate=0.1, decay_steps=5, decay_rate=0.5,
                                      staircase=True)
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Natural exponential decay with steps not working"
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Natural exp decay with steps not working in model"                

    # ----------------------------------------------------------------------- #
    #                           Exponential Decay                             #
    # ----------------------------------------------------------------------- #

    @mark.learning_rate_schedules
    def test_exp_decay_learning_rate_schedule_wo_staircase(self, get_regression_data):
        logs = {}
        exp_result = [0.0870550563,	0.0757858283,	0.0659753955,	0.0574349177,	0.0500000000]
        act_result = []        
        lrs = ExponentialDecay(learning_rate=0.1, decay_rate=0.5, decay_steps=5)
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Exponential decay not working"
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Exponential decay not working in model"                

    @mark.learning_rate_schedules
    def test_exp_decay_learning_rate_schedule_w_staircase(self, get_regression_data):
        logs = {}
        exp_result = [0.1,0.1,0.1,0.1,0.05]
        act_result = []        
        lrs = ExponentialDecay(learning_rate=0.1, decay_rate=0.5, decay_steps=5, staircase=True)
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Exponential decay with steps and staircase not working"       
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Exponential decay with steps and staircase not working in model"                         
    
    # ----------------------------------------------------------------------- #
    #                           Inverse Scaling                               #
    # ----------------------------------------------------------------------- #

    @mark.learning_rate_schedules
    def test_inv_scaling_learning_rate_schedule(self, get_regression_data):
        logs = {}
        exp_result = [0.1,0.070710678,0.057735027,0.05,0.04472136]
        act_result = []        
        lrs = InverseScaling(learning_rate=0.1, power=0.5)    
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Inverse scaling not working"
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Inverse scaling not working in model"                        

    # ----------------------------------------------------------------------- #
    #                           Polynomial Decay                              #
    # ----------------------------------------------------------------------- #

    @mark.learning_rate_schedules
    def test_polynomial_decay_learning_rate_schedule_wo_cycle(self, get_regression_data):
        logs = {}
        exp_result = [0.0895,0.0775,0.0633,0.0448,0.0001]
        act_result = []        
        lrs = PolynomialDecay(learning_rate=0.1, decay_steps=5, power=0.5,
                              end_learning_rate=0.0001)
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Polynomial decay not working"
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Polynomial decay not working in model"

    @mark.learning_rate_schedules
    def test_polynomial_decay_learning_rate_schedule_w_cycle(self, get_regression_data):
        logs = {}
        exp_result = [0.0895,0.0775,0.0633,0.0448,0.0001]
        act_result = []        
        lrs = PolynomialDecay(learning_rate=0.1, decay_steps=5, power=0.5,
                              end_learning_rate=0.0001, cycle=True)
        iterations =  [i+1 for i in range(5)]
        for i in iterations:
            logs['epoch'] = i
            act_result.append(lrs(logs))
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Polynomial decay with cycle not working"   
        exp_result.insert(0, 0.1)
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, epochs=6)
        model.fit(X,y)
        assert all(np.isclose(exp_result,model.history.epoch_log.get('learning_rate'),rtol=1e-1)), "Polynomial decay with cycle not working in model"        

    # ----------------------------------------------------------------------- #
    #                              Adaptive                                   #
    # ----------------------------------------------------------------------- #        

    @mark.learning_rate_schedules
    def test_adaptive_learning_rate_schedule(self, get_regression_data):
        logs = {}
        exp_result = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.05,0.05]
        act_result = []        
        lrs = Adaptive(learning_rate=0.1, decay_rate=0.5, precision=0.01, patience=5)
        logs['learning_rate'] = 0.1
        cost = [5,5,5,5,5,4,4,4,4,4,4,3]        
        iterations =  [i+1 for i in range(12)]
        for i in iterations:
            logs['epoch'] = i
            logs['train_cost'] = cost[i-1]
            learning_rate = lrs(logs)
            act_result.append(learning_rate)
            logs['learning_rate'] = learning_rate
        assert all(np.isclose(exp_result,act_result,rtol=1e-1)), "Adaptive decay with cycle not working"             
        exp_result.insert(0, 0.1)        
        X, y = get_regression_data
        model = LinearRegression(learning_rate=lrs, batch_size=1, epochs=100)
        model.fit(X,y)        
        learning_rates = model.history.epoch_log.get('learning_rate')
        assert learning_rates[0] != learning_rates[-1], "Adaptive learning rate didn't change" 