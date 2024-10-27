AWS tickert in sadnbxo account:
https://support.console.aws.amazon.com/support/home?region=us-east-1#/case/?displayId=171715815300558&language=en

deploy the stack


kubectl access fails:
```bash

aws eks --region us-east-1 update-kubeconfig --name mock-service
Updated context arn:aws:eks:us-east-1:709310380790:cluster/mock-service in /home/nmarks/.kube/config


kubectl get pods -A
E0925 09:59:13.361059  655204 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
E0925 09:59:13.954295  655204 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
E0925 09:59:14.522212  655204 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
E0925 09:59:15.094677  655204 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
E0925 09:59:15.652729  655204 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
error: You must be logged in to the server (the server has asked for the client to provide credentials)

```
In the AWS Console:
in the cluster -> Access -> IAM Access Entries create an entry for the assumed role arn for SSO (arn:aws:iam::709310380790:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AdministratorAccess_30daf8503494f58e) and give it AmazonEKSClusterAdminPolicy (arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy)

Figure out how to do apply the same change using the CLI. This doesnt' work:
```bash

aws eks create-access-entry \
--cluster-name mock-service \
--principal-arn arn:aws:iam::709310380790:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AdministratorAccess_30daf8503494f58e

    
aws eks associate-access-policy \
--cluster-name mock-service \
--principal-arn arn:aws:iam::709310380790:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AdministratorAccess_30daf8503494f58e \
--policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
--access-scope type=cluster

```

now kubectl works:
```bash

aws eks --region us-east-1 update-kubeconfig --name mock-service
Updated context arn:aws:eks:us-east-1:709310380790:cluster/mock-service in /home/nmarks/.kube/config
 nmarks  ~  projects  mock-service   eks ✚ 1  kubectl get pods -A
NAMESPACE     NAME                                            READY   STATUS    RESTARTS   AGE
default       mock-service-5d89fb769f-6n8z5                   1/1     Running   0          3m26s
default       mock-service-5d89fb769f-pgb9p                   1/1     Running   0          3m26s
kube-system   aws-load-balancer-controller-5bb6c9458d-6qjlm   1/1     Running   0          3m15s
kube-system   aws-load-balancer-controller-5bb6c9458d-92scf   1/1     Running   0          3m15s
kube-system   aws-node-hbjgr                                  2/2     Running   0          7m22s
kube-system   aws-node-z2sxz                                  2/2     Running   0          7m22s
kube-system   coredns-586b798467-jmc9z                        1/1     Running   0          10m
kube-system   coredns-586b798467-x84v7                        1/1     Running   0          10m
kube-system   kube-proxy-kx4m7                                1/1     Running   0          7m22s
kube-system   kube-proxy-wnqr2                                1/1     Running   0          7m22s

```
