from dnacentersdk import api
from datetime import datetime
import yaml
import time
import sys
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)



dnac = api.DNACenterAPI()

today = datetime.today()
TSTAMP = today.strftime("%Y-%m-%dT%H-%M-%S")

CONFIG = ""
TEMPLATE = ""
with open('deploy/dnac.yaml', 'r') as file:
    CONFIG = yaml.safe_load(file)

def has_defined_variables(devices, variables):
    """
    Checks if the template has variables and if the devices has those variables defined
    """
    template_variables = []
    for variable in variables:
        template_variables.append(variable.get("parameterName"))
    for device in devices:
        if device.get("variables", None) is None:
            return False
        for variable in template_variables:
            if device.get("variables").get(variable, None) is None:
                return False
    return True

def deploy_template(project, project_id, has_variables):
    devices = project.get("devices")
    template_filename = project.get("file")
    product_family = project.get("product_family")
    device_types = []
    for family in product_family:
        device_types.append({"productFamily": family})

    template_file = ""
    with open(f"templates/{template_filename}", 'r') as file:
        template_file = file.read()
    template_params  = []
    if has_variables:
        template_params = project.get("variables")
    compliance_template_task = dnac.configuration_templates.create_template(
        project_id = project_id,
        author="jenkins",
        composite=False,
        description=f"Jenkins deployment {TSTAMP}",
        deviceTypes=device_types,
        softwareType="IOS-XE",
        softwareVariant="XE",
        templateContent=template_file,
        language="JINJA",
        name=f"{project.get('name')}-{TSTAMP}",
        templateParams=template_params
    )

    logger.info(f"Compliance project {project.get('name')}-{TSTAMP} task id is: {compliance_template_task.response.taskId}")
    logger.info("Sleeping for 60 seconds...")
    time.sleep(60)

    task = dnac.task.get_task_by_id(compliance_template_task.response.taskId)
    template_id = task.response.data
    
    dnac.configuration_templates.version_template(comments="Jenkins Deployment", templateId=template_id)

    logger.info("Sleeping for 10 seconds...")
    time.sleep(10)

    target_info = []
    for device in devices:
        if has_variables:
            target_info.append({"id": device.get("name"), 
                                "type": "MANAGED_DEVICE_HOSTNAME",
                                "params": device.get("variables")})
        else:
            target_info.append({"id": device.get("name"), "type": "MANAGED_DEVICE_HOSTNAME"})

    deploy_template_task = dnac.configuration_templates.deploy_template_v2(
        forcePushTemplate=True,
        isComposite=False,
        templateId=template_id,
        targetInfo=target_info
    )

    logger.info("Sleeping for 60 seconds...")
    time.sleep(60)
    task = dnac.task.get_task_by_id(deploy_template_task.response.taskId)
    logger.info(f"Deployment status is: {task.response.progress}")

def get_project(name):
    projects = dnac.configuration_templates.get_projects(name=name)
    if len(projects) > 0:
        return projects[0].id
    project_task = dnac.configuration_templates.create_project(name=name)
    time.sleep(5)
    project_task_data = dnac.task.get_task_by_id(project_task.response.taskId)
    return project_task_data.response.data

def deploy_configuration_templates():
    configuration_templates = CONFIG.get("configuration_templates", None)
    for configuration_template in configuration_templates:
        project_id = get_project(configuration_template["project"])
        if configuration_template.get("variables"):
            if has_defined_variables(configuration_template.get("devices"),
                                     configuration_template.get("variables")):
                logger.info("Deploying template with variables")
                deploy_template(configuration_template, project_id, True)
        else:
            logger.info("Deploying template without variables")
            deploy_template(configuration_template, project_id, False)

def deploy_sites():
    return


if __name__ == "__main__":
    # execute only if run as a script
    deploy_configuration_templates()
    deploy_sites()