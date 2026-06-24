---
title: "Handling 429 rate limit errors"
category: sdk_api_error
department: integrations
tier_visibility: ["Platinum", "Diamond", "Gold"]
article_id: handling-429-rate-limits
last_updated: "2026-05-12"
---

# Handling 429 rate limit errors

## Introduction to Rate Limit Errors
If you're encountering a 429 error code, also known as RATE_LIMIT_EXCEEDED, it means you've exceeded the allowed number of requests to the Stacklytics API within a given time frame. This error can occur when your application is sending too many events to our servers, surpassing the limits defined by your plan. For example, if you're on the Gold tier, you're limited to 1M events per month. 

## Understanding Your Plan Limits
To avoid hitting the rate limit, it's essential to understand the event limits associated with your plan. The Diamond tier, for instance, allows up to 10M events per month, while the Platinum tier offers unlimited events. If you're consistently reaching your event limit, you may want to consider upgrading to a higher tier to accommodate your needs. You can find more information about your plan limits by reviewing your invoice or contacting our support team.

## Resolving Rate Limit Errors
If you've received a 429 error, you can resolve the issue by reducing the number of requests to the Stacklytics API or by upgrading to a higher tier. You can also use our API base URL, https://api.stacklytics.io/v2, to implement exponential backoff in your application, which can help prevent rate limit errors. Additionally, you can monitor your event usage and plan limits on our status page, https://status.stacklytics.io, to anticipate and prevent rate limit errors.
