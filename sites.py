from dnacentersdk import api
import yaml
import sys
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

dnac = api.DNACenterAPI()

SITES = ""
with open('config/sites.yaml', 'r') as file:
    SITES = yaml.safe_load(file)

def deploy_sites(sites):
    area = {
        "type": "area",
        "site": {
            "area": {
                "name": "",
                "parentName": ""
            }
        }
    }
    
    building = {
        "type": "building",
        "site": {
            "building": {
                "name": "",
                "parentName": "",
                "latitude": 0.0,
                "longitude":0.0 
            }
        }
    }

    floor = {
        "type": "floor",
        "site": {
            "floor": {
                "name": "",
                "parentName": "",
                "height": 0,
                "length": 0,
                "width": 0,
                "rfModel": ""
            }
        }
    }
    
    for site in sites:
        if site["type"] == 'area':
            area["site"]["area"]["name"] = site["name"]
            area["site"]["area"]["parentName"] = site["parentName"]
            logger.info("Deploying area...")
            exists = 0 
            try:
                dnac_response = dnac.sites.get_site(name=f'{site.get("parentName")}/{site.get("name")}')
                if len(dnac_response.response):
                    exists = 1
                    logger.error(f'Site {site.get("parentName")}/{site.get("name")} already exists')
                else:
                    dnac.sites.create_site(payload=area)
            except:
                dnac.sites.create_site(payload=area)
            if exists:
                sys.exit(1)
        elif site["type"] == 'building':
            building["site"]["building"]["name"] = site["name"]
            building["site"]["building"]["parentName"] = site["parentName"]
            building["site"]["building"]["latitude"] = site["latitude"]
            building["site"]["building"]["longitude"] = site["longitude"]
            dnac.sites.create_site(payload=building)
        elif site["type"] == 'floor':
            floor["site"]["floor"]["name"] = site["name"]
            floor["site"]["floor"]["parentName"] = site["parentName"]
            floor["site"]["floor"]["height"] = site["height"]
            floor["site"]["floor"]["length"] = site["length"]
            floor["site"]["floor"]["width"] = site["width"]
            floor["site"]["floor"]["rfModel"] = site["rfModel"]
            dnac.sites.create_site(payload=floor)

 
if __name__ == "__main__":
    deploy_sites(SITES)