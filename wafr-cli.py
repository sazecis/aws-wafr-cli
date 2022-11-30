import argparse

import wafr.template as template
import wafr.workload as workload
import wafr.lens as lens
import config.config as conf

def main():
    parser = argparse.ArgumentParser(description='Well-architected framework review CLI tool is helping to handle automatically some well-architected tool functionalities. See subcommands for more details.')
    subparsers = parser.add_subparsers(help='Select one of the subcommands.')

    manage_template_parser = subparsers.add_parser(
        name='manage-template', 
        description='Commands to generate and save templates. Also used to list workload from which the template can be generated.')
    manage_template_parser.add_argument('-w', '--workloadid', help='An already available workload id from where the tool will get the questions and answers.', default='')
    manage_template_parser.add_argument('-o', '--outputfile', help='The location of the file where the generated template will be saved.', default='')
    manage_template_parser.add_argument('-s', '--saveworkload', action='store_true', help='By activating this option the content of the workload will be saved to the template. If not used the behaviour is that a new default template is generated', default='')
    manage_template_parser.add_argument('-l', '--listworkloads', action='store_true', help='List the available workload ids of the currently used account.', default='')
    manage_template_parser.add_argument('-c', '--customlens', help='Generate custom lens template from an already existing custom lens workload.', choices=[conf.EKS_LENS_ALIAS], default='')
    manage_template_parser.set_defaults(func=manage_template)

    create_workload_parser = subparsers.add_parser(
        name='create-workload', 
        description='Create workload can be used to generate new workload in the currently configured account with standard and custom templates. ' +
                    'The templates can be of different lens type, e.g. standard well-architected or custom eks lens.')
    create_workload_parser.add_argument('-t', '--templatefile', help='Template file path used to create a new workload from. Default templates in the templates folder.', metavar='TEMPLATE_FILE_PATH', required=True, default='templates/standard.yaml') 
    create_workload_parser.add_argument('-w', '--workloadname', help='Name of the new workload.', required=True) 
    create_workload_parser.add_argument('-d', '--description', help='Description of the new workload.', required=True)
    create_workload_parser.add_argument('-e', '--environment', help='Environment where the workload is running [prod, pre-prod].', choices=['prod', 'pre-prod'], required=True)
    create_workload_parser.add_argument('-a', '--accountids', help='The AWS account IDs where the workload is running.', nargs='*', default=[])
    create_workload_parser.add_argument('-r', '--regions', help='The regions where the workload is running. e.g. eu-central-1.', nargs='*', default=['eu-central-1'])
    create_workload_parser.add_argument('-o', '--reviewowner', help='The name of the reviewer who created this WAFR workload.', required=True)
    create_workload_parser.add_argument('-ds', '--disablestandard', action='store_true', help='Disable the questions from the standard lens. Usable when the workload is created with custom lens. Ineffectiv with standard lens.')
    create_workload_parser.add_argument('-ta', '--trustedadvisor', help='Enable or disable the Trusted Advisor integration [enable, disable]', choices=['enable','disable'])
    create_workload_parser.set_defaults(func=create_new_workload)

    update_workload_parser = subparsers.add_parser(
        name='update-workload',
        description='Update workload can be used to update existing workloads in the currently configured account with standard and custom templates. ' +
                    'The templates can be of different lens type, e.g. standard well-architected or custom eks lens.')
    update_workload_parser.add_argument('-t', '--templatefile', help='Template file path used to create a new workload from. Default templates in the templates folder.', metavar='TEMPLATE_FILE_PATH', required=True, default='templates/standard.yaml') 
    update_workload_parser.add_argument('-w', '--workloadname', help='Name of the updated workload.', required=True) 
    update_workload_parser.add_argument('-ds', '--disablestandard', action='store_true', help='Disable the questions from the standard lens. Usable when the workload is created with custom lens. Ineffectiv with standard lens.')
    update_workload_parser.set_defaults(func=update_workload)

    publish_lens_parser = subparsers.add_parser(
        name='publish-lens', 
        description='Publish a new custom lens version or creates a new one if does not exist.')
    publish_lens_parser.add_argument('-t', '--templatepath', help='Create a new custom lens version from template. Example templates are in the lenses folder.', metavar='LENS_FILE_PATH', required=True, default='')
    publish_lens_parser.add_argument('-v', '--lensversion', help='Publish a new version of your the lens.', required=True, default='')
    publish_lens_parser.set_defaults(func=publish_lens)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        
def manage_template(args):
    template.start_generation(
        workload_id=args.workloadid, 
        output_file=args.outputfile, 
        save_workload=args.saveworkload, 
        list_workloads=args.listworkloads, 
        custom_lens=args.customlens)

def create_new_workload(args):
    workload.create_new_workload(
        template_file_path=args.templatefile,
        workload_name=args.workloadname, 
        description=args.description, 
        environment=args.environment, 
        account_ids=args.accountids, 
        regions=args.regions, 
        review_owner=args.reviewowner,
        disable_standard= args.disablestandard,
        trusted_advisor=args.trustedadvisor)

def update_workload(args):
    workload.update_existing_workload(
        template_file_path=args.templatefile, 
        workload_name=args.workloadname,
        disable_standard= args.disablestandard)

def publish_lens(args):
    lens.publish_lens(
        lens_file_path=args.templatepath, 
        lens_version=args.lensversion)


if __name__ == "__main__":
    main()