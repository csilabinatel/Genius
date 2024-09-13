# Initial configuration

## What about this step?

Begin by configuring the initial settings for your project. This involves untracking certain folders from raw Git repository, renaming files to align with project acronyms, and establishing Git tracking for the updated files in your new repository.

## Commands

### Clone the Repository
Clone the repository and designate a parent folder name incorporating project acronym alongside a distinctive identifier. For instance, for a project with the acronym "RPI" the parent folder should be named "rpi_machine_learning".
```bash
git clone https://jira.inatel.br/bitbucket/scm/pdia/pdia_project_structure.git <project_name>
```
### Update to your new repository
Run the command by setting appropiated input parameter for project acronim and repository url
```bash
cd <project_name>
./scripts/pdia_initial_config.sh <project_acronim> <repository_url>
```