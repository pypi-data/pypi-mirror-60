#!/usr/bin/env python3

from aws_cdk import core
from aws_cdk.cx_api import CloudAssembly

from services.bookings.cdk_bookings_stack import CDKBookingsStack
import os

from zinc_cli.infrastructure.services.static_site.cdk_static_site_stack import CDKStaticSiteStack


def build(project_name: str, site_domain: str, aws_account: str, aws_region: str) -> CloudAssembly:

    # This is the build definition.
    app = core.App()
    project_id = "my_new_project"

    # Use environment vars to load configuration.
    if "PROJECT_NAME" in os.environ:
        project_id = os.environ["PROJECT_NAME"]
        print(f"Project Name Override: {project_id}")

    # Create the stacks.
    # CDKBookingsStack(app, f"ZincBookings-{project_id}", project_id)

    # Static site: Region must be us-east-1 for Route53 and CDN.
    env = {"account": aws_account, "region": "us-east-1"}
    static_stack_id = f"ZStaticSite-{project_name}"
    CDKStaticSiteStack(app, static_stack_id, project_name, domain_name=site_domain, env=env)

    # Synthesize the application.
    result = app.synth()
    return result


def no_op_deploy():
    print("Deploying CDK Stack")


if __name__ == "__main__":
    no_op_deploy()
