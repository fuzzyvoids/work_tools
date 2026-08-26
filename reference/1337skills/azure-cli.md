# Azure CLI intermediate

Comprehensive Azure CLI commands and workflows for managing Microsoft Azure cloud services, including virtual machines, storage, and Azure Active Directory.

## Installation & Authentication

| Command | Description |
| --- | --- |
| `az login` | Login to Azure |
| `az login --service-principal -u <app-id> -p <password> --tenant <tenant>` | Login with service principal |
| `az logout` | Logout from Azure |
| `az account list` | List all subscriptions |
| `az account set --subscription "subscription-name"` | Set active subscription |
| `az account show` | Show current subscription |
| `az configure` | Configure Azure CLI settings |

## Resource Groups

| Command | Description |
| --- | --- |
| `az group list` | List all resource groups |
| `az group create --name myResourceGroup --location eastus` | Create resource group |
| `az group delete --name myResourceGroup` | Delete resource group |
| `az group show --name myResourceGroup` | Show resource group details |
| `az group update --name myResourceGroup --tags environment=production` | Update resource group tags |

## Virtual Machines

### VM Management

| Command | Description |
| --- | --- |
| `az vm list` | List all VMs |
| `az vm create --resource-group myResourceGroup --name myVM --image UbuntuLTS --admin-username azureuser --generate-ssh-keys` | Create VM |
| `az vm start --resource-group myResourceGroup --name myVM` | Start VM |
| `az vm stop --resource-group myResourceGroup --name myVM` | Stop VM |
| `az vm restart --resource-group myResourceGroup --name myVM` | Restart VM |
| `az vm delete --resource-group myResourceGroup --name myVM` | Delete VM |
| `az vm deallocate --resource-group myResourceGroup --name myVM` | Deallocate VM |

### VM Information

| Command | Description |
| --- | --- |
| `az vm show --resource-group myResourceGroup --name myVM` | Show VM details |
| `az vm list-sizes --location eastus` | List available VM sizes |
| `az vm image list --output table` | List popular VM images |
| `az vm image list --publisher Canonical --output table` | List images by publisher |
| `az vm get-instance-view --resource-group myResourceGroup --name myVM` | Get VM instance view |

### VM Extensions

| Command | Description |
| --- | --- |
| `az vm extension list --resource-group myResourceGroup --vm-name myVM` | List VM extensions |
| `az vm extension set --resource-group myResourceGroup --vm-name myVM --name customScript --publisher Microsoft.Azure.Extensions --settings '\\{"fileUris":["https://example.com/script.sh"],"commandToExecute":"sh script.sh"\\}'` | Install extension |
| `az vm extension delete --resource-group myResourceGroup --vm-name myVM --name customScript` | Remove extension |

## Storage

### Storage Accounts

| Command | Description |
| --- | --- |
| `az storage account list` | List storage accounts |
| `az storage account create --name mystorageaccount --resource-group myResourceGroup --location eastus --sku Standard_LRS` | Create storage account |
| `az storage account delete --name mystorageaccount --resource-group myResourceGroup` | Delete storage account |
| `az storage account show --name mystorageaccount --resource-group myResourceGroup` | Show storage account details |
| `az storage account keys list --account-name mystorageaccount --resource-group myResourceGroup` | List storage account keys |

### Blob Storage

| Command | Description |
| --- | --- |
| `az storage container list --account-name mystorageaccount` | List containers |
| `az storage container create --name mycontainer --account-name mystorageaccount` | Create container |
| `az storage container delete --name mycontainer --account-name mystorageaccount` | Delete container |
| `az storage blob upload --file myfile.txt --container-name mycontainer --name myblob --account-name mystorageaccount` | Upload blob |
| `az storage blob download --container-name mycontainer --name myblob --file myfile.txt --account-name mystorageaccount` | Download blob |
| `az storage blob list --container-name mycontainer --account-name mystorageaccount` | List blobs |

### File Shares

| Command | Description |
| --- | --- |
| `az storage share list --account-name mystorageaccount` | List file shares |
| `az storage share create --name myshare --account-name mystorageaccount` | Create file share |
| `az storage file upload --share-name myshare --source myfile.txt --account-name mystorageaccount` | Upload file |
| `az storage file download --share-name myshare --path myfile.txt --dest myfile.txt --account-name mystorageaccount` | Download file |

## App Service

### Web Apps

| Command | Description |
| --- | --- |
| `az webapp list` | List web apps |
| `az webapp create -resource-group myResourceGroup -plan myAppServicePlan -name myWebApp -runtime "NODE | 14-lts"` |
| `az webapp delete --resource-group myResourceGroup --name myWebApp` | Delete web app |
| `az webapp start --resource-group myResourceGroup --name myWebApp` | Start web app |
| `az webapp stop --resource-group myResourceGroup --name myWebApp` | Stop web app |
| `az webapp restart --resource-group myResourceGroup --name myWebApp` | Restart web app |

