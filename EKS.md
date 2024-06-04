AWS tickert in sadnbxo account:
https://support.console.aws.amazon.com/support/home?region=us-east-1#/case/?displayId=171715815300558&language=en

deploy the stack

change the authentication mode t:

<BS>EKS API and ConfigMap

iwe should be able to use this to set that, but it doesn't work with teh L2
construct

```python
        access_config = eks.CfnCluster.AccessConfigProperty(
            authentication_mode="API_AND_CONFIG_MAP",
            bootstrap_cluster_creator_admin_permissions=True,
        )
```


manually create IAm access entries for my user:
AmazonEKSAdminPolicy
AmazonEKSAdminViewPolicy
AmazonEKSClusterAdminPolicyA


```bash

aws_whoami 
 2016  aws eks --region us-east-1 update-kubeconfig --name EKSMockService4418E7E4-b876a39ce4b74f7c986328f12c053d32
 2017  kubectl 
 2018* kubectl versionA
 2019  aws eks --region us-east-1 update-kubeconfig --name EKSMockService4418E7E4-b876a39ce4b74f7c986328f12c053d32
 2020  kubectl get pods -A
 2021  kubectl get svc
 2022  kubectl exec -it mock-service-68885c88db-48mr9 -- /bin/bash
 2023  make static 
 2024  make pytest_update_golden 
 2025  make STACK=mock-service-eks cdk-deploy-single 
 2026  kubectl get pods -n kube-system
 2027  make static 
 2028  kubectl get deploy
 2029  kubectl describe deploy mock-service
 2030  vim ggg.yml
 2031  kubectl apply -f ggg.yml 
 2032  vim ggg.yml
 2033  kubectl apply -f ggg.yml 
 2034  kubectl get ingress
 2035    curl -X GET 'http://k8s-default-mockingr-36a1a0e310-494347807.us-east-1.elb.amazonaws.com/?wait=2000ms'
 2036   curl -X GET 'http://k8s-default-mockingr-36a1a0e310-494347807.us-east-1.elb.amazonaws.com/?wait=2000ms'
 2037  which curl
 2038  curl -X GET 'http://k8s-default-mockingr-36a1a0e310-494347807.us-east-1.elb.amazonaws.com/?wait=2000ms'
 2039  pkill zoom 
 2040  gaa
 2041  gca
 2042  vim EKS.md
```


## EKS CLI

```bash
export EKS_CLUSTER_NAME="$(aws eks list-clusters --output text | awk '{print $2}')"
aws eks describe-cluster --name  "${EKS_CLUSTER_NAME}"
aws eks update-kubeconfig --name  "${EKS_CLUSTER_NAME}"
export ADMIN_POLICY_ARN="$(aws iam list-policies --query 'Policies[?PolicyName==`AdministratorAccess`].{ARN:Arn}' --output text)"

```