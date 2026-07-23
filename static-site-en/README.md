# fujiiguruji.com — Deployment Runbook

Static site hosting for *I Bow to the Buddha in You* by Fujii Nichidatsu.  
Stack: **S3 + CloudFront + ACM + Route 53** — no server, no EC2, no OS to maintain.

---

## Architecture

```
fujiiguruji.com  ──►  Route 53  ──►  CloudFront  ──►  S3 bucket
fujiguruji.com   ──►  Route 53  ──►  CloudFront  ──►  (redirect to fujiiguruji.com)
```

- **S3** stores the files (`index.html`, EPUB, PDF)
- **CloudFront** provides HTTPS and global CDN caching
- **ACM** provides the free TLS certificate
- **Route 53** points the domains at CloudFront

Approximate cost: **$0.50–$2.00/month** (Route 53 hosted zone $0.50/month; S3 and CloudFront negligible at low traffic).

---

## Prerequisites

### AWS CLI installed and configured

```bash
# Install (macOS)
brew install awscli

# Configure with your credentials
aws configure
# Prompts for:
#   AWS Access Key ID
#   AWS Secret Access Key
#   Default region: us-east-1
#   Default output format: json
```

> **Note:** Keep your Access Key ID and Secret Access Key out of this repo.  
> Store them in `~/.aws/credentials` (what `aws configure` does) or use IAM Identity Center.

### Verify you're authenticated

```bash
aws sts get-caller-identity
# Should return your Account ID, UserId, and ARN
```

---

## One-time setup

Work through these sections in order. Most steps only need to be done once.

---

### Step 1 — Create the S3 buckets

You need two buckets:
- `fujiiguruji.com` — serves the actual site
- `www.fujiiguruji.com` — redirects to the canonical domain

```bash
# Main bucket
aws s3api create-bucket \
  --bucket fujiiguruji.com \
  --region us-east-1

# www redirect bucket
aws s3api create-bucket \
  --bucket www.fujiiguruji.com \
  --region us-east-1
```

> **Note:** S3 bucket names must match your domain exactly for static website hosting to work cleanly.

#### Enable static website hosting on the main bucket

```bash
aws s3api put-bucket-website \
  --bucket fujiiguruji.com \
  --website-configuration '{
    "IndexDocument": {"Suffix": "index.html"},
    "ErrorDocument": {"Key": "index.html"}
  }'
```

#### Configure www bucket to redirect to the main domain

```bash
aws s3api put-bucket-website \
  --bucket www.fujiiguruji.com \
  --website-configuration '{
    "RedirectAllRequestsTo": {
      "HostName": "fujiiguruji.com",
      "Protocol": "https"
    }
  }'
```

#### Make the main bucket publicly readable

```bash
# First, disable the "block public access" setting
aws s3api put-public-access-block \
  --bucket fujiiguruji.com \
  --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Then attach a public read policy
aws s3api put-bucket-policy \
  --bucket fujiiguruji.com \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::fujiiguruji.com/*"
    }]
  }'
```

---

### Step 2 — Request a TLS certificate (ACM)

> **Critical:** CloudFront only accepts certificates from ACM in **us-east-1** (N. Virginia), regardless of where your other resources live. This is an AWS quirk that catches everyone the first time.

```bash
aws acm request-certificate \
  --domain-name fujiiguruji.com \
  --subject-alternative-names www.fujiiguruji.com fujiguruji.com www.fujiguruji.com \
  --validation-method DNS \
  --region us-east-1
```

This returns a `CertificateArn`. Save it — you'll need it in Step 3.

```bash
# Save the ARN to a shell variable for convenience
CERT_ARN="arn:aws:acm:us-east-1:YOUR_ACCOUNT_ID:certificate/YOUR_CERT_ID"
```

#### Validate the certificate via DNS

ACM needs to verify you own the domains. It does this by asking you to add CNAME records to Route 53.

```bash
# Get the DNS validation records ACM needs
aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --region us-east-1 \
  --query "Certificate.DomainValidationOptions"
```

This returns one or two CNAME records. For each one, add it to Route 53:

```bash
# Get your hosted zone ID
aws route53 list-hosted-zones \
  --query "HostedZones[?Name=='fujiiguruji.com.'].Id" \
  --output text
# Returns something like: /hostedzone/Z1234567890ABC
# Strip the /hostedzone/ prefix — just the ID part

ZONE_ID="Z1234567890ABC"

# Add the ACM validation CNAME (repeat for each domain ACM listed)
# Replace NAME and VALUE with what acm describe-certificate returned
aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "_abc123.fujiiguruji.com.",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "_xyz456.acm-validations.aws."}]
      }
    }]
  }'
```

