__author__ = 'Srikandan Raju, Sathish Anandha'
__copyright__ = 'Copyright (C) 2007 Free Software Foundation'
__license__ = 'GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007'
__version__ = '1.0.2'
__maintainer__ = 'Srikandan Raju, Sathish Anandha'

# Importing required packages
def import_required_package():
    try:
        global grid_cv
        global reg_score_class
        global classify_score_class
        
        from sklearn.model_selection import GridSearchCV as grid_cv
        from model_analyzer.score_model import regression_score as reg_score_class
        from model_analyzer.score_model import classification_score as classify_score_class
        
        return 'imported'
    
    except Exception as e:
        e = 'Kindly install or update Packages \n' + str(e)
        return e

# gridsearch_cv function runs the GridSearchCV
def gridsearch_cv(model, tune_param, score_type, data, prob):
    output = import_required_package()
    
    if output == 'imported':
        try:
            grid_search = grid_cv(estimator = model, 
                                param_grid = tune_param, scoring = score_type, 
                                n_jobs = -1, cv = 10, verbose = 3)
            grid_search.fit(data[0], data[1])
            grid_predict = grid_search.predict(data[2])
            # score = ''
            # if prob == 'regression':
            #     score = reg_score_class.get_model_score(score_type, data, grid_predict)
            # elif  prob == 'classification':     
            #     score = classify_score_class.get_model_score(score_type, data, grid_predict)
                
            return str(grid_search.best_score_), str(grid_search.best_params_)
        except Exception as e:
            return e
    else:
        return output