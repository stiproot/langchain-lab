
# Work Item Specification (WIS)
**Work Item Types:**
- Programme
- Small/Large/Medium Project
- Epic
- Feature
- User Story
- Task

**Example of work item hierarchy:**
```yml
- type: Small Project
  title: Build a new support website
  children:
    - type: Epic
      title: User telemetry dashboard
      children:
        - type: Feature
          title: Predictive analytics
          children:
            - type: User Story
              title: As as user, I want to see the predicted number of support tickets for the next month
              children:
                - type: Task
                  title: Create a predictive model
                - type: Task
                  title: Investigate telemetry streaming technology stack
```