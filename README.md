# Introduction 
    As we need to develop a pipeline to maintain ignition gateway, this repository contains updated projects and tags required to download a sanitized ignition gateway backup. 

    Purpose is to allow multi-developer environment and maintain visibility of what's change while provide quality control on the ignition code itself.

    Ultimately, these structures allow for CICD software lifecycle management.

# Getting Started
    1.	Installation process
    These packages assume one dedicated environment setup to have ignition services setup and running. To install ignition, please follow this url: https://www.docs.inductiveautomation.com/docs/8.1/getting-started/installing-and-upgrading

    For which ignition version, please refer #2. 

    Git Server must be installed.

    2.	Software dependencies
        Ignition Version: 8.1.45

        Following ignition modules are used:
        - Allen-Bradley Driver	6.1.45 (b2025010709)
        - Logix Driver	5.1.45 (b2025010709)
        - OPC-UA	9.1.45 (b2025010709)
        - Perspective	2.1.45 (b2025010709)
        - Reporting	6.1.45 (b2025010709)
        - SQL Bridge	10.1.45 (b2025010709)
        - Symbol Factory	7.1.45 (b2025010709)
        - Tag Historian	4.1.45 (b2025010709)
        - UDP and TCP Drivers	6.1.45 (b2025010709)
        - Vision	11.1.45 (b2025010709)
        - Web Browser	5.1.45 (b2025010709)
        - WebDev	5.1.45 (b2025010709)

        Git Version: 2.48.1
    3.	Latest releases
    4.	API references

# Build and Test
    Goal is to build a gateway.gwbk for field service engineer to restore.
    To achieve that goal, we need to build Jenkin pipelines to properly get sanitized gateway backups.

    Step 1: Check Ignition 8.1.45 with modules listed in #2 are installed and running in user-specified environment.

    Step 2: Restore base_gateway.gwbk to get initial gateway config.
    .\.gateway_backups\base_gateway.gwbk should be used for base install. This base install contains latest config to be used.

    Step 3: Run this .\build\moveFilesFrom_Repo_To_IgnDir.bat script. This script is required to update ignition project that contains UI components and ignition backend codes. This script will follow these steps:
        Step 3a: Pull latest files from remote-repository.

        Step 3b: Delete projects folder on where ignition is installed. Typically: "C:\Program Files\Inductive Automation\Ignition\data\projects"

        Step 3c: Robocopy project files from local-repository to projects folder on where the ignition is installed. Typically: "C:\Program Files\Inductive Automation\Ignition\data\projects"

    Step 4: 
    Run HTTPPost command to have ignition to get its tagProvider updated to reflect with data in tags folder.
    HTTPPost command parameters are found in this document .\build\HTTPRest_TagUpdate.txt.