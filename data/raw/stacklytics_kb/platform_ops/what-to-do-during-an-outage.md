---
title: "What to do during an outage"
category: outage_downtime
department: platform_ops
tier_visibility: ["Platinum", "Diamond", "Gold"]
article_id: what-to-do-during-an-outage
last_updated: "2026-05-12"
---

# What to do during an outage

## Introduction to Outages
In the event of an outage, our team works diligently to resolve the issue as quickly as possible. To stay informed about the status of our services, please visit our status page at https://status.stacklytics.io. This page provides real-time updates on any ongoing outages or maintenance. Our uptime SLA guarantees a certain level of availability, with Platinum customers receiving 99.95% uptime, Diamond customers receiving 99.9%, and Gold customers receiving 99.5%.

## Troubleshooting Common Issues
Before assuming an outage, please check your API key and ensure it is valid. A 401 error code indicates an invalid API key, which can be resolved by verifying your credentials. Additionally, be mindful of rate limits, as exceeding them will result in a 429 error code with the message RATE_LIMIT_EXCEEDED. If you are experiencing issues with event schema validation, you may encounter an SDK-1042 error, which can be resolved by reviewing your event schema.

## Next Steps
If you have confirmed an outage and are experiencing issues, please review our support response times for your tier. Platinum customers can expect a response within 1 hour, Diamond customers within 4 hours, and Gold customers within 8 hours, Monday through Friday, 9am-5pm Pacific Time. If you are experiencing a critical issue, please submit a ticket and our support team will work to resolve it as quickly as possible.
