from __future__ import print_function, unicode_literals
from ..lib.handler.github_handler import GithubHandler
from ..lib.handler.slack_handler import SlackHandler
from ..lib.handler import prompt_utils
from ..lib.handler import aws_handler as aws
from ..lib.handler import drone_handler as drone
from ..lib.logger import Logger
from halo import Halo
import sys
import time

github = GithubHandler()
logger = Logger()
slack = SlackHandler()


def entrypoint(args):

    if args.project == "prima":
        sys.exit(-1)
    else:
        if aws.is_cloudfront_distribution(args.project):
            version = ask_version(drone.get_tag_from_builds(args.project))
            build = drone.get_build_from_tag(args.project, version)
            drone.launch_build(args.project, build)
            logger.error("Deploy con cloudfront")
            sys.exit(-1)
        else:
            repo = github.get_repo(args.project)
            stacks_name = aws.get_stacks_name(args.project)
            if len(stacks_name) > 0:
                version = ask_version(
                    aws.get_artifacts_version_from_s3(args.project))
                release = github.get_release_if_exists(repo, version)
                logger.info(
                    "\nDescrizione della release selezionata:\n{}\n".format(release.body))
                if not prompt_utils.ask_confirm("Vuoi continuare con il rollback?"):
                    sys.exit(-1)

                for stack_name in stacks_name:
                    aws.update_stack(stack_name, version)
                    if update_completed(stack_name):
                        # slack.post("#deploy", "ho effettuato il rollback di {} alla release {}".format())
                        logger.info(
                            "Rollback compleato con successo - {}".format(stack_name))
                    else:
                        logger.error(
                            "Errore durante il rollback. Controllare lo stato su Cloudformation o chiedere ai DevOps")
            else:
                logger.error(
                    "Nessuno stack trovato. Impossibile procedere con il rollback.")


def update_completed(stack_name):
    for i in range(0, 60):
        with Halo(text='Rollback in progress...', spinner='dots', color='magenta'):
            if get_stack_stauts(stack_name) == "UPDATE_COMPLETE":
                return True
            elif "FAILED" in stack_status:
                logger.error(
                    "Errore durante il rollback. Controllare lo stato su Cloudformation o chiedere ai DevOps")
            else:
                time.sleep(10)
    return False


def ask_version(choiches):
    return prompt_utils.ask_choices("Seleziona release: ", choiches)
