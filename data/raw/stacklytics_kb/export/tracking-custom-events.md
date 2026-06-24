---
title: "Tracking custom events"
category: how_to_onboarding
department: export
tier_visibility: ["Platinum", "Diamond", "Gold"]
article_id: tracking-custom-events
last_updated: "2026-05-12"
---

# Tracking custom events

## Introduction to Custom Events
Tracking custom events is a key feature of Stacklytics, allowing engineering teams to gain valuable insights into their application's performance. To get started, you'll need to integrate our SDKs, available in JavaScript, Python, and Go, into your application. Our API base URL, https://api.stacklytics.io/v2, is used to send events to our servers. Make sure to handle common errors, such as 401 for invalid API keys and 429 for rate limit exceeded, to ensure seamless data tracking.

## Sending Custom Events
When sending custom events, it's essential to validate your event schema to avoid errors like SDK-1042. Our SDKs provide built-in validation to help you catch any issues before sending the events to our servers. Depending on your plan, you'll have a limited or unlimited number of events you can send per month, with Gold plans limited to 1M events/mo and Platinum plans having no limits. Be sure to check your plan details to avoid exceeding your event limits and incurring potential rate limit errors.

## Troubleshooting and Support
If you encounter any issues while tracking custom events, our support team is available to help. Platinum plan customers can expect a response within 1 hour, while Diamond and Gold plan customers can expect a response within 4 hours and 8 hours, respectively, during our support hours of Monday-Friday, 9am-5pm Pacific Time. You can also check our status page, https://status.stacklytics.io, for any ongoing issues that may be affecting your event tracking.
