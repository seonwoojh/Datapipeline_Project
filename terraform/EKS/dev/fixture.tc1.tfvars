aws_region      = "ap-northeast-2"
azs             = ["ap-northeast-2a", "ap-northeast-2b", "ap-northeast-2c"]
cidr       = "10.1.0.0/16"
enable_igw = true
enable_ngw = true
single_ngw = true
name            = "eks-autoscaling-tc1"
tags = {
  env  = "dev"
  test = "tc1"
}
kubernetes_version  = "1.21"
enable_ssm          = true
managed_node_groups = [
	{
    name          = "ElasticSearch-master"
    min_size      = 1
    max_size      = 3
    desired_size  = 1
    instance_type = "t3.medium"
  }, 
	{
    name          = "ElasticSearch-data"
    min_size      = 1
    max_size      = 3
    desired_size  = 1
    instance_type = "t3.medium"
  }, 
	{
    name          = "ElasticSearch-client"
    min_size      = 1
    max_size      = 3
    desired_size  = 1
    instance_type = "t3.medium"
  }, 
	{
    name          = "Kibana"
    min_size      = 1
    max_size      = 3
    desired_size  = 1
    instance_type = "t3.medium"
  }
]
node_groups = []
fargate_profiles = []