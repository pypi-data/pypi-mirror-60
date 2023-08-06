

def import_required_packages():
    try:
        global reg_class
        from model_analyzer.models import regression as reg_class
            
        return 'imported'
    except Exception as  e:
        e = 'Kindly install or update Packages \n' + str(e)
        return e
        
# Main method
def predector(prob_type, data, alg_type=['linear'], score_type=['r2'], 
              tune_param='default'):
    import_status = import_required_packages()
    
    try:
        if import_status == 'imported':
            prob_type = str(prob_type).lower()
            
            if prob_type == 'regression':
                output = regression(data, alg_type, score_type, tune_param)
            # elif prob_type == 'classification':
            #     classification(data, opt_param)
            # elif prob_type == 'clustering':
            #     clustering(data, opt_param)
            # elif prob_type == 'nltk':
            #     natural_language(data, opt_param)
            else:
                output = 'Not a valid Machine Learning Techniques'
            return output
        else:
            return import_status
    except Exception as e :
        return e

 
def regression(data, alg_type, score_type, tune_param):
    reg_main = reg_class.main_regression
    try:
        output = reg_main.regression(data, alg_type, score_type, tune_param, 
                                     reg_main)
        return output
    except Exception as e :
        return e