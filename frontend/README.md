Mobile Web Component Development Assignment
Case Study: IMS-Connect

1. Use Case Model

Use Case Diagram Explanation:

IMS-Connect System:

Represents the central platform for idea management.
Actors:

Employee:
Submits ideas.
Votes on ideas.
Collaborates on ideas.
Tracks the progress of their submissions.
Innovation Manager:
Evaluates and approves ideas.
Monitors the status of ideas across regions.
Generates reports for decision-making.
System Admin:
Oversees access control and security.
Supports PAM integration to protect intellectual property and data.
Generates reports on system usage.
Use Case Descriptions:

Authenticate User:

Actors: Employee, Innovation Manager, System Administrator
Description: All actors must log in to access system features securely.
Extensions/Exceptions: Failed authentication leads to an error message.
Submit an Idea:

Actor: Employee
Description: Employees submit ideas for review. Offline submission is available in areas with connectivity issues.
Includes: Authenticate User
Extensions/Exceptions: Offline submissions are synced later when the connection is restored.
Vote on Ideas:

Actor: Employee
Description: Employees vote on ideas to bring the best ones to the forefront.
Includes: Authenticate User
Extensions/Exceptions: If ideas receive equal votes, managers may manually resolve conflicts.
Track Idea Progress:

Actor: Employee, Innovation Manager
Description: Users monitor the status of ideas through various stages of development.
Includes: Authenticate User
Extends: Submit an Idea
Collaborate on Ideas:

Actor: Employee
Description: Teams from different regions collaborate on refining promising ideas.
Extends: Track Idea Progress
Extensions/Exceptions: Regional teams may face language barriers, resolved via built-in translation features.
Evaluate Ideas:

Actor: Innovation Manager
Description: Managers review and rank submitted ideas based on votes and feasibility.
Includes: Authenticate User
Extends: Vote on Ideas
Approve or Reject Ideas:

Actor: Innovation Manager
Description: Managers decide whether an idea should proceed to the implementation stage.
Included: Evaluate Ideas
Provide Feedback:

Actor: Innovation Manager
Description: Managers provide feedback on ideas to improve them.
Extends: Evaluate Ideas
Assign Resources:

Actor: Innovation Manager
Description: Managers allocate resources like budget, staff, or tools for implementing approved ideas.
Extends: Approve or Reject Ideas
Manage User Access:

Actor: System Administrator
Description: Admins oversee user permissions and access control.
Includes: Authenticate User
Configure Incentive System:

Actor: System Administrator
Description: Admins set up points-based incentives for encouraging participation.
Extensions/Exceptions: Changes in the system require manager approval.
Handle Technical Issues:

Actor: System Administrator
Description: Admins resolve system-related issues to ensure smooth operation.
Extensions/Exceptions: Regional offices with poor connectivity have troubleshooting guides.
Ensure Data Security:

Actor: System Administrator
Description: Admins enforce security protocols to protect sensitive data.
Extensions/Exceptions: Breaches are logged and resolved via incident response protocols.
2. Class Diagram

3. Swimlanes Diagram

4. Type Modal Class Diagram

5. Part A: Business Rules

Submission Rule:

Only authenticated employees can submit ideas. Unauthenticated submissions are not allowed.
Voting Rule:

Each employee is allowed one vote per idea, and votes cannot be changed once cast.
Approval Rule:

Innovation Managers must evaluate submitted ideas within 14 days of submission.
Data Security Rule:

All data must be encrypted and stored securely, adhering to company privacy policies.
Feedback Rule:

Feedback on ideas must be tied to specific evaluations and cannot exceed 500 characters.
6. Part B: System Interfaces

Authentication System (Single Sign-On):

IMS-Connect integrates with the company’s SSO system to authenticate employees.
Idea Storage Database:

Ideas and associated data (feedback, votes, etc.) are stored in a centralized, cloud-based database.
AI Filter Module:

An AI module assists with sorting and prioritizing ideas based on keywords and voting patterns.
Report Generation API:

The system uses an external API to create detailed reports on idea submissions, votes, and progress.
Collaboration Tool Integration:

IMS-Connect links with collaboration tools (e.g., Slack, Microsoft Teams) to facilitate team discussions on approved ideas.
7. Component Architecture Diagram

8. Interaction Diagram
art A: Business Rules for IMS-Connect

Here are five business rules that define the behavior and constraints of IMS-Connect:

Submission Rule: Only authenticated employees can submit ideas. Unauthenticated submissions are not allowed to maintain data security and ensure that all contributions come from verified personnel.

Voting Rule: Each employee is allowed one vote per idea, and votes cannot be changed once cast. This ensures that voting remains fair and unbiased.

Approval Rule: Innovation Managers must evaluate submitted ideas within 14 days of submission. This rule ensures timely assessment and reduces delays in moving ideas through the pipeline.

Data Security Rule: All data must be encrypted and stored securely, adhering to company privacy policies. This includes both idea submissions and feedback to protect sensitive information.

Feedback Rule: Feedback on ideas must be tied to specific evaluations and cannot exceed 500 characters. This rule helps maintain constructive and clear communication.

Part B: System Interfaces

Here are five examples of system interfaces that IMS-Connect will integrate with:

Authentication System (Single Sign-On): IMS-Connect integrates with the company’s Single Sign-On (SSO) system to authenticate employees, ensuring secure access to the platform.

Idea Storage Database: Ideas and associated data (feedback, votes, etc.) are stored in a centralized, cloud-based database to facilitate easy access and management.

AI Filter Module: An AI-powered module assists in sorting and prioritizing ideas based on keywords, votes, and user patterns, helping Innovation Managers filter high-potential ideas efficiently.

Report Generation API: The system uses an external API to create detailed reports on idea submissions, votes, and progress, which can be used for management decision-making.

Collaboration Tool Integration: IMS-Connect links with collaboration tools like Slack and Microsoft Teams to facilitate team discussions on approved ideas and promote cross-regional collaboration.

Task 6: Component Architecture Diagram

The Component Architecture Diagram for IMS-Connect should include major components such as:

Front-end: User Interface (UI) for employees, Innovation Managers, and system administrators.
Back-end: Includes the authentication system, idea submission and voting modules, report generation, and AI filtering system.
Database: Centralized cloud storage for ideas, votes, feedback, and user data.
AI Module: For filtering ideas based on voting patterns and relevance.
Security Module: Integrates with PAM for protecting intellectual property and data privacy.
Interaction Diagram

The Interaction Diagram would depict the flow of interactions between the different components in the system:

User Authentication: Employees, Innovation Managers, and system admins authenticate via SSO.
Idea Submission: Employees submit ideas through the UI, which are then stored in the centralized database.
Voting: Employees vote on ideas, and their votes are recorded.
AI Filtering: AI system filters ideas based on keywords and voting patterns.
Reporting: Reports are generated using an API, summarizing submission details, votes, and status.
Collaboration: Team members collaborate through integrated tools like Slack or Microsoft Teams.