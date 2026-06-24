---
title: "Events not appearing in your dashboard"
category: data_sync_issue
department: integrations
tier_visibility: ["Platinum", "Diamond", "Gold"]
article_id: events-not-appearing
last_updated: "2026-05-12"
---

# Events not appearing in your dashboard

## Introduction to Event Tracking
If your events are not appearing in your dashboard, there are several potential causes to investigate. First, ensure that your API key is valid and correctly configured in your application. An invalid API key will result in a 401 error, indicating that the key is not recognized by our system. You can verify your API key by checking the API base URL, https://api.stacklytics.io/v2, and reviewing your API key documentation.

## Common Errors and Troubleshooting
Another common issue is exceeding the rate limit for your tier. If you receive a 429 error with the code RATE_LIMIT_EXCEEDED, you may need to upgrade to a higher tier, such as Diamond or Platinum, which offer more generous event limits. For example, the Gold tier includes 1M events/mo, while the Diamond tier includes 10M events/mo. Additionally, if you encounter an SDK-1042 error, it indicates an event schema validation failure, which can be resolved by reviewing your event schema and ensuring it conforms to our validation rules.

## Resolving Event Tracking Issues
To resolve event tracking issues, review your application's integration with our SDKs, available in JavaScript, Python, and Go. Ensure that you are using the correct SDK and that it is properly configured. If you are still experiencing issues, you can contact our support team, which is available Monday-Friday, 9am-5pm Pacific Time, for assistance. Platinum tier customers can expect a response within 1 hour, while Diamond and Gold tier customers can expect a response within 4 hours and 8 hours, respectively. You can also check our status page, https://status.stacklytics.io, for any ongoing issues that may be affecting your event tracking.
