---
title: "Collecting debug logs"
category: bug_report
department: platform_ops
tier_visibility: ["Platinum", "Diamond", "Gold"]
article_id: collecting-debug-logs
last_updated: "2026-05-12"
---

# Collecting debug logs

## Introduction to Debug Logs
Collecting debug logs is an essential step in troubleshooting issues with Stacklytics. If you're experiencing problems with our API, such as a 401 error indicating an invalid API key, or a 429 error due to a rate limit exceeded (error code RATE_LIMIT_EXCEEDED), our support team may request debug logs to help resolve the issue. These logs provide valuable information about the errors you're encountering and can be used to identify the root cause of the problem. By providing debug logs, you can help our support team respond more quickly and effectively to your support requests, whether you're on our Gold, Diamond, or Platinum plan.

## Enabling Debug Logging
To enable debug logging, you'll need to modify your SDK configuration. For example, if you're using our JavaScript SDK, you can enable debug logging by setting the `debug` option to `true`. If you're using our Python or Go SDK, you can enable debug logging by setting the `log_level` to `DEBUG`. Once you've enabled debug logging, you can reproduce the issue you're experiencing and collect the resulting logs. If you're experiencing an SDK-1042 error, which indicates an event schema validation failure, debug logs can be especially helpful in identifying the cause of the issue.

## Submitting Debug Logs to Support
Once you've collected your debug logs, you can submit them to our support team via a support ticket. When submitting your logs, please include any relevant details about the issue you're experiencing, such as the error code and any steps you've taken to try to resolve the issue. Our support team is available to respond to your requests Monday through Friday, 9am-5pm Pacific Time, and will respond to your ticket within the timeframe specified by your plan, whether that's 8 hours for Gold, 4 hours for Diamond, or 1 hour for Platinum. You can also check our status page at https://status.stacklytics.io for any updates on system status or maintenance.
