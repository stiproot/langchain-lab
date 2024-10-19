# Example of a C4 Container Diagram in Mermaid

## Overview
This is an example of a C4 Container diagram.
It depicts a microservice architecture. 
It is a system that gathers Work Items from the Azure DevOps API, Work Items are summarized and then structured into hierarchical tree structure, and persisted to a store.
The tree structure is used by the D3.js charting library in the user-facing web application.

## Summary of containers

**UI**
Web application used to display charts that represent the health of a project.

**UI API**
Acts as a gateway to the backend services.
- Endpoint for querying for data
- Endpoint for publishing a request to rebuild a data structures

**Kafka API**
- Enpoint for publishing messages to Kafka

**Cuchbase API**
- Endpoint for querying data in Couchbase
- Endpoint for persisting data to Couchbase

**Persist Worker**
- Consume messages off a dedicated 'persist' topic
- Persist data to Couchbase, through the Couchbase API

**Insights Worker**
- Consume messages off a dedicated 'insights' command topic
- Gather work item details from Azure DevOps
- Structure data in a summarized tree format
- Persist tree structure through by publishing a persit command to Kafka, through the Kafka API

## Diagram
```mermaid
C4Context
  title System Context Diagram for Microservice Architecture

  Person(user, "User", "")

  Enterprise_Boundary(systemBoundary, "System Boundary") {

    Container_Boundary(uiBoundary, "UI Boundary") {
      System(ui, "UI", "Display insights")
      System(uiApi, "UI API", "Serves Metrics")
    }

    Container_Boundary(persistBoundary, "Persist Boundary"){
      Container(persistWorker, "Persist Worker", "Persists data to Couchbase")
      Container(couchbaseApi, "Couchbase Api", "Persist data gateway")
      Container(couchbase, "Couchbase", "Data Storage")
    }

    Container_Boundary(insightsBoundary, "Insights Boundary"){
      Container(insightsWorker, "Insights Worker", "Structures data")
      Container(azdoProxyApi, "AzDO Proxy API", "Interact with AzDO")
    }

    Container_Boundary(extAzdo, "Azure Dev Ops") {
      Container_Ext(extAzdoApi, "Azure DevOps API", "Interact with Azure DevOps")
    }
  }

  System_Boundary(messagingBoundary, "Messaging Boundary") {

    Container(kafkaApi, "Kafka Api", "Kakfa publish gateway")

    System_Boundary(confluentBoundary, "Confluent Boundary") {
      Container_Ext(broker, "Kafka Broker", "Kafka message broker")
      SystemQueue(persistCmdTopic, "persist_cmd_topic", "Cmds to persist payloads to cb")
      SystemQueue(insightsCmdTopic, "insights_cmd_topic", "Cmd to gather insights from Azure DevOps")
    }
  }

  Rel(user, ui, "<<interacts>>")
  Rel(ui, uiApi, "<<request>>")
  Rel(uiApi, couchbaseApi, "<<query read data>>")
  Rel(uiApi, kafkaApi, "<<publish cmd to structure data>>")
  Rel(couchbaseApi, couchbase, "<<query>>,<<upsert>>")

  Rel(persistWorker, persistCmdTopic, "<<consume persist cmds>>")
  Rel(persistWorker, couchbaseApi, "<<persist data req>>")

  Rel(insightsWorker, insightsCmdTopic, "<<consume structure cmds>>")
  Rel(insightsWorker, kafkaApi, "<<persist structure req>>")
  Rel(insightsWorker, azdoProxyApi, "<<perform azdo op cmd>>")
  Rel(azdoProxyApi, extAzdoApi, "<<perform azdo op req>>")

  Rel(kafkaApi, broker, "<<publish cmd>>")

  Rel(broker, persistCmdTopic, "<<produce msg>>")
  Rel(broker, insightsCmdTopic, "<<produce msg>>")

```
