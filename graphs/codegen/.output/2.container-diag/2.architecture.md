```mermaid
C4Container
  title Container Diagram for Meeting Transcript to Azure DevOps Work Items

  System_Boundary(webAppBoundary, "Web Application Boundary") {
    Container(webApp, "Web Application", "Vue.js", "Allows users to upload meeting transcripts and view work item hierarchy")
    Container(apiGateway, "API Gateway", "Python, FastAPI", "Handles requests and routes them to appropriate services")
  }

  System_Boundary(backendBoundary, "Backend Services") {
    Container(transcriptService, "Transcript Service", "Python", "Processes meeting transcripts and builds work item hierarchy")
    Container(approvalService, "Approval Service", "Python", "Manages approval of work item hierarchy")
    Container(azureDevOpsService, "Azure DevOps Service", "Python", "Creates work items in Azure DevOps")
  }

  System_Boundary(databaseBoundary, "Database Boundary") {
    ContainerDb(noSqlDb, "NoSQL Database", "MongoDB", "Stores transcripts and work item data")
  }

  System_Boundary(messagingBoundary, "Messaging Boundary") {
    Container(dapr, "Dapr", "Dapr Sidecar", "Facilitates communication between microservices")
  }

  Rel(webApp, apiGateway, "Uploads transcripts and requests hierarchy")
  Rel(apiGateway, transcriptService, "Processes transcript")
  Rel(transcriptService, approvalService, "Sends hierarchy for approval")
  Rel(approvalService, azureDevOpsService, "Approves and sends to Azure DevOps")
  Rel(azureDevOpsService, noSqlDb, "Stores work item data")
  Rel(apiGateway, dapr, "Uses Dapr for service communication")
```

### Explanation

- **Web Application**: Built with Vue.js, this component allows users to upload meeting transcripts and view the generated work item hierarchy.
- **API Gateway**: Developed using Python and FastAPI, it routes incoming requests to the appropriate backend services.
- **Transcript Service**: Processes the uploaded meeting transcripts and constructs a hierarchy of work items.
- **Approval Service**: Manages the approval process for the generated work item hierarchy.
- **Azure DevOps Service**: Responsible for creating work items in Azure DevOps once the hierarchy is approved.
- **NoSQL Database**: Utilizes MongoDB to store transcripts and work item data.
- **Dapr**: Used as a sidecar to facilitate communication between microservices, ensuring scalability and resilience.