#### Wait for the certificate to validate

```bash
aws acm wait certificate-validated \
  --certificate-arn $CERT_ARN \
  --region us-east-1
# This can take 2–10 minutes. The command exits when done.
```

---

### Step 3 — Create the CloudFront distribution

```bash
aws cloudfront create-distribution \
  --distribution-config "{
    \"CallerReference\": \"fujiiguruji-2026\",
    \"Aliases\": {
      \"Quantity\": 4,
      \"Items\": [\"fujiiguruji.com\", \"www.fujiiguruji.com\", \"fujiguruji.com\", \"www.fujiguruji.com\"]
    },
    \"DefaultRootObject\": \"index.html\",
    \"Origins\": {
      \"Quantity\": 1,
      \"Items\": [{
        \"Id\": \"S3-fujiiguruji.com\",
        \"DomainName\": \"fujiiguruji.com.s3-website-us-east-1.amazonaws.com\",
        \"CustomOriginConfig\": {
          \"HTTPPort\": 80,
          \"HTTPSPort\": 443,
          \"OriginProtocolPolicy\": \"http-only\"
        }
      }]
    },
    \"DefaultCacheBehavior\": {
      \"TargetOriginId\": \"S3-fujiiguruji.com\",
      \"ViewerProtocolPolicy\": \"redirect-to-https\",
      \"CachePolicyId\": \"658327ea-f89d-4fab-a63d-7e88639e58f6\",
      \"Compress\": true,
      \"AllowedMethods\": {
        \"Quantity\": 2,
        \"Items\": [\"GET\", \"HEAD\"],
        \"CachedMethods\": {\"Quantity\": 2, \"Items\": [\"GET\", \"HEAD\"]}
      }
    },
    \"ViewerCertificate\": {
      \"ACMCertificateArn\": \"$CERT_ARN\",
      \"SSLSupportMethod\": \"sni-only\",
      \"MinimumProtocolVersion\": \"TLSv1.2_2021\"
    },
    \"HttpVersion\": \"http2and3\",
    \"Enabled\": true,
    \"Comment\": \"fujiiguruji.com\"
  }"
```

> Replace `YOUR_CERT_ARN_HERE` with the ARN from Step 2.  
> The `CachePolicyId` `658327ea...` is AWS's built-in "CachingOptimized" policy — use it as-is.

This returns a distribution object. Note the **DomainName** field — it looks like `d1234abcd.cloudfront.net`. You need it for Step 4.

```bash
# Save it
CF_DOMAIN="d1234abcd.cloudfront.net"

# Also save the distribution ID for future cache invalidations
CF_DIST_ID="E1234ABCDEFGH"
```

#### Wait for the distribution to deploy

```bash
aws cloudfront wait distribution-deployed \
  --id $CF_DIST_ID
# Takes 5–15 minutes. Go make tea.
```

---

### Step 4 — Point the domains at CloudFront in Route 53

Do this for both `fujiiguruji.com` and `fujiguruji.com` (each has its own hosted zone).

```bash
# fujiiguruji.com hosted zone
ZONE_ID_MAIN="Z00062872GI36R63HF7KG"   # fujiiguruji.com
ZONE_ID_TYPO="Z09616293J2MGM5Z9R4AU"   # fujiguruji.com (forwards to main)

# Apex domain (fujiiguruji.com) — must use ALIAS, not CNAME
aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID_MAIN \
  --change-batch '{
    "Changes": [
      {
        "Action": "UPSERT",
        "ResourceRecordSet": {
          "Name": "fujiiguruji.com",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "Z2FDTNDATAQYW2",
            "DNSName": "'"$CF_DOMAIN"'",
            "EvaluateTargetHealth": false
          }
        }
      },
      {
        "Action": "UPSERT",
        "ResourceRecordSet": {
          "Name": "www.fujiiguruji.com",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "Z2FDTNDATAQYW2",
            "DNSName": "'"$CF_DOMAIN"'",
            "EvaluateTargetHealth": false
          }
        }
      }
    ]
  }'

# fujiguruji.com (typo domain) — point at the same CloudFront distribution
aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID_TYPO \
  --change-batch '{
    "Changes": [
      {
        "Action": "UPSERT",
        "ResourceRecordSet": {
          "Name": "fujiguruji.com",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "Z2FDTNDATAQYW2",
            "DNSName": "'"$CF_DOMAIN"'",
            "EvaluateTargetHealth": false
          }
        }
      }
    ]
  }'
```

