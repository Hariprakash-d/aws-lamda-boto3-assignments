# AWS Cloud Automation Engine Portfolio

A production-grade suite of event-driven, serverless automation frameworks designed to optimize costs, enforce lifecycle security baselines, and inject programmatic governance across AWS infrastructure pools.

---

## 🏗️ Architecture System Blueprint

This portfolio showcases four main architectural patterns utilizing **AWS Lambda (Python/Boto3)**, **Amazon EventBridge**, **Amazon SNS**, and native cloud monitoring APIs:

```mermaid
graph TD
    %% Global Triggers
    EB_Sched[Amazon EventBridge Scheduler] -->|Daily/Weekly Cron| L_Storage[Lambda: S3 & EBS Engineers]
    EB_Event[Amazon EventBridge Events] -->|Real-time State Change| L_Compute[Lambda: EC2 Auto-Tagger]
    
    %% Task 1 & 2 Execution Paths
    L_Storage -->|s3:DeleteObject| S3[Task 1: Amazon S3 Bucket Purge]
    L_Storage -->|ec2:Create/DeleteSnapshot| EBS[Task 2: Automated EBS Snapshot Engine]
    
    %% Task 3 Execution Path
    L_Compute -->|ec2:CreateTags| EC2[Task 3: Real-Time EC2 compliance Tagging]
    
    %% Task 4 Execution Path
    EB_Sched -->|ce:GetCostAndUsage| L_FinOps[Lambda: Cost Explorer Analytics]
    L_FinOps -->|sns:Publish| SNS[Task 4: FinOps Slack & Email Cost Alerts]

    %% Styling
    style L_Storage fill:#ff9900,stroke:#333,stroke-width:1px,color:#fff
    style L_Compute fill:#ff9900,stroke:#333,stroke-width:1px,color:#fff
    style L_FinOps fill:#ff9900,stroke:#333,stroke-width:1px,color:#fff
    style EB_Sched fill:#ff4f4f,stroke:#333,stroke-width:1px,color:#fff
    style EB_Event fill:#ff4f4f,stroke:#333,stroke-width:1px,color:#fff
```

---

## 📁 Repository Structure

Each automation component is fully self-contained inside its respective directory, complete with zero-dependency source code, least-privilege IAM configuration frameworks, and granular configuration runbooks.

```text
.
├── 01-s3-bucket-cleanup/
│   ├── lambda_function.py      # Boto3 object lifecycle execution script
│   └── README.md               # Step-by-step S3 setup & lifecycle discussion points
├── 02-ebs-snapshot-manager/
│   ├── lambda_function.py      # Targeted snapshot creation & retention loop 
│   └── README.md               # IAM inline policy guides & DLM trade-off analysis
├── 03-ec2-auto-tagger/
│   ├── lambda_function.py      # Real-time metadata tracking engine
│   └── README.md               # Event pattern rules & CloudTrail user-extraction bonus
└── 04-daily-cost-notifier/
    ├── lambda_function.py      # Month-to-Date FinOps calculation core
    └── README.md               # SNS subscription configurations & AWS Budgets comparison
```

---

## 🚀 Module Executive Summaries

### [Task 1: Automated S3 Bucket Cleanup](./01-s3-bucket-cleanup/)
*   **Objective**: Mitigate structural storage bloat by automatically purging stale objects.
*   **Core Logic**: Iterates across target bucket namespaces using `s3.list_objects_v2`, evaluates object age properties via UTC timezone arrays, and issues atomic `DeleteObject` calls for files exceeding a 30-day lifecycle threshold.
*   **Trigger**: Daily EventBridge Scheduler rules.

### [Task 2: Automated EBS Snapshot Creation and Cleanup](./02-ebs-snapshot-manager/)
*   **Objective**: Establish a custom, programmatic data recovery engine for block storage components.
*   **Core Logic**: Generates an isolated volume snapshot tagged with custom runtime metadata markers (`CreatedBy=Lambda-Backup`), sweeps for historical backups owning that matching signature, and programmatically purges targets older than a 30-day retention window.
*   **Trigger**: Weekly EventBridge cron orchestration.

### [Task 3: Auto-Tagging EC2 Instances on Launch](./03-ec2-auto-tagger/)
*   **Objective**: Enforce runtime structural tracking, explicit ownership mapping, and resource allocation tags.
*   **Core Logic**: Intercepts real-time `EC2 Instance State-change Notification` payloads, extracts target instance metadata coordinates, and dynamically injects global tags including `LaunchDate`, `Environment`, and `Owner` at initialization.
*   **Trigger**: Real-time EventBridge State Match (`running`).

### [Task 4: Daily AWS Cost Alert Engine](./04-daily-cost-notifier/)
*   **Objective**: Implement modern FinOps boundaries to avoid surprise budget spikes without legacy CloudWatch mechanisms.
*   **Core Logic**: Interrogates the global AWS Cost Explorer API (`ce:GetCostAndUsage`) to compute precise Month-to-Date (MTD) unblended expenditures and issues high-priority notification traces down an Amazon SNS email/webhook delivery pipeline if financial ceilings are breached.
*   **Trigger**: Daily automated morning evaluation check.

---

## 🛡️ Enterprise Governance & Best Practices Applied

*   **Least-Privilege Scoping**: Every automation pipeline runs under its own localized IAM Execution Role, completely eliminating wildcard (`"Resource": "*"`) permissions for state mutations.
*   **Network-Independent Configurations**: Functions are built to decouple from strict private VPC isolation boundaries unless specifically routed to dedicated endpoint infrastructure, preventing API execution timeout bugs.
*   **Serverless Efficiency**: Compute pipelines run strictly on an event-driven basis—zero infrastructure assets are left running idle, ensuring total compliance framework upkeep for less than pennies per month.

***
*For specific step-by-step instructions, copy-pasteable JSON IAM policies, and manual validation testing configurations, please open the dedicated subfolders listed above.*
