USER_INPUT = """
    Use case:
    As as user, I would like to translate a meeting transcript into Azure DevOps Work Items.
    I would like to upload the transcript to a web application, and have it build a work item hierarchy.
    If I approve the hierarchy, I would like the web application to create the work items in Azure DevOps.

    Technical requirements:
    - The system should be able to handle 1000 requests per second.
    - The system should be able to store 1TB of data.
    - The system should use a NoSQL database.
    - The system should be able to scale horizontally.
    - The system should use Dapr for microservices.
    - Vue.js should be used for the frontend.
    - Python should be used for the backend.
 
    Write the output to the following folder `/Users/simon.stipcich/code/repo/langchain-lab/graphs/codegen/.output/`.
    """
