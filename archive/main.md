# Main Prompt
This prompt controls the generation of documentation for Everclear's projects and linear tickets.

## Overview.md 
The user has created the file overview.md which contains the overview of this project.
This will be used as the starting point for our documentation. 

## Project Details
Refer to the file project_metadata.json for the project title and the teams that will be implementing this project.

## Instructions

### Documentation
Follow this exact sequence to generate the necessary documentation and Linear tickets.
For each document below follow this sequence:
1. Read the file overview.md and all other markdown files in the repository
2. Create the document specified
3. Critique the document produced and recommend suggestions to improve the document, be very harsh
4. Make the suggested updates
5. Give the user the opportunity to review the document and make changes

Follow the sequence above to produce each of the following documents in order:
1. Product requirements document in the file prd.md
2. User stories document in the file user_stories.md
3. Technical design document in the file tech_design.md
4. Technical requirements document in the file tech_requirements.md
5. If the project requires a UI design create it in the file ui_design.md

### Tasks
Read all markdown files in this directory and create a prioritised task list tasks.json.
The file should have the following fields and format:

```
{
    "project": "Project name",
    "version": "1.0",
    "lastUpdated": "2025-01-27",
    "description": "Prioritized tasks derived from prd.md for project_name",
    "epics": [
            {
            "epic": "epic name",
            "tasks": [
                    {
                    "id": "task id",
                    "title": "title",
                    "description": "Task description",
                    "priority": "P0 to P3",
                    "effort": "N days",
                    "dependencies": ["task id"],
                    "acceptanceCriteria": [
                        "criteria 1",
                        "criteria 2"
                    ],
                    "definitionOfDone": [
                        "definition 1",
                        "definition 2"
                    ]
                    }
            ]
            }
    ]
}
```

### Linear 
Follow the instructions in linear-tasks-prompt.md to create linear issues using the tasks.json file.