### App Service Plans

| Command | Description |
| --- | --- |
| `az appservice plan list` | List app service plans |
| `az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku B1` | Create app service plan |
| `az appservice plan delete --name myAppServicePlan --resource-group myResourceGroup` | Delete app service plan |
| `az appservice plan update --name myAppServicePlan --resource-group myResourceGroup --sku S1` | Update app service plan |

### Deployment

| Command | Description |
| --- | --- |
| `az webapp deployment source config --resource-group myResourceGroup --name myWebApp --repo-url https://github.com/user/repo --branch master` | Configure Git deployment |
| `az webapp deployment source sync --resource-group myResourceGroup --name myWebApp` | Sync deployment |
| `az webapp log tail --resource-group myResourceGroup --name myWebApp` | Stream logs |
| `az webapp config appsettings set --resource-group myResourceGroup --name myWebApp --settings key=value` | Set app settings |

## Azure Functions

### Function Apps

| Command | Description |
| --- | --- |
| `az functionapp list` | List function apps |
| `az functionapp create --resource-group myResourceGroup --consumption-plan-location eastus --runtime node --name myFunctionApp --storage-account mystorageaccount` | Create function app |
| `az functionapp delete --resource-group myResourceGroup --name myFunctionApp` | Delete function app |
| `az functionapp start --resource-group myResourceGroup --name myFunctionApp` | Start function app |
| `az functionapp stop --resource-group myResourceGroup --name myFunctionApp` | Stop function app |

### Function Management

| Command | Description |
| --- | --- |
| `az functionapp function list --resource-group myResourceGroup --name myFunctionApp` | List functions |
| `az functionapp function show --resource-group myResourceGroup --name myFunctionApp --function-name myFunction` | Show function details |
| `az functionapp function delete --resource-group myResourceGroup --name myFunctionApp --function-name myFunction` | Delete function |

## Azure SQL Database

### SQL Servers

| Command | Description |
| --- | --- |
| `az sql server list` | List SQL servers |
| `az sql server create --name myserver --resource-group myResourceGroup --location eastus --admin-user myadmin --admin-password myPassword123!` | Create SQL server |
| `az sql server delete --name myserver --resource-group myResourceGroup` | Delete SQL server |
| `az sql server show --name myserver --resource-group myResourceGroup` | Show SQL server details |

### SQL Databases

| Command | Description |
| --- | --- |
| `az sql db list --resource-group myResourceGroup --server myserver` | List databases |
| `az sql db create --resource-group myResourceGroup --server myserver --name mydatabase --service-objective S0` | Create database |
| `az sql db delete --resource-group myResourceGroup --server myserver --name mydatabase` | Delete database |
| `az sql db show --resource-group myResourceGroup --server myserver --name mydatabase` | Show database details |

### Firewall Rules

| Command | Description |
| --- | --- |
| `az sql server firewall-rule list --resource-group myResourceGroup --server myserver` | List firewall rules |
| `az sql server firewall-rule create --resource-group myResourceGroup --server myserver --name AllowMyIP --start-ip-address 192.168.1.1 --end-ip-address 192.168.1.1` | Create firewall rule |
| `az sql server firewall-rule delete --resource-group myResourceGroup --server myserver --name AllowMyIP` | Delete firewall rule |

## Azure Active Directory

### Users

| Command | Description |
| --- | --- |
| `az ad user list` | List users |
| `az ad user create --display-name "John Doe" --password myPassword123! --user-principal-name john@contoso.com` | Create user |
| `az ad user delete --id john@contoso.com` | Delete user |
| `az ad user show --id john@contoso.com` | Show user details |
| `az ad user update --id john@contoso.com --display-name "John Smith"` | Update user |

### Groups

| Command | Description |
| --- | --- |
| `az ad group list` | List groups |
| `az ad group create --display-name "My Group" --mail-nickname mygroup` | Create group |
| `az ad group delete --group mygroup` | Delete group |
| `az ad group member add --group mygroup --member-id john@contoso.com` | Add member to group |
| `az ad group member remove --group mygroup --member-id john@contoso.com` | Remove member from group |

### Applications

| Command | Description |
| --- | --- |
| `az ad app list` | List applications |
| `az ad app create --display-name "My App"` | Create application |
| `az ad app delete --id <app-id>` | Delete application |
| `az ad app show --id <app-id>` | Show application details |

## Azure Kubernetes Service (AKS)

### Cluster Management

