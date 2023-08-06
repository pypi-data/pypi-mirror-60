

def import_required_package():
    try:
        global grid_cv
        global reg_score_class
        
        from sklearn.model_selection import GridSearchCV as grid_cv
        from model_analyzer.score_model import regression_score as reg_score_class
        
        return 'imported'
    
    except Exception as e:
        e = 'Kindly install or update Packages \n' + str(e)
        return e
    
def gridsearch_cv(model, tune_param, score_type, data):
    output = import_required_package()
    
    if output == 'imported':
        try:
            grid_search = grid_cv(estimator = model, 
                                param_grid = tune_param, scoring = score_type, 
                                n_jobs = -1, cv = 10, verbose = 3)
            grid_search.fit(data[0], data[1])
            grid_predict = grid_search.predict(data[2])
            score = reg_score_class.get_model_score(score_type, data, grid_predict)
            return score, str(grid_search.best_score_), str(grid_search.best_params_)
        except Exception as e:
            return e
    else:
        return output