> `Z2FDTNDATAQYW2` is the fixed Hosted Zone ID for **all** CloudFront distributions globally. Use it as-is.

---

### Step 5 — Upload the site files

```bash
# Upload the main HTML file as index.html
aws s3 cp ibow.html s3://fujiiguruji.com/index.html \
  --content-type "text/html; charset=utf-8" \
  --cache-control "max-age=3600"

# Upload the standalone EPUB and PDF (for direct linking if needed)
aws s3 cp I_Bow_to_the_Buddha_in_You.epub s3://fujiiguruji.com/ \
  --content-type "application/epub+zip" \
  --cache-control "max-age=86400"

aws s3 cp I_Bow_to_the_Buddha_in_You.pdf s3://fujiiguruji.com/ \
  --content-type "application/pdf" \
  --cache-control "max-age=86400"
```

#### Verify the bucket contents

```bash
aws s3 ls s3://fujiiguruji.com/
```

---

## Updating the site

When you publish a new version of the HTML file:

```bash
# 1. Upload the new file
aws s3 cp ibow.html s3://fujiiguruji.com/index.html \
  --content-type "text/html; charset=utf-8" \
  --cache-control "max-age=3600"

# 2. Invalidate the CloudFront cache so visitors see the update immediately
aws cloudfront create-invalidation \
  --distribution-id $CF_DIST_ID \
  --paths "/*"
```

> Without the invalidation, CloudFront may serve the old cached version for up to an hour.

---

## Checking the site is up

```bash
# Should return HTTP 200 and the HTML
curl -I https://fujiiguruji.com

# Check that the typo domain redirects
curl -I https://fujiguruji.com
# Should return 301 or 302 to fujiiguruji.com
```

---

## Environment variables

These are stored in `.env` in the repo root. Load them before running any CLI commands:

```bash
source .env
```

> **Important:** Add `.env` to `.gitignore` — it contains your AWS account details and should never be committed.

```
CERT_ARN=arn:aws:acm:us-east-1:174320949457:certificate/625a037c-fd10-498c-b59b-2c207781ec4c
CF_DIST_ID=E1MYF9QA94BFJS
CF_DOMAIN=d1mbsssf8piflx.cloudfront.net
ZONE_ID_MAIN=Z00062872GI36R63HF7KG   # fujiiguruji.com
ZONE_ID_TYPO=Z09616293J2MGM5Z9R4AU   # fujiguruji.com
```

---

## Things AWS will charge you for

| Service | What | Approx. cost |
|---------|------|-------------|
| Route 53 | $0.50/month per hosted zone (×2 domains) | $1.00/month |
| S3 | Storage + requests (tiny at this scale) | < $0.05/month |
| CloudFront | First 1TB transfer/month is free tier; after that $0.0085/GB | ~$0 |
| ACM | TLS certificate | Free |

**Total: ~$1.00–$1.10/month**

---

## Things people always forget

- ACM certificates for CloudFront **must** be requested in `us-east-1`, even if you're in another region
- Apex domains (`fujiiguruji.com` with no www) **cannot** use a CNAME in DNS — they must use an ALIAS record (Route 53's term) pointing at CloudFront
- `Z2FDTNDATAQYW2` is the CloudFront hosted zone ID, the same for everyone — it's not a typo
- After uploading new files, run a CloudFront invalidation or your visitors will see the old version
- CloudFront distribution deployment takes 5–15 minutes; DNS propagation can take up to 48 hours (usually much less)
- The www redirect bucket doesn't need a public access policy — it just redirects, it never serves content directly

---

## Site files in this repo

| File | Description |
|------|-------------|
| `ibow.html` | The website (rename to `index.html` when uploading to S3) |
| `I_Bow_to_the_Buddha_in_You.epub` | Standalone EPUB (also embedded in the HTML) |
| `I_Bow_to_the_Buddha_in_You.pdf` | Standalone PDF (also embedded in the HTML) |
| `README.md` | This file |

---

*Site built with Claude. Source text: Fujii Nichidatsu, translated by Yumiko Miyazaki.*
