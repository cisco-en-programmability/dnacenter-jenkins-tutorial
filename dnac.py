from dnacentersdk import api
from datetime import datetime
import time
import csv

dnac = api.DNACenterAPI()

devices = dnac.devices.get_device_list(family="Switches and Hubs")

for device in devices.response:
    print("{:20s} {}".format(device.hostname, device.upTime))

TEMPLATE = ""
with open('deploy/template.j2', 'r') as file:
    TEMPLATE = file.read()

today = datetime.today()
TSTAMP = today.strftime("%Y-%m-%dT%H-%M-%S")
print(TSTAMP)

def deploy_template(device_name):
    compliance_projects = dnac.configuration_templates.get_projects(name="Compliance")
    print(f"Compliance Project ID is: {compliance_projects[0].id}")

    device_types = [{"productFamily": "Routers"}, {"productFamily": "Switches and Hubs"}]
    compliance_template_task = dnac.configuration_templates.create_template(
        project_id = compliance_projects[0].id,
        author="jenkins",
        composite=False,
        description=f"Jenkins deployment {TSTAMP}",
        deviceTypes=device_types,
        softwareType="IOS-XE",
        softwareVariant="XE",
        templateContent=TEMPLATE,
        language="JINJA",
        name=f"compliance-{device_name}-{TSTAMP}"
    )

    print(f"Compliance project task id is: {compliance_template_task.response.taskId}")
    time.sleep(60)

    task = dnac.task.get_task_by_id(compliance_template_task.response.taskId)
    template_id = task.response.data
    
    dnac.configuration_templates.version_template(comments="Jenkins Deployment", templateId=template_id)

    time.sleep(10)

    deploy_template_task = dnac.configuration_templates.deploy_template_v2(
        forcePushTemplate=True,
        isComposite=False,
        templateId=template_id,
        targetInfo=[{"id": device_name, "type": "MANAGED_DEVICE_HOSTNAME"}]
    )

    task = dnac.task.get_task_by_id(deploy_template_task.response.taskId)
    print(task)

with open('deploy/hosts.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    next(csvreader)
    for row in csvreader:
        deploy_template(row[0])
