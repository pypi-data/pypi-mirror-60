from rhythmic import rhythmicDB;
from . import configuration;
from .db_record_to_dictionary import modelPropertiesDictionary;


def getModelsList():

    the_models_list = [];

    with rhythmicDB(db_name = "SQLite", db_filename = configuration.db_file_name) as db:
        deployed_models = db.execute("SELECT * FROM models_table WHERE 1");

    if len(deployed_models) > 0:
        for the_model_data_row in deployed_models:
            the_models_list.append(modelPropertiesDictionary(the_model_data_row));

    return the_models_list;
