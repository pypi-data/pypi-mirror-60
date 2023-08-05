from flask import Flask, request, render_template as renderTemplate;
from . import helpers;
from functools import wraps;
import json;
from rhythmic import rhythmicDB, Logger;

app = Flask(__name__);

#==========================================================================
#====================      INITIALIZATION     =========================================
#==========================================================================

deploy_storage = helpers.DeployMemoryStorage();
with rhythmicDB(db_name = "SQLite", db_filename = helpers.configuration.db_file_name) as db:
    predeployed_ids = db.execute("SELECT id FROM models_table WHERE 1");
    if len(predeployed_ids) > 0:
        for predeployed_id in predeployed_ids:
            deploy_storage.deployCell(predeployed_id[0]);

deploy_logger = Logger();

deploy_logger.writeDown("Starting RhythmicML Deploy API Server.");

#==========================================================================
#====================      DECORATORS     =========================================
#==========================================================================
def checkPost(entry_point):

    @wraps(entry_point)
    def wrapper(*args, **kwargs):
        if request.method == "POST":

            return entry_point(*args, **kwargs);

        else:

            deploy_logger.writeDown("Invalid method access attempt. \n {} \n {} \n {}".\
                                                    format(
                                                                entry_point.__name__,
                                                                args,
                                                                kwargs
                                                              )
                                                  );

            return "Only POST requests are presumed.";

    return wrapper;

#==========================================================================
#====================      SERVER ROUTES     ========================================
#==========================================================================
@app.route("/")
def index():

    models_list = helpers.getModelsList();

    deploy_logger.writeDown("Access to web-UI; \n Models List: {}".format(models_list));

    return renderTemplate("index.html", models_list = models_list);


@app.route("/deploy", methods = ["POST"])
@checkPost
def deployModelData():

    global deploy_storage;

    result = helpers.deployModel(request.files);
    request.close();
    result_json = json.dumps(result);

    model_deploy_id = result["model_deploy_id"];

    deploy_storage.deployCell(model_deploy_id);

    deploy_logger.writeDown("A model deployed: \n {}".format(result_json));

    return result_json;

@app.route("/score/<model_deploy_id>", methods = ["POST"])
@checkPost
def scoreModel(model_deploy_id):

    global deploy_storage;

    data_json = request.data.decode();
    the_model = deploy_storage.fetchCell(model_deploy_id);

    if the_model:
        result_json = the_model(data_json);
    else:
        result_json = json.dumps({"Error":"model with deploy id = {} not found".format(model_deploy_id)});

    deploy_logger.writeDown("Model deploy_id = {} scoring request: \
                                            \n Input Data: {}\
                                            \n Result: {}\
                                            ".format(
                                                            model_deploy_id,
                                                            data_json,
                                                            result_json
                                                        )
                                          );

    return result_json;

@app.route("/status/<model_deploy_id>", methods = ["POST"])
@checkPost
def getModelStatus(model_deploy_id):

    global deploy_storage;

    the_model = deploy_storage.fetchCell(model_deploy_id);

    if the_model:
        result_string = the_model.lifeSign();
    else:
        result_string = "Error: model with deploy id = {} not found".format(model_deploy_id);

    deploy_logger.writeDown("Model deploy_id = {} status request. \n Status: {}".\
                                            format(
                                                        model_deploy_id,
                                                        result_string
                                                      )
                                         );

    return result_string;

#==========================================================================
#============================= HELPERS =======================================
#==========================================================================
@app.route("/helpers/confirmation_dialogue", methods = ["POST", "GET"])
@checkPost
def renderConfirmationDialogue():

    data_json = request.data.decode();
    data = json.loads(data_json);

    deploy_logger.writeDown("Confirmation called: \n{}".format(data_json));
# confirmation dialogue parameters are the following (passed as an object):
# confirmation_message - string, the statement to confirm
# helper_url - string, an url to request if confirmation is positive
# data_for_helper - string, data to send with that request
# confirmation_result - string: 
#      "refresh" - call asyncPostRequestWithRefresh
#      "value" - call asyncPostRequest(..., to_innerHTML = false)
#      "html" - call regular asyncPostRequest();
# result_element_id - string, dom element id to use in "value" and "html" cases

    return renderTemplate("confirmation_dialogue.html", confirmation_dialogue_parameters = data);


@app.route("/helpers/remove_deployment/<model_deploy_id>", methods = ["POST", "GET"])
@checkPost
def removeDeployment(model_deploy_id):

    deploy_storage.killCell(model_deploy_id);

    deploy_logger.writeDown("Model deploy_id = {} deployment killed.".format(model_deploy_id));

    return helpers.removeModel(model_deploy_id);


#==========================================================================
#==========================================================================
#==========================================================================

def runAPI(app, host = helpers.configuration.host, port = helpers.configuration.port):
    """
    runAPI(app, host = host, port = port):  
    app is a Flask app
    """

    app.run(debug = True, host = host, port = port);

    return True;

if __name__ == "__main__":

    runAPI(app);
