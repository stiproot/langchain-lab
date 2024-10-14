```mermaid
C4Context
  title System Context diagram for Meeting Transcript to Azure DevOps Work Items

  Enterprise_Boundary(b0, "System Boundary") {
    Person(user, "User", "A user who uploads meeting transcripts and approves work item hierarchies.")

    System(webApp, "Web Application", "Processes transcripts and creates work item hierarchies.")

    System_Ext(azureDevOps, "Azure DevOps", "Stores the work items created from transcripts.")

    SystemDb_Ext(noSqlDb, "NoSQL Database", "Stores transcripts and work item data.")
  }

  BiRel(user, webApp, "Uploads transcripts and approves hierarchies")
  Rel(webApp, azureDevOps, "Creates work items")
  Rel(webApp, noSqlDb, "Stores and retrieves data")

  UpdateElementStyle(user, $fontColor="black", $bgColor="lightgrey", $borderColor="black")
  UpdateElementStyle(webApp, $fontColor="black", $bgColor="lightblue", $borderColor="black")
  UpdateElementStyle(azureDevOps, $fontColor="black", $bgColor="lightgreen", $borderColor="black")
  UpdateElementStyle(noSqlDb, $fontColor="black", $bgColor="lightyellow", $borderColor="black")
```