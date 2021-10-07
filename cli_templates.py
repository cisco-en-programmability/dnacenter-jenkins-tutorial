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

CONFIGURATION_TEMPLATES = ""
with open('config/cli_templates.yaml', 'r') as file:
    CONFIGURATION_TEMPLATES = yaml.safe_load(file)


def validate_devices(configuration_templates):
    for configuration_template in configuration_templates:
        devices = configuration_template.get("devices", None)
        if devices:
            for device in devices:
                dnac_response = dnac.devices.get_device_list(hostname=device.get("name"))
                if not len(dnac_response.response):
                    logger.error(f"Device {device.get('name')} does not exist")
                    sys.exit(1)

def has_defined_params(devices, params):
    """
    Checks if the template has params and if the devices has those params defined
    """
    template_params = []
    for param in params:
        template_params.append(param.get("parameterName"))
    for device in devices:
        if device.get("params", None) is None:
            logger.error(f"Device {device.get('name')} does not have params defined.")
            sys.exit(1)
        for param in template_params:
            if device.get("params").get(param, None) is None:
                logger.error(f"Device {device.get('name')} does not have {param} defined.")
                sys.exit(1)
    return True



def deploy_template(project, project_id, has_params):
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
    if has_params:
        template_params = project.get("params")

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

    logger.info(f"Template {project.get('name')}-{TSTAMP} task id is: {compliance_template_task.response.taskId}")
    logger.info("Creating template. Sleeping for 10 seconds...")
    time.sleep(10)

    task = dnac.task.get_task_by_id(compliance_template_task.response.taskId)
    template_id = task.response.data
    
    dnac.configuration_templates.version_template(comments="Jenkins Deployment", templateId=template_id)

    logger.info("Versioning template. Sleeping for 10 seconds...")
    time.sleep(10)

    target_info = []
    for device in devices:
        if has_params:
            target_info.append({"id": device.get("name"), 
                                "type": "MANAGED_DEVICE_HOSTNAME",
                                "params": device.get("params")})
        else:
            target_info.append({"id": device.get("name"), "type": "MANAGED_DEVICE_HOSTNAME"})

    deploy_template_task = dnac.configuration_templates.deploy_template_v2(
        forcePushTemplate=True,
        isComposite=False,
        templateId=template_id,
        targetInfo=target_info
    )

    logger.info("Deploying template. Sleeping for 10 seconds...")
    time.sleep(10)
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

if __name__ == "__main__":
    validate_devices(CONFIGURATION_TEMPLATES)
    for configuration_template in CONFIGURATION_TEMPLATES:
        project_id = get_project(configuration_template["project"])
        if configuration_template.get("params"):
            if has_defined_params(configuration_template.get("devices"),
                                     configuration_template.get("params")):
                logger.info("Deploying template with params...")
                deploy_template(configuration_template, project_id, True)
        else:
            logger.info("Deploying template without params...")
            deploy_template(configuration_template, project_id, False)