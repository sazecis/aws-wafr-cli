from calendar import c
import boto3
import yaml
from datetime import datetime

import config.config as conf
import wafr.lens as lens

well_architected_tool_client = boto3.client('wellarchitected')

def create_new_workload(template_file_path, workload_name, description, environment, account_ids, regions, review_owner, disable_standard):
    template = get_template_content(template_file_path)
    lens_alias = get_lens_alias(template_file_path)
    if not lens_alias:
        print('No lens exist for this type of template. Please publish first the lens and then create the workload.')
    else:
        workload = well_architected_tool_client.create_workload(
            WorkloadName=workload_name,
            Description=description,
            Environment=convert_environment(environment),
            AccountIds=account_ids,
            AwsRegions=regions,
            ReviewOwner=review_owner,
            PillarPriorities=['security', 'reliability', 'operationalExcellence', 'performance', 'costOptimization', 'sustainability'],
            Lenses=[lens_alias],
            ClientRequestToken=str(datetime.now())
        )
        workload_id = workload['WorkloadId']
        if disabling_standard_lens(disable_standard, lens_alias):
            disable_standard_questions(workload_id, get_template_content('templates/standard.yaml'))
        apply_marks_in_well_architected_tool(workload_id, template, lens_alias)
        print(f"Workload updated with the marked question from the {template_file_path} file")

def update_existing_workload(template_file_path, workload_name, disable_standard):
    template = get_template_content(template_file_path)
    lens_alias = get_lens_alias(template_file_path)
    workload_id = get_workload_id(workload_name)    
    if adding_new_lens(workload_id, lens_alias) and update_allowed():
        associate_new_lens(workload_id, lens_alias)
    apply_marks_in_well_architected_tool(workload_id, template, lens_alias)
    if disabling_standard_lens(disable_standard, lens_alias):
        disable_standard_questions(workload_id, get_template_content('templates/standard.yaml'))
    print(f"Workload updated with the marked question from the {template_file_path} file")

def disabling_standard_lens(disable_standard, lens_alias):
    return disable_standard and lens_alias != conf.STANDARD_LENS_ALIAS

def adding_new_lens(workload_id, lens_alias):
    workload_lenses = well_architected_tool_client.get_workload(
            WorkloadId=workload_id
        )['Workload']['Lenses']
    if lens_alias not in workload_lenses:
        return True
    return False

def update_allowed():
    choice = ''
    while choice.lower() not in ['y', 'n']:
        print('The lens template type is different than the one in the workload. Do you want to add this lens to the workload? (y/N)')
        choice = input()
        if choice=='':
            choice = 'n'
        else: 
            choice = str(choice).lower()
    if choice == 'y':
        return True
    return False

def associate_new_lens(workload_id, lens_alias):
    well_architected_tool_client.associate_lenses(
        WorkloadId=workload_id,
        LensAliases=[
            lens_alias
        ]
    )

def convert_environment(environment):
    if environment == 'prod':
        environment = 'PRODUCTION'
    else:
        environment = 'PREPRODUCTION'        
    return environment

def get_workload_id(workload_name):
    workload_list = well_architected_tool_client.list_workloads()['WorkloadSummaries']
    for workload in workload_list:
        if workload['WorkloadName'] == workload_name:
            return workload['WorkloadId']

def get_lens_alias(template_file_path):
    with open(template_file_path, 'r') as file:
        template = yaml.full_load(file)    
    lens_alias = lens.get_lens_alias(template['lens'])
    return lens_alias

def get_template_content(template_file_path):
    with open(template_file_path, 'r') as file:
        template = yaml.full_load(file)    
    del template['lens']
    return template


def apply_marks_in_well_architected_tool(workload_id, template, lens_alias):
    for pillar in template:
        for question in template[pillar]:
            if 'notes' in question:
                notes = question['notes']
            else:
                notes = ''
            if 'not_applicable' in question and question['not_applicable']:
                well_architected_tool_client.update_answer(
                    WorkloadId=workload_id,
                    LensAlias=lens_alias,
                    QuestionId=question['question_id'],
                    IsApplicable=False,
                    Notes=notes 
                )                
            else:
                for answer in question['answers']:
                    if 'status' in answer:
                        update_answer(
                            answer,
                            workload_id,
                            question_id=question['question_id'],
                            notes=notes,
                            lens_alias=lens_alias
                        )

def disable_standard_questions(workload_id, template):
    for pillar in template:
        for question in template[pillar]:
            well_architected_tool_client.update_answer(
                WorkloadId=workload_id,
                LensAlias=conf.STANDARD_LENS_ALIAS,
                QuestionId=question['question_id'],
                IsApplicable=False,
                Notes='' 
            )                


def update_answer(answer, workload_id, question_id, notes, lens_alias):
    if answer_is_selected(answer):
        status = {
            answer['id']: {
                'Status': answer['status']
            }
        }
    else:
        status = {
            answer['id']: {
                'Status': answer['status'],
                'Reason': answer['reason'],
                'Notes': answer['notes']
            }
        }
    well_architected_tool_client.update_answer(
        WorkloadId=workload_id,
        LensAlias=lens_alias,
        QuestionId=question_id,
        ChoiceUpdates=status,
        Notes=notes
    )

def answer_is_selected(answer):
    return answer['status'] == 'SELECTED'
