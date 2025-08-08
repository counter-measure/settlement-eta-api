# Linear Tasks
Refer to the file project_metadata.json for the project title and the teams that will be implementing this project. Update the fields below with this information.

PROJECT_NAME = <example>
PROJECT_ID = <example> // Lookup using the PROJECT NAME using Linear MCP
TEAMS = <teams>

## MCP
Connect to the Linear MCP.

## GOAL 
Create Linear Tasks for Each task in tasks.json.

## How to use (To be carried out by a human)
Use Claude or Taskmaster to create a tasks.json file based on your prd.md, tech_design.md and ui_design.md.
Then use Claude, Claude Code or Cursor to complete the following instructions.

## Instructions
- Connect to the Linear MCP and carry out the following tasks
- Get the Linear Project Id for project PROJECT_NAME and store it in PROJECT_ID 
- Get the Team called "Engineering" and assign all issues to this Team
- Create a Linear Issue for each task in tasks.json
- Make sure to associate each issue with the project PROJECT_NAME
- Label each issue with the Epic name from tasks.json
- Update the Issue "Priority" field with the priority from tasks.json using this mapping:
  - P0 = 2 High
  - P1 = 3 Medium
  - P2 = 4 Low
  - P3 = 0 No Priority
- Update the Issue "estimate" field using the "effort" from tasks.json using this mapping:
  - 1 hr = 1 XS
  - 0.5 day = 2 S
  - 1 day = 3 M
  - 2 day = 4 L
  - 3 day = 5 XL
  - 3 to 5 day = 6 XXL
  - >5 day = 7 XXXL
  

