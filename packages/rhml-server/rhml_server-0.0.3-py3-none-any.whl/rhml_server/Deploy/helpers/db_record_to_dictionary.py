from rhythmic.general import faultReturnHandler;

@faultReturnHandler
def modelPropertiesDictionary(sql_row_list):
    """
    modelPropertiesDictionary(sql_row_list)
    transforms a row gotten via SQL request (list), to a dictionary

    affects .get_models_list.py
    """
    
    properties_dictionary = \
    {
        "id": sql_row_list[0],
        "name": sql_row_list[1],
        "last_deploy_timestamp": sql_row_list[2],
        "active_version": sql_row_list[3],
        "build_id": sql_row_list[4]
    };

    return properties_dictionary;
