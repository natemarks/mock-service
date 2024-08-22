
# Deploy the lambda on a VPC with an RDS postgres instance

This IaC deploys the latest lambda artifact in the imprivata sandbox account. It's hard coded in  deployments/cdk/app.py to use a bucket in that account:
```python
ARTIFACT_BUCKET = "com.imprivata.709310380790.us-east-1.devops-artifacts"
```

Set credentials for the sandbox account and run these make commands to deploy and destroy the test environmemnt

```bash
make deploy
make destroy
```

NOTE: CDK requires nodejs. It's installed from npm


## EKS cluster

need IAM privileges for EKS and k8s RBAC privilieges

https://docs.aws.amazon.com/eks/latest/userguide/security_iam_id-based-policy-examples.html

```text
aws eks update-kubeconfig --region us-east-1 --name mock-service

aws sts assume-role \
--role-arn arn:aws:sts::709310380790:assumed-role/mock-service-eks-L2ClusterCreationRoleFCDE87E9-bikE392CN0x2/AWSCDK.EKSCluster.Create.bddc4380-2478-4aac-82b4-0c5d0744c4b7 \
--role-session-name eks-mock-service

kubectl get nodes
```