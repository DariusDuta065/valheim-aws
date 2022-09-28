packer {
  required_plugins {
    amazon = {
      version = ">= 0.0.2"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

source "amazon-ebs" "ubuntu" {
  ami_name      = "valheim-ami"
  instance_type = "t3a.medium"
  region        = "eu-west-2"
  ssh_username  = "ubuntu"

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-focal-20.04-amd64-server-*" // Ubuntu 20.04 LTS
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"] // AWS-owned AMIs
  }

  tags = {
    project = "valheim"
  }
}

build {
  name = "learn-packer"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]

  provisioner "shell" {
    environment_vars = [
      "SLEEP_TIME=30",
    ]
    inline = [
      "sleep $SLEEP_TIME",

      // apt packages
      "sudo apt-get update -y",
      "sudo apt-get install -y python3-pip python-setuptools awscli",

      // cfn-init scripts
      "sudo pip3 install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-py3-latest.tar.gz",
      "sudo mkdir -p /opt/aws/bin/",
      "sudo ln /usr/local/bin/cfn-init /opt/aws/bin/cfn-init",
      "sudo ln /usr/local/bin/cfn-signal /opt/aws/bin/cfn-signal",

      // LinuxGSM Valheim game server setup
      "wget -O linuxgsm.sh https://linuxgsm.sh",
      "chmod +x linuxgsm.sh",
      "bash linuxgsm.sh vhserver",
      "./vhserver auto-install"
    ]
  }
}
