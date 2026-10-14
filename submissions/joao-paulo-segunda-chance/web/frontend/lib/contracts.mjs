// Generated from domain/source_contracts.py; regenerate instead of diverging.
export const contracts = {
  "accounts": {
    "account_id": {
      "kind": "text",
      "nullable": false
    },
    "account_name": {
      "kind": "text",
      "nullable": false
    },
    "industry": {
      "kind": "text",
      "nullable": false
    },
    "country": {
      "kind": "text",
      "nullable": false
    },
    "referral_source": {
      "kind": "text",
      "nullable": false
    },
    "plan_tier": {
      "kind": "text",
      "nullable": false
    },
    "seats": {
      "kind": "integer",
      "nullable": false
    },
    "is_trial": {
      "kind": "boolean",
      "nullable": false
    },
    "churn_flag": {
      "kind": "boolean",
      "nullable": false
    },
    "signup_date": {
      "kind": "date",
      "nullable": false
    }
  },
  "subscriptions": {
    "subscription_id": {
      "kind": "text",
      "nullable": false
    },
    "account_id": {
      "kind": "text",
      "nullable": false
    },
    "plan_tier": {
      "kind": "text",
      "nullable": false
    },
    "billing_frequency": {
      "kind": "text",
      "nullable": false
    },
    "seats": {
      "kind": "integer",
      "nullable": false
    },
    "mrr_amount": {
      "kind": "numeric",
      "nullable": false
    },
    "arr_amount": {
      "kind": "numeric",
      "nullable": false
    },
    "is_trial": {
      "kind": "boolean",
      "nullable": false
    },
    "upgrade_flag": {
      "kind": "boolean",
      "nullable": false
    },
    "downgrade_flag": {
      "kind": "boolean",
      "nullable": false
    },
    "churn_flag": {
      "kind": "boolean",
      "nullable": false
    },
    "auto_renew_flag": {
      "kind": "boolean",
      "nullable": false
    },
    "start_date": {
      "kind": "date",
      "nullable": false
    },
    "end_date": {
      "kind": "date",
      "nullable": true
    }
  },
  "usage": {
    "usage_id": {
      "kind": "text",
      "nullable": false
    },
    "subscription_id": {
      "kind": "text",
      "nullable": false
    },
    "feature_name": {
      "kind": "text",
      "nullable": false
    },
    "usage_count": {
      "kind": "integer",
      "nullable": false
    },
    "usage_duration_secs": {
      "kind": "integer",
      "nullable": false
    },
    "error_count": {
      "kind": "integer",
      "nullable": false
    },
    "is_beta_feature": {
      "kind": "boolean",
      "nullable": false
    },
    "usage_date": {
      "kind": "date",
      "nullable": false
    }
  },
  "support": {
    "ticket_id": {
      "kind": "text",
      "nullable": false
    },
    "account_id": {
      "kind": "text",
      "nullable": false
    },
    "priority": {
      "kind": "text",
      "nullable": false
    },
    "first_response_time_minutes": {
      "kind": "integer",
      "nullable": false
    },
    "resolution_time_hours": {
      "kind": "numeric",
      "nullable": true
    },
    "satisfaction_score": {
      "kind": "numeric",
      "nullable": true
    },
    "escalation_flag": {
      "kind": "boolean",
      "nullable": false
    },
    "submitted_at": {
      "kind": "timestamp",
      "nullable": false
    },
    "closed_at": {
      "kind": "timestamp",
      "nullable": true
    }
  },
  "churn": {
    "churn_event_id": {
      "kind": "text",
      "nullable": false
    },
    "account_id": {
      "kind": "text",
      "nullable": false
    },
    "reason_code": {
      "kind": "text",
      "nullable": false
    },
    "feedback_text": {
      "kind": "text",
      "nullable": true
    },
    "refund_amount_usd": {
      "kind": "numeric",
      "nullable": false
    },
    "preceding_upgrade_flag": {
      "kind": "boolean",
      "nullable": false
    },
    "preceding_downgrade_flag": {
      "kind": "boolean",
      "nullable": false
    },
    "is_reactivation": {
      "kind": "boolean",
      "nullable": false
    },
    "churn_date": {
      "kind": "date",
      "nullable": false
    }
  }
};
export const contractVersion = "1.0.0";
