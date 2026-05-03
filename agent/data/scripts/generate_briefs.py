"""Generate 5,000 synthetic campaign brief records.

Produces campaign_briefs.csv with the exact 9-column schema. Uses weighted
distributions to hit the requested quality / missingness / industry mix.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

random.seed(20260503)

OUT_PATH = Path(__file__).parent.parent / "raw" / "campaign_briefs.csv"
TOTAL_ROWS = 5000

HEADER = [
    "Campaign Name",
    "Business Objective",
    "Target Audience",
    "Key Message",
    "Channels",
    "Budget",
    "Timeline",
    "Success Metrics",
    "Constraints / Brand Notes",
]

# ---------------------------------------------------------------------------
# Industry / campaign-type catalog
# ---------------------------------------------------------------------------

INDUSTRIES = [
    "B2B SaaS",
    "B2C Retail",
    "E-commerce",
    "Banking",
    "Fintech",
    "Healthcare",
    "Insurance",
    "Education",
    "Travel",
    "Telecom",
    "Consumer Subscription",
    "Events",
    "Professional Services",
]

CAMPAIGN_TYPES = [
    "Product Launch",
    "Trial-to-Paid Conversion",
    "Lead Generation",
    "Customer Reactivation",
    "Upsell",
    "Cross-sell",
    "Loyalty",
    "Retention",
    "Seasonal Promotion",
    "Event Registration",
    "App Adoption",
    "Renewal",
    "Awareness",
]

# Industry-specific budget ranges (low_realistic, high_realistic, currency)
BUDGET_RANGES = {
    "B2B SaaS": (10_000, 250_000),
    "B2C Retail": (5_000, 500_000),
    "E-commerce": (5_000, 500_000),
    "Banking": (20_000, 750_000),
    "Fintech": (20_000, 500_000),
    "Healthcare": (20_000, 750_000),
    "Insurance": (20_000, 750_000),
    "Education": (3_000, 200_000),
    "Travel": (10_000, 400_000),
    "Telecom": (25_000, 600_000),
    "Consumer Subscription": (8_000, 350_000),
    "Events": (3_000, 200_000),
    "Professional Services": (5_000, 150_000),
}

# Industry-specific audience size ranges
AUDIENCE_RANGES = {
    "B2B SaaS": (500, 100_000),
    "B2C Retail": (10_000, 2_000_000),
    "E-commerce": (10_000, 2_000_000),
    "Banking": (5_000, 1_000_000),
    "Fintech": (5_000, 800_000),
    "Healthcare": (5_000, 1_000_000),
    "Insurance": (5_000, 1_000_000),
    "Education": (1_000, 500_000),
    "Travel": (5_000, 800_000),
    "Telecom": (10_000, 1_500_000),
    "Consumer Subscription": (5_000, 600_000),
    "Events": (1_000, 500_000),
    "Professional Services": (1_000, 80_000),
}

CONVERSION_RANGES = {
    "B2B SaaS": (5, 30),
    "B2C Retail": (2, 12),
    "E-commerce": (2, 12),
    "Banking": (2, 15),
    "Fintech": (2, 15),
    "Healthcare": (2, 15),
    "Insurance": (2, 15),
    "Education": (5, 30),
    "Travel": (3, 18),
    "Telecom": (3, 18),
    "Consumer Subscription": (3, 20),
    "Events": (5, 30),
    "Professional Services": (3, 20),
}

# Word banks for naming / messaging
PRODUCT_NAMES = {
    "B2B SaaS": ["Insight Cloud", "FlowOps", "DataPilot", "SyncSuite", "VaultIQ", "PulseAnalytics",
                  "NimbusCRM", "Forge Platform", "Apex Workspace", "Beacon AI", "Helix DevTools",
                  "Lumen API", "Quanta Reports", "Stratus ERP", "OrbitHR"],
    "B2C Retail": ["AuroraWear", "NorthPeak", "Maple & Oak", "Lumen Home", "Halcyon Beauty",
                    "Coastline Apparel", "EmberKitchen", "Drift Footwear", "Saltwater Co."],
    "E-commerce": ["ShopHaven", "Cartly", "BoxBloom", "MarketRise", "Pixie Pantry", "ZestMart",
                    "WrapNorth", "Bundlr"],
    "Banking": ["NorthBridge Bank", "Sterling Federal", "BlueCrest Bank", "Pinecrest Trust",
                 "Anchor National"],
    "Fintech": ["PayLane", "Stackr", "Vaulted", "GlideFi", "MintRail", "Lumio Wallet"],
    "Healthcare": ["CareNova", "MediBridge", "VivaHealth", "OakClinic Network", "Wellpath",
                    "Pulse Primary"],
    "Insurance": ["SafeHarbor Insurance", "AssureFirst", "Northstar Mutual", "Beacon Life",
                   "Truecover"],
    "Education": ["LearnRise Academy", "Edulane", "Cohort Hub", "ScholarPath", "Apex Tutoring",
                   "BrightArc University"],
    "Travel": ["Wayfare", "AzureTrails", "Voyage&Co", "TerraNomad", "Skyloft Hotels", "Glide Cruises"],
    "Telecom": ["Nimbus Mobile", "FiberOne", "Velocity Wireless", "ClearWave", "Orbit Connect"],
    "Consumer Subscription": ["BrewBox", "FitFuel", "PageNest", "Hearth&Home Box", "GlowCrate",
                                "Lumen+"],
    "Events": ["FutureStack Conference", "GrowthSummit", "DevForge Live", "NorthExpo",
                "RetailNext World", "InsureCon"],
    "Professional Services": ["Northbeam Consulting", "Apex Legal", "Helix Advisory",
                                "Forge Accounting", "Quanta Strategy"],
}

# --- Generators -------------------------------------------------------------

def fmt_money(amount: int) -> str:
    return f"${amount:,}"


def pick_industry_and_type() -> tuple[str, str]:
    industry = random.choice(INDUSTRIES)
    # Bias certain types toward certain industries
    type_weights = {t: 1.0 for t in CAMPAIGN_TYPES}
    if industry == "B2B SaaS":
        type_weights["Trial-to-Paid Conversion"] = 3
        type_weights["Lead Generation"] = 3
        type_weights["Upsell"] = 2
    if industry in ("B2C Retail", "E-commerce"):
        type_weights["Seasonal Promotion"] = 3
        type_weights["Loyalty"] = 2
        type_weights["Customer Reactivation"] = 2
    if industry in ("Banking", "Fintech", "Insurance"):
        type_weights["Cross-sell"] = 3
        type_weights["Renewal"] = 2
        type_weights["Lead Generation"] = 2
    if industry == "Healthcare":
        type_weights["Awareness"] = 3
        type_weights["Retention"] = 2
    if industry == "Education":
        type_weights["Lead Generation"] = 3
        type_weights["Event Registration"] = 2
    if industry == "Events":
        type_weights["Event Registration"] = 6
    if industry == "Travel":
        type_weights["Seasonal Promotion"] = 3
        type_weights["Loyalty"] = 2
    if industry == "Telecom":
        type_weights["Renewal"] = 3
        type_weights["Cross-sell"] = 2
    if industry == "Consumer Subscription":
        type_weights["Trial-to-Paid Conversion"] = 3
        type_weights["Retention"] = 3
    types = list(type_weights.keys())
    weights = [type_weights[t] for t in types]
    ctype = random.choices(types, weights=weights, k=1)[0]
    return industry, ctype


REGIONS = ["NA", "EMEA", "APAC", "LATAM", "DACH", "UK", "US", "EU", "ANZ", "Nordics",
           "MENA", "Global"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
YEARS = ["2026", "2026", "2026", "2027"]
SEASONS = ["Spring", "Summer", "Fall", "Winter", "Holiday", "Back-to-School", "Black Friday",
           "Cyber Monday", "Tax Season", "Open Enrollment"]


def make_campaign_name(industry: str, ctype: str, used: set) -> str:
    base = random.choice(PRODUCT_NAMES.get(industry, ["Brand"]))
    code = random.choice(["", f" {random.choice(QUARTERS)} {random.choice(YEARS)}",
                          f" {random.choice(REGIONS)}", f" {random.choice(SEASONS)}",
                          f" v{random.randint(2, 9)}", f" {random.randint(2026, 2027)}"])
    type_word = {
        "Product Launch": "Launch",
        "Trial-to-Paid Conversion": "Trial Conversion Push",
        "Lead Generation": "Lead Gen",
        "Customer Reactivation": "Win-Back",
        "Upsell": "Upsell Wave",
        "Cross-sell": "Cross-sell Drive",
        "Loyalty": "Loyalty Boost",
        "Retention": "Retention Sprint",
        "Seasonal Promotion": "Seasonal Promo",
        "Event Registration": "Event Reg Push",
        "App Adoption": "App Adoption",
        "Renewal": "Renewal Drive",
        "Awareness": "Awareness",
    }[ctype]
    name = f"{base}{code} - {type_word}"
    # Ensure uniqueness
    if name in used:
        suffix = 2
        while f"{name} #{suffix}" in used:
            suffix += 1
        name = f"{name} #{suffix}"
    used.add(name)
    return name


# --- Field generators -------------------------------------------------------

def gen_business_objective(industry: str, ctype: str, aggressive: bool, low_quality: bool) -> str:
    pct_low, pct_high = CONVERSION_RANGES[industry]
    if aggressive:
        # Unrealistic stretch goal
        target = random.randint(pct_high * 2, pct_high * 4)
    else:
        target = random.randint(pct_low, pct_high)
    audience_low, audience_high = AUDIENCE_RANGES[industry]
    n = random.randint(audience_low, audience_high)
    quantified_templates = {
        "Product Launch": [
            f"Acquire {n:,} new users within the launch window",
            f"Drive {target}% adoption of the new release among current customers",
            f"Generate {random.randint(200, 5000):,} qualified sign-ups in the first 60 days",
        ],
        "Trial-to-Paid Conversion": [
            f"Increase trial-to-paid conversion from {max(2, target-5)}% to {target}%",
            f"Convert {random.randint(500, 20000):,} active trial users to paid plans",
        ],
        "Lead Generation": [
            f"Generate {random.randint(300, 15000):,} MQLs at CPL under ${random.randint(20, 250)}",
            f"Deliver {random.randint(100, 3000):,} SQLs to the sales team",
        ],
        "Customer Reactivation": [
            f"Reactivate {target}% of customers dormant for 6+ months",
            f"Win back {random.randint(1000, 50000):,} lapsed customers",
        ],
        "Upsell": [
            f"Lift ARPU by {target}% across the existing book of business",
            f"Upsell {random.randint(500, 20000):,} customers to a higher tier",
        ],
        "Cross-sell": [
            f"Attach a second product to {target}% of single-product customers",
            f"Cross-sell {random.randint(1000, 50000):,} eligible customers",
        ],
        "Loyalty": [
            f"Increase loyalty program enrollment by {target}%",
            f"Lift repeat purchase rate from {max(5, target)}% to {target + 5}%",
        ],
        "Retention": [
            f"Reduce monthly churn from {round(random.uniform(3, 9), 1)}% to {round(random.uniform(1.5, 4), 1)}%",
            f"Improve 90-day retention by {target} percentage points",
        ],
        "Seasonal Promotion": [
            f"Drive ${random.randint(50_000, 5_000_000):,} in incremental revenue during the promo window",
            f"Lift conversion rate by {target}% vs. prior season baseline",
        ],
        "Event Registration": [
            f"Register {random.randint(500, 25_000):,} attendees",
            f"Hit {target}% RSVP-to-attend conversion",
        ],
        "App Adoption": [
            f"Drive {random.randint(5_000, 500_000):,} new app installs",
            f"Lift weekly active users by {target}%",
        ],
        "Renewal": [
            f"Achieve {min(99, 85 + target // 3)}% gross renewal rate",
            f"Renew {random.randint(500, 20_000):,} expiring contracts this cycle",
        ],
        "Awareness": [
            f"Reach {random.randint(100_000, 10_000_000):,} unique impressions in target segment",
            f"Lift unaided brand awareness by {target} points",
        ],
    }
    vague_templates = [
        "Grow the business in the target segment",
        "Drive more revenue from this audience",
        "Increase engagement and pipeline",
        "Build awareness and momentum",
        "Move the needle on conversions this quarter",
        "Support the broader GTM motion",
    ]
    if low_quality and random.random() < 0.55:
        return random.choice(vague_templates)
    if random.random() < 0.12:
        return random.choice(vague_templates)
    return random.choice(quantified_templates[ctype])


VAGUE_AUDIENCES = [
    "young professionals",
    "existing users",
    "enterprise customers",
    "lapsed buyers",
    "high-value customers",
    "millennials",
    "small business owners",
    "general consumers",
    "our customer base",
    "prospects in target markets",
    "premium segment",
    "digital-first audience",
]


def gen_target_audience(industry: str, vague: bool) -> str:
    if vague:
        return random.choice(VAGUE_AUDIENCES)
    age = f"{random.choice([18, 21, 25, 30, 35, 40, 45, 50])}-{random.choice([34, 44, 54, 64, 70])}"
    region = random.choice(["US", "UK", "Canada", "Germany", "France", "Australia", "Japan",
                             "Singapore", "Brazil", "Mexico", "India", "Nordics", "Benelux",
                             "EMEA", "APAC"])
    industry_specific = {
        "B2B SaaS": [
            f"VP/Director of Engineering at companies with 200-2000 employees in {region}",
            f"IT decision-makers at mid-market firms ({region}), {random.choice(['SaaS', 'Fintech', 'Healthtech'])} verticals",
            f"DevOps leads at Series B-D startups in {region}",
            f"CFOs at SMBs with $10M-$100M revenue in {region}",
            f"Marketing operations managers at B2B SaaS companies, {region}",
        ],
        "B2C Retail": [
            f"Women aged {age} interested in sustainable fashion, {region}",
            f"Households with income $75K+ in {region} suburbs",
            f"Gen Z shoppers aged 18-26 in {region} metros",
            f"Repeat customers with 3+ purchases in last 12 months, {region}",
        ],
        "E-commerce": [
            f"Cart abandoners in last 30 days, {region}",
            f"Loyalty members aged {age} in {region}",
            f"First-time site visitors from paid social, {region}",
            f"VIP tier customers (top 10% LTV), {region}",
        ],
        "Banking": [
            f"Mass-affluent customers aged {age} with $50K-$250K deposits, {region}",
            f"Existing checking customers without a credit product, {region}",
            f"Small business banking customers with <$5M annual revenue, {region}",
        ],
        "Fintech": [
            f"Gig workers aged {age} in {region} tier-1 cities",
            f"Active app users with 30+ day inactivity, {region}",
            f"First-time investors aged 25-40 in {region}",
        ],
        "Healthcare": [
            f"Adults aged {age} with chronic condition flags, {region}",
            f"Caregivers aged 40-65 of aging parents, {region}",
            f"Patients overdue for annual wellness visit, {region}",
        ],
        "Insurance": [
            f"Auto policyholders approaching renewal, aged {age}, {region}",
            f"Homeowners aged 35-65 without umbrella coverage, {region}",
            f"Small business owners without cyber liability, {region}",
        ],
        "Education": [
            f"Working professionals aged {age} considering a career change, {region}",
            f"High school juniors and parents in {region}",
            f"Alumni aged 25-45 of partner universities, {region}",
            f"Course completers eligible for the next certification, {region}",
        ],
        "Travel": [
            f"Loyalty members with 1+ booking in last 24 months, {region}",
            f"Couples aged {age} with HHI $100K+, {region}",
            f"Business travelers aged 30-55, {region}",
        ],
        "Telecom": [
            f"Postpaid customers approaching contract end, {region}",
            f"Single-line subscribers eligible for family-plan upgrade, {region}",
            f"Prepaid customers aged {age} with 6+ months tenure, {region}",
        ],
        "Consumer Subscription": [
            f"Trial users in day 7-14 of free trial, {region}",
            f"Subscribers paused in last 90 days, {region}",
            f"Annual plan subscribers approaching renewal, {region}",
        ],
        "Events": [
            f"Past attendees of last 2 editions, {region}",
            f"Practitioners and decision-makers in target verticals, {region}",
            f"Speakers, sponsors, and partner network contacts, {region}",
        ],
        "Professional Services": [
            f"General Counsel and CFOs at mid-market firms, {region}",
            f"Founders of pre-Series A startups, {region}",
            f"HR leaders at companies with 500-5000 employees, {region}",
        ],
    }
    return random.choice(industry_specific[industry])


def gen_key_message(industry: str, ctype: str) -> str:
    templates = {
        "Product Launch": [
            "Introducing the next generation of {product} - faster, smarter, built for your team.",
            "Meet {product}: everything you loved, reimagined.",
            "{product} is here. Get ahead from day one.",
        ],
        "Trial-to-Paid Conversion": [
            "Don't lose what you've built - upgrade today and keep your momentum.",
            "Your trial ends soon. Unlock the full {product} experience.",
            "Ready when you are: pick the plan that fits.",
        ],
        "Lead Generation": [
            "See why leading teams choose {product} - book a 20-minute demo.",
            "Get the playbook trusted by 500+ teams.",
            "Find out what {product} can do for your business.",
        ],
        "Customer Reactivation": [
            "We've missed you - here's 25% off your next order.",
            "A lot has changed. Come back and see what's new.",
            "Your spot is still here. Welcome back.",
        ],
        "Upsell": [
            "You're getting more from {product} than ever - here's how to get even more.",
            "Unlock advanced capabilities built for power users.",
            "Ready for the next tier? Here's what's waiting.",
        ],
        "Cross-sell": [
            "You already love {product}. Here's the perfect companion.",
            "Bundle and save - smarter together.",
            "One account, more value.",
        ],
        "Loyalty": [
            "Members earn more. Join today.",
            "Your loyalty, rewarded.",
            "Status, perks, and points - on us.",
        ],
        "Retention": [
            "Stay with us and get more of what you love.",
            "Here's what's new, just for you.",
            "Thank you for being a customer - here's something special.",
        ],
        "Seasonal Promotion": [
            "Limited time: save big this {season}.",
            "{season} is here - shop the edit.",
            "Our biggest {season} event yet.",
        ],
        "Event Registration": [
            "Save your seat at {event}.",
            "{event}: where the industry connects.",
            "Register now - early bird pricing ends soon.",
        ],
        "App Adoption": [
            "Get more done on the go - download the app.",
            "Your account, in your pocket.",
            "Faster, easier, in-app exclusive perks.",
        ],
        "Renewal": [
            "Renew today and lock in your current rate.",
            "Don't lose access - renew before {date}.",
            "Stay covered. Stay supported.",
        ],
        "Awareness": [
            "Meet {product} - a smarter way to {benefit}.",
            "{product}: built for what's next.",
            "The brand professionals trust.",
        ],
    }
    template = random.choice(templates[ctype])
    product = random.choice(PRODUCT_NAMES.get(industry, ["our product"]))
    season = random.choice(SEASONS)
    event = random.choice(PRODUCT_NAMES["Events"])
    benefit = random.choice(["save time", "reduce risk", "scale faster", "stay compliant",
                              "delight customers", "grow revenue"])
    date = f"{random.choice(['Mar', 'Jun', 'Sep', 'Dec'])} {random.randint(1, 28)}"
    return template.format(product=product, season=season, event=event, benefit=benefit, date=date)


FULL_CHANNELS = [
    "Email", "Paid Search", "Paid Social (Meta)", "Paid Social (LinkedIn)", "Display",
    "Programmatic", "YouTube", "Connected TV", "SMS", "Push Notifications", "In-app",
    "Webinar", "Direct Mail", "OOH", "Radio", "Podcast", "Influencer", "Organic Social",
    "Affiliate", "PR", "Content Syndication", "Account-Based Marketing",
]
VAGUE_CHANNELS = ["social", "digital", "email and ads", "paid media", "online", "performance marketing",
                   "social and email"]


def gen_channels(industry: str, ctype: str, vague: bool) -> str:
    if vague:
        return random.choice(VAGUE_CHANNELS)
    # Base channel mix by industry
    preferred = {
        "B2B SaaS": ["Email", "Paid Social (LinkedIn)", "Paid Search", "Webinar",
                      "Content Syndication", "Account-Based Marketing"],
        "B2C Retail": ["Paid Social (Meta)", "Email", "Display", "Influencer", "OOH",
                        "Connected TV", "SMS"],
        "E-commerce": ["Paid Social (Meta)", "Paid Search", "Email", "Display", "Affiliate",
                        "SMS", "Push Notifications"],
        "Banking": ["Direct Mail", "Email", "Paid Search", "Display", "Programmatic"],
        "Fintech": ["Paid Social (Meta)", "Paid Search", "Email", "Push Notifications",
                     "In-app", "Influencer"],
        "Healthcare": ["Email", "Paid Search", "Display", "Direct Mail", "PR"],
        "Insurance": ["Direct Mail", "Email", "Paid Search", "Display", "Radio"],
        "Education": ["Paid Social (Meta)", "Paid Search", "Email", "YouTube", "Webinar"],
        "Travel": ["Paid Search", "Paid Social (Meta)", "Email", "Display", "Influencer",
                    "Connected TV"],
        "Telecom": ["Paid Search", "Display", "Email", "OOH", "Direct Mail", "SMS"],
        "Consumer Subscription": ["Email", "Paid Social (Meta)", "Push Notifications", "In-app",
                                    "Influencer"],
        "Events": ["Email", "Paid Social (LinkedIn)", "Webinar", "Organic Social", "PR"],
        "Professional Services": ["Email", "Paid Social (LinkedIn)", "Webinar", "Content Syndication",
                                    "PR"],
    }[industry]
    n = random.randint(2, min(5, len(preferred)))
    pick = random.sample(preferred, n)
    return ", ".join(pick)


def gen_budget(industry: str, missing_or_vague: bool, low_quality: bool) -> str:
    if missing_or_vague:
        return random.choice([
            "Not specified", "TBD", "Limited budget", "Per-channel budget missing",
            "Pending finance approval", "To be confirmed by CMO",
            "Use available Q-end funds",
        ])
    low, high = BUDGET_RANGES[industry]
    amount = random.randint(low, high)
    # Round to a marketing-friendly number
    if amount > 100_000:
        amount = (amount // 5_000) * 5_000
    elif amount > 20_000:
        amount = (amount // 1_000) * 1_000
    else:
        amount = (amount // 500) * 500
    suffix = random.choice(["", " (media only)", " total", " incl. agency fees",
                             " excl. production", ""])
    return f"{fmt_money(amount)}{suffix}"


def gen_timeline(vague: bool) -> str:
    if vague:
        return random.choice([
            "next quarter", "before holiday season", "Q3 launch", "ASAP", "soon",
            "this year", "by end of fiscal year", "summer push", "post-launch window",
            "TBD", "rolling",
        ])
    start_month = random.choice(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                                   "Sep", "Oct", "Nov"])
    start_day = random.randint(1, 28)
    duration_weeks = random.choice([2, 3, 4, 6, 8, 10, 12])
    year = random.choice(["2026", "2026", "2027"])
    return f"{start_month} {start_day}, {year} - {duration_weeks} week flight"


def gen_success_metrics(industry: str, ctype: str, incomplete: bool) -> str:
    pct_low, pct_high = CONVERSION_RANGES[industry]
    baseline = round(random.uniform(pct_low * 0.4, pct_low * 1.0), 1)
    target = round(random.uniform(pct_low, pct_high), 1)
    window = random.choice(["over 30 days", "over 60 days", "over the campaign flight",
                             "by end of quarter", "within 90 days post-launch"])
    cpa = random.randint(15, 350)
    roas = round(random.uniform(2.0, 8.0), 1)

    full_templates = {
        "Product Launch": [
            f"Adoption rate: baseline {baseline}%, target {target}%, measured {window}.",
            f"New sign-ups: target {random.randint(500, 20000):,} {window}; CPA <= ${cpa}.",
        ],
        "Trial-to-Paid Conversion": [
            f"Trial-to-paid conversion: baseline {baseline}%, target {target}%, {window}.",
        ],
        "Lead Generation": [
            f"MQLs: target {random.randint(500, 10000):,}, CPL <= ${cpa}, measured {window}.",
            f"SQL conversion: baseline {baseline}%, target {target}%, {window}.",
        ],
        "Customer Reactivation": [
            f"Reactivation rate: baseline {baseline}%, target {target}%, {window}.",
        ],
        "Upsell": [
            f"ARPU lift: baseline ${random.randint(20, 200)}, target +{target}%, {window}.",
        ],
        "Cross-sell": [
            f"Attach rate: baseline {baseline}%, target {target}%, {window}.",
        ],
        "Loyalty": [
            f"Program enrollment: target +{target}% vs. baseline, {window}.",
        ],
        "Retention": [
            f"Monthly churn: baseline {baseline}%, target {round(baseline * 0.6, 1)}%, {window}.",
        ],
        "Seasonal Promotion": [
            f"Incremental revenue: target ${random.randint(50_000, 2_000_000):,}, ROAS >= {roas}, {window}.",
        ],
        "Event Registration": [
            f"Registrations: target {random.randint(500, 15_000):,}; show-up rate >= {random.randint(40, 75)}%; {window}.",
        ],
        "App Adoption": [
            f"Installs: target {random.randint(5_000, 250_000):,}; D7 retention >= {random.randint(20, 45)}%; {window}.",
        ],
        "Renewal": [
            f"Gross renewal rate: baseline {round(80 + baseline, 1)}%, target {round(85 + target / 3, 1)}%, {window}.",
        ],
        "Awareness": [
            f"Aided awareness lift: baseline {random.randint(20, 50)}%, target +{random.randint(3, 12)} pts, {window}.",
        ],
    }
    incomplete_templates = [
        f"Conversion rate target {target}%",  # missing baseline + window
        f"Improve CTR vs. last campaign",  # missing all numbers
        f"Hit {random.randint(500, 10000):,} sign-ups",  # missing window
        f"Lift engagement",  # fully vague
        f"ROAS target {roas}",  # missing window
        f"Reduce CPA",  # missing baseline + target
        f"Baseline {baseline}%, improve over time",  # missing target + window
    ]
    if incomplete:
        return random.choice(incomplete_templates)
    return random.choice(full_templates[ctype])


COMPLIANCE_BY_INDUSTRY = {
    "Healthcare": [
        "HIPAA compliance required; no PHI in creative or targeting data.",
        "All medical claims must be reviewed by Medical Legal Review (MLR) before launch.",
        "FDA fair-balance language required for any branded therapy mention.",
    ],
    "Banking": [
        "All offers must include APR/APY disclosures and FDIC member language.",
        "Reg Z and UDAAP review required prior to launch.",
        "No targeting on protected class attributes (ECOA/Reg B).",
    ],
    "Fintech": [
        "Required disclosures on rates, fees, and partner bank relationship.",
        "All claims must be reviewed by Compliance and Legal before publication.",
        "No misleading earnings or returns language.",
    ],
    "Insurance": [
        "State-specific disclosures required; suppress non-licensed states.",
        "All quotes must include 'subject to underwriting' language.",
        "No guaranteed-acceptance language without policy substantiation.",
    ],
    "Education": [
        "FERPA-aligned data handling; no student PII in third-party platforms.",
        "Title IV compliance review required for any financial-aid messaging.",
        "Outcome claims (placement, salary) must include cohort source citation.",
    ],
}

GDPR_NOTES = [
    "EU audiences: GDPR consent required; honor cookie banner state and DSAR within 30 days.",
    "DACH market: double opt-in for email; no purchased lists.",
    "UK/EU: lawful basis must be documented; suppress contacts without marketing consent.",
]

CANNIBALIZATION_NOTES = {
    "B2C Retail": [
        "Avoid overlap with concurrent storewide promo; suppress full-price loyalists from discount creative.",
        "Do not stack with member 20% offer; cap discount at 30% MSRP.",
        "Margin floor 35%; exclude clearance SKUs from promotion.",
    ],
    "E-commerce": [
        "Suppress recent purchasers (last 14 days) to prevent post-purchase discount cannibalization.",
        "Do not run alongside sitewide free-shipping promo without finance sign-off.",
        "Exclude high-AOV segments from blanket discounts.",
    ],
    "Loyalty": [
        "Coordinate with concurrent acquisition offers to avoid loyalty member dilution.",
        "Members-only pricing must remain materially better than public promo.",
    ],
    "Travel": [
        "Avoid stacking with seasonal sale; cap combined discount at agreed max.",
        "Suppress recently booked travelers to avoid post-purchase regret refunds.",
    ],
}

BRAND_NOTES = [
    "Adhere to brand voice guidelines v3.2; primary palette only.",
    "No competitor logos or comparison claims in paid creative.",
    "Use approved product photography only; lifestyle imagery requires brand review.",
    "Tone: confident, helpful, never alarmist.",
    "All copy must use inclusive language per brand DEI guidelines.",
    "Localization required for non-English markets; transcreation, not direct translation.",
    "CEO and executive quotes require Comms approval.",
    "Do not reference unannounced roadmap items.",
    "Hero creative must feature flagship product, not bundled SKUs.",
    "Maintain accessibility: WCAG 2.1 AA for all digital assets.",
]

CREATIVE_RESTRICTIONS = [
    "No animated GIFs in email; static hero only.",
    "Video assets capped at 15s for social, 30s for CTV.",
    "Mobile-first creative required; desktop is secondary.",
    "Subject lines under 50 characters; no emojis in B2B sends.",
    "Landing page must load under 2.5s on 4G.",
]


def gen_constraints(industry: str, ctype: str, region_eu: bool, low_quality: bool) -> str:
    parts = []
    # Industry-specific compliance
    if industry in COMPLIANCE_BY_INDUSTRY:
        parts.append(random.choice(COMPLIANCE_BY_INDUSTRY[industry]))
    # GDPR for EU exposure
    if region_eu or industry in ("Healthcare", "Banking", "Fintech", "Insurance", "Education") and random.random() < 0.4:
        if random.random() < 0.6:
            parts.append(random.choice(GDPR_NOTES))
    # Cannibalization for retail / e-com / loyalty / promo
    if (industry in ("B2C Retail", "E-commerce", "Travel")
            or ctype in ("Loyalty", "Seasonal Promotion", "Customer Reactivation")):
        if random.random() < 0.7:
            key = "Loyalty" if ctype == "Loyalty" else industry
            pool = CANNIBALIZATION_NOTES.get(key) or CANNIBALIZATION_NOTES.get("E-commerce")
            parts.append(random.choice(pool))
    # Brand + creative notes
    if random.random() < 0.7:
        parts.append(random.choice(BRAND_NOTES))
    if random.random() < 0.4:
        parts.append(random.choice(CREATIVE_RESTRICTIONS))

    if low_quality and random.random() < 0.5:
        # Sparse / vague constraints
        return random.choice([
            "Follow brand guidelines.",
            "Standard legal review.",
            "TBD with Legal.",
            "No major restrictions noted.",
            "",
        ])
    if not parts:
        parts.append(random.choice(BRAND_NOTES))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Row-quality orchestration
# ---------------------------------------------------------------------------

def choose_quality_tier() -> str:
    # 30% high, 45% medium, 25% low (within requested ranges)
    r = random.random()
    if r < 0.30:
        return "high"
    if r < 0.75:
        return "medium"
    return "low"


def make_row(used_names: set) -> list[str]:
    industry, ctype = pick_industry_and_type()
    quality = choose_quality_tier()

    # Probability flags driven by quality tier + global distribution targets
    # Targets (global): vague_budget 25%, vague_audience 20%, vague_channels 25%,
    # vague_timeline 17%, aggressive 10%, incomplete metrics ~ correlates with quality
    if quality == "high":
        p_vague_budget = 0.05
        p_vague_audience = 0.05
        p_vague_channels = 0.05
        p_vague_timeline = 0.05
        p_incomplete_metrics = 0.05
        p_low_quality_text = 0.0
    elif quality == "medium":
        p_vague_budget = 0.30
        p_vague_audience = 0.20
        p_vague_channels = 0.30
        p_vague_timeline = 0.18
        p_incomplete_metrics = 0.35
        p_low_quality_text = 0.0
    else:  # low
        p_vague_budget = 0.55
        p_vague_audience = 0.50
        p_vague_channels = 0.55
        p_vague_timeline = 0.40
        p_incomplete_metrics = 0.70
        p_low_quality_text = 1.0

    aggressive = random.random() < 0.10  # ~10% rows with overly aggressive goals
    vague_audience = random.random() < p_vague_audience
    vague_channels = random.random() < p_vague_channels
    vague_budget = random.random() < p_vague_budget
    vague_timeline = random.random() < p_vague_timeline
    incomplete_metrics = random.random() < p_incomplete_metrics
    low_quality_text = p_low_quality_text > 0 and random.random() < 0.6

    # EU exposure ~ 30%
    region_eu = random.random() < 0.30

    name = make_campaign_name(industry, ctype, used_names)
    obj = gen_business_objective(industry, ctype, aggressive, low_quality_text)
    audience = gen_target_audience(industry, vague_audience)
    if region_eu and not vague_audience:
        audience = audience + " (EU coverage)"
    msg = gen_key_message(industry, ctype)
    channels = gen_channels(industry, ctype, vague_channels)
    budget = gen_budget(industry, vague_budget, low_quality_text)
    timeline = gen_timeline(vague_timeline)
    metrics = gen_success_metrics(industry, ctype, incomplete_metrics)
    constraints = gen_constraints(industry, ctype, region_eu, low_quality_text)

    return [name, obj, audience, msg, channels, budget, timeline, metrics, constraints]


def main() -> None:
    used_names: set = set()
    rows = []
    for _ in range(TOTAL_ROWS):
        rows.append(make_row(used_names))

    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
