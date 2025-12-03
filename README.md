# aws-website-uptime-monitor
A cost-efficient, serverless website monitoring and alerting system built with AWS Lambda, EventBridge, and SNS.

# 🌐 AWS Serverless Website Uptime Monitor :-
Built By: Atharva

🚀 Project Overview :-
This project implements a highly available, cost-optimized, and fully serverless solution on AWS to perform scheduled health checks on a target URL. It ensures business continuity by providing real-time alerting the moment a service failure is detected.
This architecture validates proficiency in core AWS serverless services, infrastructure automation, and robust monitoring practices.

# 🏛️ Architecture and Data Flow :-
  For this refer the pdf file and the images of dataflow / workflow.
  
# ⚙️ Technical Deep Dive & Key Learnings :-
This section highlights the specific technical choices that demonstrate best practices:
1. Cost Efficiency (Serverless First): By choosing Lambda and EventBridge, the solution operates entirely within the AWS Free Tier for typical usage, incurring costs only during execution time (milliseconds),
   eliminating the overhead and cost of dedicated EC2 instances. 
2. Secure Execution: Implemented a fine-grained IAM Role for the Lambda function, strictly enforcing the Principle of Least Privilege. The role only allows write access to its designated DynamoDB table and
   publishing to the SNS topic.
3. Resilience & Error Handling: The Python code within Lambda is configured to specifically catch HTTPError and URLError exceptions, distinguishing between application-level failures (e.g., 500 status codes) and
   network/DNS/timeout failures, providing precise alert information.
4. Configuration as Environment Variables: All sensitive configuration data (Target URL, SNS ARN) is passed securely to the Lambda function via Environment Variables, separating configuration from code logic.

# 🛠️ Quick Setup Guide
To replicate this environment:
1. Dependencies: Ensure Python 3.x and the Boto3 SDK are available.
2. AWS Console Steps:
   * Create a DynamoDB table (UptimeMonitorResults) with target_url as the Partition Key. 
   * Create an SNS Topic (UptimeAlertsTopic) and subscribe your email.  
   * Deploy the lambda_function.py code to a Lambda function with the required IAM Role. 
   * Configure the TARGET_URL, SNS_TOPIC_ARN, and DYNAMODB_TABLE_NAME as environment variables. 
   * Create an EventBridge Rule to trigger the Lambda every 5 minutes.

# 📜 License
This project is open source and available under the MIT License.

© 2025 ATHARVA
