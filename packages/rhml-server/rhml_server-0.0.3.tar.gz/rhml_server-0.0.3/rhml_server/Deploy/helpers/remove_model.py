from rhythmic import rhythmicDB, faultReturnHandler;
from . import configuration;
from .scan_folder import scanModelFolder, scanFolder;
from os import remove, rmdir as rmDir, getcwd as getCurrentWorkingDir;

@faultReturnHandler
def removeModel(model_deploy_id):

    working_dir_path = getCurrentWorkingDir();
    storage_dir = "{}/{}".format(working_dir_path, configuration.storage_folder_name);
    deploy_dir = "{}/model{}".format(storage_dir, model_deploy_id);

    with rhythmicDB(configuration.db_name, configuration.db_file_name) as db:

        db.execute(
            """
            DELETE FROM models_table WHERE id = '{}';
            """.format(
                                model_deploy_id
                            )
            );

    deployment_files = scanModelFolder(deploy_dir);
    deployment_folders = [deploy_dir];

    for the_file in deployment_files:
        if deployment_files[the_file]["is_dir"]:
            deployment_folders.append(the_file);
        else:
            remove(the_file);

    if len(deployment_folders) > 0:
        for the_folder in sorted(deployment_folders, key = lambda folder_name: len(folder_name), reverse = True):
            rmDir(the_folder);

    return "Success";
