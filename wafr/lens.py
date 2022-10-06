import boto3
import json
import config.config as conf

well_architected_tool_client = boto3.client('wellarchitected')

def publish_lens(lens_file_path, lens_version):
    lens_alias = import_lens(lens_file_path)
    print(f'Publishing lens alias {lens_alias} with version {lens_version}')
    well_architected_tool_client.create_lens_version(        
        LensAlias=lens_alias,
        LensVersion=lens_version
    )

def import_lens(lens_file_path):
    lens_temlate = load_template(lens_file_path)
    lens_name = get_lens_name(lens_temlate)
    print(f'Importing lens with name: {lens_name}')
    lens_alias = get_lens_alias(lens_name)
    if lens_alias:
        well_architected_tool_client.import_lens(
            LensAlias=lens_alias,
            JSONString=json.dumps(lens_temlate)
        )
    else:
        lens_alias = well_architected_tool_client.import_lens(
            JSONString=json.dumps(lens_temlate)
        )['LensArn']
    return lens_alias

def load_template(lens_file_path):
    with open(lens_file_path) as f:
        json_content = json.load(f)
    return json_content

def get_lens_alias(lens_name):
    lenses = well_architected_tool_client.list_lenses()
    for lens in lenses['LensSummaries']:
        if lens['LensName'] == lens_name:
            return lens['LensArn']
    return None

def get_lens_name(template):
    return template['name']