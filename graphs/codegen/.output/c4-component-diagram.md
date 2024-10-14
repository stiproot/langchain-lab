```mermaid
C4Component
title Component Diagram for Meeting Transcript to Azure DevOps Work Items

Container_Boundary(webAppBoundary, "Web Application") {
    Component(frontendUploader, "Uploader Component", "Vue.js", "Handles file uploads from users.")
    Component(frontendApproval, "Approval Component", "Vue.js", "Displays and manages approval of work item hierarchies.")
    
    Component(apiGatewayRouter, "Router Component", "Python, Dapr", "Routes requests to appropriate services.")
    
    Component(transcriptProcessor, "Transcript Processor", "Python, Dapr", "Processes transcripts to build work item hierarchies.")
    Component(hierarchyBuilder, "Hierarchy Builder", "Python, Dapr", "Constructs work item hierarchies from processed data.")
    
    Component(approvalManager, "Approval Manager", "Python, Dapr", "Handles approval logic for work item hierarchies.")
    Component(workItemCreator, "Work Item Creator", "Python, Dapr", "Creates work items in Azure DevOps upon approval.")
}

ContainerDb(database, "NoSQL Database", "Stores transcripts and work item data.")

System_Ext(azureDevOps, "Azure DevOps", "Stores the work items created from transcripts.")

Rel(user, frontendUploader, "Uploads transcripts")
Rel(user, frontendApproval, "Approves hierarchies")

Rel(frontendUploader, apiGatewayRouter, "Sends upload requests")
Rel(frontendApproval, apiGatewayRouter, "Sends approval requests")

Rel(apiGatewayRouter, transcriptProcessor, "Routes to")
Rel(apiGatewayRouter, approvalManager, "Routes to")

Rel(transcriptProcessor, hierarchyBuilder, "Processes and builds")
Rel(hierarchyBuilder, database, "Stores hierarchy data")

Rel(approvalManager, workItemCreator, "Upon approval, creates")
Rel(workItemCreator, azureDevOps, "Creates work items")

Rel(database, apiGatewayRouter, "Retrieves data")

UpdateElementStyle(frontendUploader, $fontColor="black", $bgColor="lightblue", $borderColor="black")
UpdateElementStyle(frontendApproval, $fontColor="black", $bgColor="lightblue", $borderColor="black")
UpdateElementStyle(apiGatewayRouter, $fontColor="black", $bgColor="lightblue", $borderColor="black")
UpdateElementStyle(transcriptProcessor, $fontColor="black", $bgColor="lightblue", $borderColor="black")
UpdateElementStyle(hierarchyBuilder, $fontColor="black", $bgColor="lightblue", $borderColor="black")
UpdateElementStyle(approvalManager, $fontColor="black", $bgColor="lightblue", $borderColor="black")
UpdateElementStyle(workItemCreator, $fontColor="black", $bgColor="lightblue", $borderColor="black")
UpdateElementStyle(database, $fontColor="black", $bgColor="lightyellow", $borderColor="black")
UpdateElementStyle(azureDevOps, $fontColor="black", $bgColor="lightgreen", $borderColor="black")
```