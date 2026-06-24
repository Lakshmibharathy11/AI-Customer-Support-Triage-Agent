---
title: "Troubleshooting duplicate events"
category: data_sync_issue
department: integrations
tier_visibility: ["Platinum", "Diamond", "Gold"]
article_id: duplicate-events-troubleshooting
last_updated: "2026-05-12"
---

# Troubleshooting duplicate events

## Introduction to Duplicate Events
Duplicate events can occur in Stacklytics due to various reasons, including incorrect implementation of our SDKs or issues with your application's event tracking logic. To troubleshoot duplicate events, first ensure that you are using the correct API base URL, https://api.stacklytics.io/v2, and that your API key is valid. If you encounter a 401 error, it indicates an invalid API key, which may be causing the duplication. Review your API key and implementation to resolve this issue.

## Common Causes and Solutions
One common cause of duplicate events is exceeding the rate limit, which returns a 429 error with the code RATE_LIMIT_EXCEEDED. To avoid this, review your event tracking logic and adjust it according to your plan's event limits: 1M events/mo for Gold, 10M events/mo for Diamond, and unlimited events for Platinum. Additionally, ensure that your event schema is valid to prevent SDK-1042 errors, which indicate event schema validation failures. You can find more information on event schema validation in our SDK documentation for JavaScript, Python, and Go.

## Resolving Ongoing Issues
If you continue to experience issues with duplicate events after troubleshooting, contact our support team for further assistance. As a Gold, Diamond, or Platinum customer, you can expect a support response within 8, 4, or 1 hour, respectively, during our support hours of Monday-Friday, 9am-5pm Pacific Time. You can also check our status page at https://status.stacklytics.io for any ongoing issues that may be contributing to the problem. By working together, we can resolve the issue and ensure that your Stacklytics implementation is running smoothly.
