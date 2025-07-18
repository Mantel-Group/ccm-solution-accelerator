# Collector Credentials - Azure EntraID

## Objective

Provision a client ID and secret in Azure Entra ID for service authentication against Microsoft Graph API to query Entra user accounts.  This will be used by the collector process to retrieve information about Azure EntraID user accounts.

## Prerequisites

- Azure portal access: https://portal.azure.com
- Role: Application Administrator or Global Administrator
- Target: Microsoft Entra ID tenant

## 1. Register the Application

1. Navigate to: **Microsoft Entra ID → App registrations → New registration**
2. Configure:
   - **Name**: `ContinuousControlMonitoringCollector` (or appropriate name)
   - **Supported account types**: *Single tenant* (default) or *Multitenant* as required
   - **Redirect URI**: Leave empty (not required for client credentials flow)
3. Click **Register**
4. Record the following from the Overview page:
   - **Application (client) ID** (this will become `AZURE_CLIENT_ID`)
   - **Directory (tenant) ID** (this will become `AZURE_TENANT_ID`)

## 2. Create a Client Secret

1. Go to **Certificates & secrets → New client secret**
2. Provide a description and expiration
3. Click **Add**
4. Copy and securely store the **Secret Value** (not recoverable later) (this will become `AZURE_CLIENT_SECRET`)

## 3. Assign API Permissions

1. Go to **API permissions → Add a permission**
2. Select **Microsoft Graph**
3. Choose **Application permissions**
4. Add the following permission:
   - `User.Read.All`
   - `AuditLog.Read.All`
   - `Directory.Read.All`
5. Click **Add permissions**
6. Click **Grant admin consent for \<Tenant\>**

## 4. Set the environment variables

Using the provided credentials, set the following environment variables.

* `AZURE_TENANT_ID`
* `AZURE_CLIENT_ID`
* `AZURE_CLIENT_SECRET`