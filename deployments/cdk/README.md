
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