| Command | Description |
| --- | --- |
| `az aks list` | List AKS clusters |
| `az aks create --resource-group myResourceGroup --name myAKSCluster --node-count 1 --enable-addons monitoring --generate-ssh-keys` | Create AKS cluster |
| `az aks delete --resource-group myResourceGroup --name myAKSCluster` | Delete AKS cluster |
| `az aks start --resource-group myResourceGroup --name myAKSCluster` | Start AKS cluster |
| `az aks stop --resource-group myResourceGroup --name myAKSCluster` | Stop AKS cluster |

### Cluster Operations

| Command | Description |
| --- | --- |
| `az aks get-credentials --resource-group myResourceGroup --name myAKSCluster` | Get cluster credentials |
| `az aks scale --resource-group myResourceGroup --name myAKSCluster --node-count 3` | Scale cluster |
| `az aks upgrade --resource-group myResourceGroup --name myAKSCluster --kubernetes-version 1.21.1` | Upgrade cluster |
| `az aks show --resource-group myResourceGroup --name myAKSCluster` | Show cluster details |

## Azure Container Registry (ACR)

### Registry Management

| Command | Description |
| --- | --- |
| `az acr list` | List container registries |
| `az acr create --resource-group myResourceGroup --name myregistry --sku Basic` | Create container registry |
| `az acr delete --resource-group myResourceGroup --name myregistry` | Delete container registry |
| `az acr login --name myregistry` | Login to registry |

### Image Management

| Command | Description |
| --- | --- |
| `az acr repository list --name myregistry` | List repositories |
| `az acr repository show-tags --name myregistry --repository myapp` | Show image tags |
| `az acr repository delete --name myregistry --repository myapp --tag v1.0` | Delete image tag |
| `docker tag myapp:latest myregistry.azurecr.io/myapp:v1.0` | Tag image for ACR |
| `docker push myregistry.azurecr.io/myapp:v1.0` | Push image to ACR |

## Networking

### Virtual Networks

| Command | Description |
| --- | --- |
| `az network vnet list` | List virtual networks |
| `az network vnet create --resource-group myResourceGroup --name myVNet --address-prefix 10.0.0.0/16` | Create virtual network |
| `az network vnet delete --resource-group myResourceGroup --name myVNet` | Delete virtual network |
| `az network vnet subnet create --resource-group myResourceGroup --vnet-name myVNet --name mySubnet --address-prefix 10.0.1.0/24` | Create subnet |

### Network Security Groups

| Command | Description |
| --- | --- |
| `az network nsg list` | List network security groups |
| `az network nsg create --resource-group myResourceGroup --name myNSG` | Create NSG |
| `az network nsg rule create --resource-group myResourceGroup --nsg-name myNSG --name myRule --protocol tcp --priority 1000 --destination-port-range 80` | Create NSG rule |
| `az network nsg rule delete --resource-group myResourceGroup --nsg-name myNSG --name myRule` | Delete NSG rule |

### Load Balancers

| Command | Description |
| --- | --- |
| `az network lb list` | List load balancers |
| `az network lb create --resource-group myResourceGroup --name myLoadBalancer --sku Standard --public-ip-address myPublicIP` | Create load balancer |
| `az network lb delete --resource-group myResourceGroup --name myLoadBalancer` | Delete load balancer |

## Monitoring and Logging

### Azure Monitor

| Command | Description |
| --- | --- |
| `az monitor metrics list --resource <resource-id>` | List metrics |
| `az monitor metrics list-definitions --resource <resource-id>` | List metric definitions |
| `az monitor log-analytics workspace list` | List Log Analytics workspaces |
| `az monitor log-analytics workspace create --resource-group myResourceGroup --workspace-name myWorkspace` | Create workspace |

### Alerts

| Command | Description |
| --- | --- |
| `az monitor alert list` | List alerts |
| `az monitor alert create --name myAlert --resource-group myResourceGroup --condition "avg Percentage CPU > 80"` | Create alert |
| `az monitor alert delete --name myAlert --resource-group myResourceGroup` | Delete alert |

## Best Practices

### Security

1. **Use Service Principals**: Use service principals for automated deployments

1. **RBAC**: Implement role-based access control

1. **Key Vault**: Store secrets in Azure Key Vault

1. **Network Security**: Use NSGs and firewalls to secure resources

### Cost Management

1. **Resource Tagging**: Tag resources for cost tracking

1. **Auto-shutdown**: Configure auto-shutdown for development VMs

1. **Reserved Instances**: Use reserved instances for predictable workloads

1. **Cost Alerts**: Set up cost alerts and budgets

### Automation

1. **ARM Templates**: Use Azure Resource Manager templates

1. **Azure DevOps**: Integrate with Azure DevOps for CI/CD

1. **PowerShell**: Use Azure PowerShell for Windows environments

1. **Terraform**: Use Terraform for multi-cloud deployments

Source: https://1337skills.com/cheatsheets/azure-cli/
