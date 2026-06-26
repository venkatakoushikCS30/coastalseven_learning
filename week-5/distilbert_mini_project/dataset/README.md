# FAQ Intent Dataset

Customer-support FAQ dataset for DistilBERT intent classification (14 classes).

## Folder layout

```
dataset/
├── raw/
│   └── faq_intents.csv       # 210 samples (text, intent)
└── processed/
    ├── train.csv             # 146 samples (text, intent, label_id)
    ├── val.csv               # 32 samples
    ├── test.csv              # 32 samples
    └── label_maps.json       # id2label / label2id mappings
```

## Columns

| File | Columns |
|------|---------|
| `raw/faq_intents.csv` | `text`, `intent` |
| `processed/*.csv` | `text`, `intent`, `label_id` |

## Intent classes (14)

account_login, password_reset, billing_payment, refund_request, subscription_cancel, shipping_status, return_exchange, product_info, technical_support, feature_request, hours_location, contact_support, warranty_claim, account_delete

## Kaggle upload

Upload **only the contents of `processed/`** as a Kaggle Dataset:

- train.csv
- val.csv
- test.csv
- label_maps.json

Then set `DATA_DIR = "/kaggle/input/<your-dataset-name>"` in the notebook.
