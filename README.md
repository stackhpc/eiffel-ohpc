# eiffel-ohpc

Example OpenHPC cluster built on:
https://github.com/stackhpc/ansible-role-openhpc

## Install

You may find this useful to run the above ansible-playbook command:

    virtualenv .venv
    . .venv/bin/activate
    pip install -U pip
    pip install -U -r requirements.txt
    ansible-galaxy install -r requirements.yml

## Create Infrastructure

Download the latest and unzip it:
https://www.terraform.io/downloads.html

For example:

    cd terraform_ohpc
    export terraform_version="0.12.12"
    wget https://releases.hashicorp.com/terraform/${terraform_version}/terraform_${terraform_version}_linux_amd64.zip
    unzip terraform_${terraform_version}_linux_amd64.zip

Now you can get Terraform to create the infrastructure:

    cd terraform_ohpc
    ./terraform init
    ./terraform plan
    ./terraform apply

## Install OpenHPC Slurm with Ansible

You can create a cluster by doing:

    ansible-playbook create.yml -i terraform_ohpc/ohpc_hosts

## OpenOnDemand Config

To setup a password for centos, try this on the login node:

    sudo htpasswd -c /opt/rh/httpd24/root/etc/httpd/.htpasswd centos
