# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

Given the resources we need for the migartion of the application to azure we can estimate costs. In my estimation, I assume the total requests for the azure function will be lower than 1 million resulting in no costs for the resource. The application as it is will not consume any meaningful data of the storage account. Therefore I assume that the data on the stoarge account will stay low enough so no costs will occur. I assume that the azure service bus will not process more than 10.000 messages a month, that results in 0.0005 USD per month which are neglectable. I assume that the resources needed for the webapp will stay low enough to fit into the free tier resulting in no costs. The postgres database will result in 25.32 USD costs each month.

| Azure Resource | Service Tier | Cost | Monthly Cost |
| ------------ | ------------ | ------------ |
| *Azure Postgres Database* | Basic, 1 vCore(s), 5 GB | 25.32 USD / Month                                  | 25.32 USD |
| *Azure Service Bus*       | Basic                   | 0.05 USD / 1 Million Messages                      | 0.0005 USD |
| *Azure Web App*           | F1: Free                | 0 USD / Month                                      | 0 USD |
| *Azure Storage Account*   | StorageV2 Standard/Hot  | 0.021 USD / GB                                     | 0 USD |
| *Azure Azure Function*    | Consumption Plan        | 0.20 USD / 1 Million requests (first Million free) | 0 USD |

## Architecture Explanation
This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.

For the given web application it is the best solution to use a Azure Web App as migration. The application is a python flask app, that means it is supported by Azure Web App and there is no need for further control of the underlying system.
It is very easy to setup a Azure Web App for the given flask app, the infrastructure will be manged for us and it is the cheaper option. The main versability of a dedicated VM is not needed and also the estimate resources of the Azure Web App will be enough for the given web application. Considering all this Azure Web App is the way to go.
Looking into the application it self, one time consuming task can be identified that is executed directly on a user request. This can lead to slow responses and an unresponsive web site for users. So it is best to use an Azure Function to execute this task in the background will responding faster. The function that is time consuming is the iteration over every attendee to send mails. This iteration is therefore moved to an Azure Function.
