# Configuring DVC 

## What about this step?
in this step it is outlined how Data version Control (DVC) is configure within your ML project.

## Commands

### Create a python enviroment
Create a Python environment for your ML project development. Include desired Python packages in a requirements file. Run the following script with the input parameter being the name of the environment.
```bash
./scripts/pdia_create_venv.sh <enviroment_name>
```
### Configure DVC remote storage
After Python environment setup, the subsequent step entails configuring remote storage for saving versioned dataset artifacts. In this setup, we utilize an SSH/SFTP client for data management, indicating that the remote storage resides on an SSH server. If another remote storage option wants to be used, adjust line 15 of "pdia_create_venv.sh" to include the desired option. DVC supports various storage options such as [s3], [gdrive], [gs], [azure], [ssh], [hdfs], [webdav], and [oss].

### Create private key to secure SSH connection authentication