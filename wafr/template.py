from textwrap import indent
import boto3
import config.config as conf
import wafr.lens as lens

well_architected_tool_client = boto3.client('wellarchitected')

MAX_ANSWER_COUNT = 30

INDENT_SIZE = 2
INDENT_0 = INDENT_SIZE * 0
INDENT_1 = INDENT_SIZE * 1
INDENT_2 = INDENT_SIZE * 2
INDENT_3 = INDENT_SIZE * 3
INDENT_4 = INDENT_SIZE * 4

PILLAR_ID_INDEX = 1
pillar_label_name_dict = [['SEC', 'security'], 
                          ['REL', 'reliability'],
                          ['OPS', 'operationalExcellence'],
                          ['PERF', 'performance'],
                          ['COST', 'costOptimization'],
                          ['SUS', 'sustainability']]


def start_generation(workload_id, output_file, save_workload, list_workloads, custom_lens):
    if list_workloads:
        list_all_workloads()
    else:
        write_template(output_file, generate_new_template(workload_id, save_workload, custom_lens))

def list_all_workloads():
    for workload in well_architected_tool_client.list_workloads(MaxResults=20)['WorkloadSummaries']:
        print(f"Name: {workload['WorkloadName']}, Id: {workload['WorkloadId']}")

def generate_new_template(workload_id, save_workload, custom_lens):
    template = []
    lens_alias = conf.STANDARD_LENS_ALIAS
    if custom_lens == conf.EKS_LENS_ALIAS:
        lens_alias = lens.get_lens_alias(conf.EKS_LENS_LABEL)
        append_new_line(template, INDENT_0, conf.LENS_KEY, conf.EKS_LENS_LABEL)
    else:
        append_new_line(template, INDENT_0, conf.LENS_KEY, conf.STANDARD_LENS_LABEL)
    for pillar in pillar_label_name_dict:
        questions_with_answers = list_all_questions_with_answers_from_workload(workload_id, pillar, lens_alias)
        append_pillar(template, pillar[PILLAR_ID_INDEX])
        question_counter = init_question_counter()
        for question in extract_question_dict(questions_with_answers):
            question_details = get_question_answer_details(workload_id, question['QuestionId'], lens_alias)
            append_question_label(template, pillar, question_counter)
            append_question_id(template, question_id=question['QuestionId'])
            append_question_title(template, question_title=question['QuestionTitle'])
            if 'Notes' in question_details:
                append_question_note(template, question_note=question_details['Notes'])
            question_applicable = bool(question['IsApplicable'])
            if save_workload and not question_applicable:
                append_answer_not_applicable(template)
            else:
                append_answers(template, question, save_workload, question_details)                

            question_counter = increase_question_counter(question_counter)
    return template

def extract_question_dict(questions_with_answers):
    return questions_with_answers['AnswerSummaries']

def list_all_questions_with_answers_from_workload(workload_id, pillar, lens_label):
    return well_architected_tool_client.list_answers(WorkloadId=workload_id,
                        LensAlias=lens_label,
                        PillarId=pillar[PILLAR_ID_INDEX],
                        MaxResults=MAX_ANSWER_COUNT)

def init_question_counter():
    return 1

def increase_question_counter(question_counter):
    return question_counter + 1

def append_pillar(template, pillar):
    append_new_line(template, indent=INDENT_0, key=pillar, value='')

def append_question_label(template, pillar, count):
    append_new_line(template, INDENT_1, key='- label', value=f"{str(pillar[0])} {str(count)}")

def append_question_id(template, question_id):
    append_new_line(template, indent=INDENT_2, key='question_id', value=question_id)

def append_question_title(template, question_title):
    append_new_line(template, indent=INDENT_2, key='title', value=question_title)

def append_question_note(template, question_note):
    question_note_lines = question_note.split('\n')
    question_note = '|-\n' 
    for i, line in enumerate(question_note_lines):
        question_note = question_note + str(f"{'':<{INDENT_3}}{line}") + add_new_line(index=i, last_index=len(question_note_lines) - 1)
    append_new_line(template, indent=INDENT_2, key='notes', value=question_note)

def add_new_line(index, last_index):
    if index < last_index:
        return '\n'
    return ''
    
def append_answers(template, question, save_workload, question_details):
    append_answers_header(template)
    if 'ChoiceAnswers' in question_details:
        marked_answers = question_details['ChoiceAnswers']
    else:
        marked_answers = []
    for answers in question['Choices']:
        append_answer_id(template, answer_id=answers['ChoiceId'])
        append_answer_title(template, answers['Title'])
        if save_workload:
            append_answer_status_and_comments(template, answers, marked_answers)

def append_answers_header(template):
    append_new_line(template, indent=INDENT_2, key='answers', value='')

def append_answer_id(template, answer_id):
    append_new_line(template, indent=INDENT_3, key='- id', value=answer_id)

def append_answer_title(template, answer_title):
    append_new_line(template, indent=INDENT_4, key='title', value=answer_title)

def append_answer_status_and_comments(template, default_answers, marked_answers):
    for marked_answer in marked_answers:
        if marked_answer['ChoiceId'] == default_answers['ChoiceId']:
            append_answer_status(template, status=marked_answer['Status'])
            if marked_answer['Status'] == 'NOT_APPLICABLE':
                append_answer_reason(template, reason=marked_answer['Reason'])                
                append_answer_notes(template, notes=marked_answer['Notes'])

def append_answer_status(template, status):
    append_new_line(template, indent=INDENT_4, key='status', value=status)

def append_answer_reason(template, reason):
    append_new_line(template, indent=INDENT_4, key='reason', value=reason)

def append_answer_notes(template, notes):
    append_new_line(template, indent=INDENT_4, key='notes', value=notes)

def append_answer_not_applicable(template):
    append_new_line(template, indent=INDENT_2, key='not_applicable', value='true')

def append_new_line(template, indent, key, value):
    template.append(str(f"{'':<{indent}}{key}: {value}"))

def get_question_answer_details(workload_id, question_id, lens_label):
    result = well_architected_tool_client.get_answer(
        WorkloadId=workload_id,
        LensAlias=lens_label,
        QuestionId=question_id)
    return result['Answer']

def write_template(output_file, template):
    if output_file == '':
        for line in template:
            print(line)
    else:
        f = open(output_file, "w")
        for line in template:
            f.write(line + '\n')
  
