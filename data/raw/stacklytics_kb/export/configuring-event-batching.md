---
title: "Configuring event batching"
category: how_to_onboarding
department: export
tier_visibility: ["Platinum", "Diamond", "Gold"]
article_id: configuring-event-batching
last_updated: "2026-05-12"
---

# Configuring event batching

## Introduction to Event Batching
Configuring event batching is an essential step in optimizing your Stacklytics integration. Event batching allows you to group multiple events together, reducing the number of API requests and improving overall performance. This is particularly useful for customers on the Gold tier, who have a limit of 1M events per month. By batching events, you can minimize the risk of exceeding this limit and incurring a 429 error (RATE_LIMIT_EXCEEDED).

## Tier Comparison and Event Limits
The following table compares the event limits across different tiers:
| Tier | Events per Month | Support Response Time |
| --- | --- | --- |
| Gold | 1M | 8 hours |
| Diamond | 10M | 4 hours |
| Platinum | unlimited | 1 hour |
As shown in the table, the Platinum tier offers unlimited events, making it an ideal choice for large-scale applications. In contrast, the Gold and Diamond tiers have limited events per month, requiring more careful event batching configuration.

## Troubleshooting and Best Practices
When configuring event batching, it's essential to be aware of common errors such as the 401 error (invalid API key) and the SDK-1042 error (event schema validation failure). To avoid these errors, ensure that your API key is valid and your event schema is correctly formatted. Additionally, refer to the Stacklytics API documentation at https://api.stacklytics.io/v2 for more information on event batching and troubleshooting. By following best practices and monitoring your event batching configuration, you can optimize your Stacklytics integration and ensure seamless data tracking.
