#!/usr/bin/env python

""" Create/remove slurm nodes.

    Runs on ansible/tf control host as user "centos"
    Driven by suspend.sh/resume.sh run by SlurmUser on slurm control host (ohpc-login)
"""

from __future__ import print_function
import sys, subprocess, os, re

VENV = os.path.expanduser('~/.venv/bin/activate')
TF_CMD = os.path.expanduser('~/terraform')
TF_DIR = os.path.expanduser('~/eiffel-ohpc/terraform_ohpc')
ANSIBLE_CMD = 'ansible-playbook'
ANSIBLE_DIR = os.path.expanduser('~/eiffel-ohpc/')

def shell_source(script):
    """ Emulate the action of "source" in bash, setting environment vars.
    
        From https://stackoverflow.com/a/12708396/916373
    """
    pipe = subprocess.Popen(". %s; env" % script, stdout=subprocess.PIPE, shell=True)
    output = pipe.communicate()[0]
    env = dict((line.split("=", 1) for line in output.splitlines()))
    os.environ.update(env)

def main():

    mode=sys.argv[1]
    compute_changes=sys.argv[2:]
    print('inputs:', mode, compute_changes)

    # load environment
    shell_source(os.path.expanduser(VENV))
    
    # get existing compute instances as a list:
    tf_state = "{TF_CMD} state list openstack_compute_instance_v2.compute".format(TF_CMD=TF_CMD)
    output = subprocess.Popen(tf_state, stdout=subprocess.PIPE, shell=True, cwd=TF_DIR).communicate()[0]
    existing_compute = re.findall("ohpc-compute-[0-9]+", output)
    print('existing compute:', existing_compute)
    
    # create target instance string:
    # NB using sets is safer than string operations as avoids e.b. adding existing node
    if mode == 'resume':
        target_compute = sorted(set(existing_compute) | set(compute_changes))
    elif mode == 'suspend':
        target_compute = sorted(set(existing_compute) - set(compute_changes))
    else:
        exit('Invalid mode argument {mode}'.format(mode))
    target_compute = ' '.join(target_compute)
    print('target_compute ({mode}):'.format(mode=mode), target_compute)
    
    # run terraform to change instances:
    tf_apply = '{TF_CMD} apply -var nodenames="{target_compute}" -refresh=true -auto-approve'.format(TF_CMD=TF_CMD, target_compute=target_compute)
    rc = subprocess.call(tf_apply, shell=True, cwd=TF_DIR)
    if rc:
        exit('ERROR: return code of {rc} from {tf_apply}'.format(rc=rc, tf_apply=tf_apply))
    
    # for resume only, run ansible to configure instances:
    if mode == 'resume':
        ansible_main = '{ANSIBLE_CMD} main.yml -i terraform_ohpc/ohpc_hosts'.format(ANSIBLE_CMD=ANSIBLE_CMD)
        rc = subprocess.call(ansible_main, shell=True, cwd=ANSIBLE_DIR)
        if rc:
            exit('ERROR: return code of {rc} from {ansible_main}'.format(rc=rc, ansible_main=ansible_main))
    
    # on suspend:
    # - does the ohpc_hosts file need to be regenerated? YES
    # does /etc/hosts need rewriting to avoid slurm thinking nodes can't be contacted??
    # now rewrite hosts file (TODO- need to fix this!)
  # #$TERRAFORM apply -var nodenames="$target_compute" -refresh=true -auto-approve
         
if __name__ == '__main__':
    main()
    