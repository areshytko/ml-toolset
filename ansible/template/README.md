# Template experiment

Copy contents of this folder and use as a template for your experiment.

## Runbook

### Initialize

#### Setup AWS

- Setup AWS API credentials:

```
echo "export AWS_ACCESS_KEY_ID=<your key id>" >> ~/.bashrc
echo "export AWS_SECRET_ACCESS_KEY=<your secret key>" >> ~/.bashrc
source ~/.bashrc
```

- Setup SSH keys and get default VPC ID:

    - upload your default ssh public key `~/.ssh/id_rsa.pub` to AWS console
    - fill `ec2_cluster.aws_ssh_key` and `ec2_cluster.vpc_id` fields in `ansigle/config/vars.yml`

- Check your region in `ansible/config/vars.yml` and `ansible/config/aws_ec2.yml` files

#### Setup local environment

Run inside this folder:

```
source ./activate
```

#### Setup MLLab

```
export PYTHONPATH=<path to mllab package>:$PYTHONPATH
```

### Setup cluster

Run inside this folder:

```
ansible-playbook ansible/plays/setup-play.yml
```

### Submit train job

Run inside this folder:

```
../../bin/submit -- ddp_train_example.py
```

### Clean up cluster

Run inside this folder:

```
ansible-playbook ansible/plays/cleanup-play.yml
```
