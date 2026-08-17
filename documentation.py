"""
Corpus de documentación de ejemplo — contenido expandido para testeo de bases de datos vectoriales.
Diseñado para generar >350 embeddings con alta variabilidad semántica en 7 áreas de producto.
TANDA 1: Productos 1 al 4 expandidos masivamente.
"""

DOCUMENTATION = [
    # ------------------------------------------------------------------
    # PRODUCTO 1: PAYMENTS (Original + Expansiones Profundas)
    # ------------------------------------------------------------------
    {
        "product": "Payments",
        "category": "Accept a payment",
        "article_id": "accept-a-payment",
        "article_title": "Accept a payment",
        "article_path": "/docs/payments/accept-a-payment",
        "sections": [
            {
                "section": "Set up Stripe",
                "section_anchor": "set-up-stripe",
                "subsections": [
                    {
                        "subsection": "Server-side",
                        "subsection_anchor": "server-side",
                        "text": (
                            "Install the server-side library for your language (available for Node.js, Python, Ruby, PHP, Java, and Go) "
                            "and initialize it with your secret API key. On your backend server, you must create a PaymentIntent as soon "
                            "as you know the order amount, currency, and the customer's intent to check out. Setting up a PaymentIntent "
                            "before rendering the payment form lets you track the entire lifecycle of a customer's checkout flow, "
                            "including any failed payment attempts, network drop-offs, and fraud blocks. Store the PaymentIntent id "
                            "alongside the internal order record in your own relational database so you can reconcile it later. "
                            "Security warning: Never trust the amount or currency coming directly from the client application; always "
                            "recompute it on the server using your own secure pricing logic before creating the PaymentIntent. "
                            "Otherwise, a malicious client could tamper with the price payload, resulting in a completed order for a "
                            "fraction of the cost. When creating the PaymentIntent, consider passing an idempotency key to prevent "
                            "double charges in case of network timeouts, and attach metadata relevant to the transaction to assist "
                            "your customer support team later."
                        ),
                    },
                    {
                        "subsection": "Client-side",
                        "subsection_anchor": "client-side",
                        "text": (
                            "On the client application, retrieve the client secret returned by your backend when you created the "
                            "PaymentIntent. Use this secure string to initialize the payment element and confirm the payment securely. "
                            "If the payment requires additional authentication, such as 3D Secure (Strong Customer Authentication - SCA), "
                            "the client SDK automatically displays the necessary modal UI and handles the bank redirect back to "
                            "your return_url. Listen for the confirmation promise to resolve before showing a success state to the "
                            "customer. It is crucial to note that some payment methods, like SEPA or ACH, settle asynchronously, "
                            "meaning the immediate status might be 'processing' rather than 'succeeded'. You must instruct the UI to "
                            "handle 'processing' states gracefully, informing the customer that their order is confirmed but pending "
                            "final fund capture. Do not use the client-side success callback to fulfill the order; rely exclusively "
                            "on backend webhooks for fulfillment."
                        ),
                    },
                ],
                "text": None,
            },
            {
                "section": "Handle post-payment events",
                "section_anchor": "handle-post-payment-events",
                "subsections": [],
                "text": (
                    "Set up a webhook endpoint on your server to receive real-time HTTP POST events about the lifecycle of a payment, "
                    "such as payment_intent.succeeded, payment_intent.payment_failed, or payment_intent.requires_action. Webhooks are the "
                    "only recommended way to keep your own database records perfectly in sync, since some payment methods confirm "
                    "asynchronously and the client redirect alone is not a reliable signal of success (e.g., the user closes their browser "
                    "before the redirect finishes).\n\n"
                    "Always verify the webhook cryptographic signature using your endpoint's dedicated signing secret before "
                    "trusting the payload. Process events idempotently: due to the nature of distributed systems, a webhook endpoint may "
                    "receive the exact same event more than once. Use the unique event id to detect and skip processing duplicates. "
                    "Acknowledge receipt by returning an HTTP 2xx response (like 200 OK) as quickly as possible. If your server takes "
                    "longer than 3 seconds to respond, the system will assume a timeout and schedule a retry. Push any slow or blocking "
                    "work—like sending a confirmation email, updating a CRM, or communicating with inventory suppliers—into an asynchronous "
                    "background job queue (like Celery, Sidekiq, or SQS) instead of running it synchronously inside the webhook handler."
                ),
            },
        ],
    },
    {
        "product": "Payments",
        "category": "Disputes",
        "article_id": "disputes",
        "article_title": "Disputes overview and management",
        "article_path": "/docs/disputes",
        "sections": [
            {
                "section": "Dispute lifecycle",
                "section_anchor": "dispute-lifecycle",
                "subsections": [],
                "text": (
                    "A dispute (also known as a chargeback) happens when a cardholder questions a transaction directly with their card issuing bank "
                    "instead of contacting your business for a refund. The dispute moves through a strictly regulated lifecycle. First, it "
                    "opens with a specific reason code supplied by the card network (e.g., Visa or Mastercard), enters a 'needs_response' "
                    "state while evidence can be submitted, and eventually closes as either 'won' or 'lost' based on the issuer's verdict. "
                    "The disputed funds, plus a network dispute fee (usually $15 or €15), are immediately deducted from your available "
                    "balance the moment the dispute is opened, regardless of the eventual outcome. Some dispute reasons, such as 'fraudulent', "
                    "are historically difficult to win without strict proof like 3D Secure authentication. Others, like 'product_not_received', "
                    "depend heavily on your ability to provide tracking numbers, shipping logs, and delivery confirmation signatures. "
                    "During the lifecycle, the dispute object in the API emits various webhooks such as charge.dispute.created and "
                    "charge.dispute.closed to help you automate your internal accounting."
                ),
            },
            {
                "section": "Respond to a dispute",
                "section_anchor": "respond-to-a-dispute",
                "subsections": [],
                "text": (
                    "You can challenge a dispute from your dashboard or programmatically through the API by submitting structured "
                    "evidence before the strict network deadline shown on the dispute object. The evidence required varies drastically "
                    "based on the reason code. For 'canceled_subscription', you must provide logs showing the cancellation policy and "
                    "customer usage logs. For 'unrecognized', IP addresses, billing addresses, and matching CVC/AVS checks are vital. "
                    "Submit proof of delivery, signed receipts, email correspondence with the customer, and a copy of your refund policy "
                    "agreed to at the time of purchase. Submitting evidence after the deadline is mechanically impossible, as the card "
                    "networks lock the case. Therefore, track the `evidence_details.due_by` timestamp diligently and alert your support "
                    "team at least 48 hours before it passes. If you review the dispute and determine it is valid (e.g., actual friendly fraud), "
                    "you can choose to 'accept' the dispute. This immediately resolves the case against you, waving your right to submit evidence, "
                    "but it prevents further administrative time wasting."
                ),
            },
        ],
    },
    {
        "product": "Payments",
        "category": "Refunds",
        "article_id": "refunds-overview",
        "article_title": "Issuing and Managing Refunds",
        "article_path": "/docs/payments/refunds",
        "sections": [
            {
                "section": "Full vs Partial Refunds",
                "section_anchor": "full-vs-partial",
                "subsections": [],
                "text": (
                    "You can issue a full or partial refund for any successfully captured charge. Partial refunds allow you to return a "
                    "specific nominal amount to the customer, which is particularly useful for e-commerce stores when returning a single item "
                    "from a larger multi-item order, or for SaaS companies applying a pro-rated credit. You can perform multiple partial "
                    "refunds on a single charge until the entire captured amount is depleted. The original payment method dictates how long "
                    "the refund takes to appear on the customer's bank statement—typically 5 to 10 business days for credit cards. "
                    "Crucially, the processing fees you originally paid to accept the transaction are not returned when you issue a refund, "
                    "meaning refunds operate at a net loss equal to the processing fee."
                ),
            },
            {
                "section": "Refund Reason Codes",
                "section_anchor": "reason-codes",
                "subsections": [],
                "text": (
                    "When executing a refund via the API, you can optionally provide a `reason` parameter. The accepted ENUM values are "
                    "`duplicate`, `fraudulent`, or `requested_by_customer`. Providing accurate reason codes is more than just an administrative "
                    "nicety; it helps your machine-learning fraud models learn from false positives and improves your overall risk profile "
                    "with the card networks. For example, explicitly marking a refund as `fraudulent` immediately refunds the customer and "
                    "adds the associated email and IP to your internal blocklist, actively preventing the fraudster from testing more cards "
                    "on your infrastructure."
                ),
            },
            {
                "section": "Failed and Asynchronous Refunds",
                "section_anchor": "failed-refunds",
                "subsections": [],
                "text": (
                    "A refund can unexpectedly fail if the customer's bank or card issuer declines it. This typically occurs because the "
                    "customer's bank account is closed, frozen, or the physical card was canceled. In these edge cases, the refund object "
                    "transitions to a `failed` state and emits a `charge.refund.updated` webhook, which your reconciliation job should treat "
                    "as a signal to stop expecting the original refund to complete and instead surface the failure to your support team. "
                    "You will need to contact the customer to arrange an alternative payout method, such as a direct bank wire or store credit, "
                    "since retrying the identical refund against the same failed destination will simply fail again. Additionally, some bank "
                    "debit methods like SEPA Direct Debit, Sofort, or Boleto never confirm a refund synchronously at all: the API immediately "
                    "returns a refund object in a `pending` status regardless of the eventual outcome, and your accounting ledger must treat "
                    "`pending` refunds as unresolved liabilities until a terminal webhook arrives, which can take several banking business days "
                    "depending on the clearing house involved."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 2: BILLING (Suscripciones, Facturas, etc.)
    # ------------------------------------------------------------------
    {
        "product": "Billing",
        "category": "Subscriptions",
        "article_id": "subscription-lifecycle",
        "article_title": "Advanced Subscription Lifecycle",
        "article_path": "/docs/billing/subscriptions/lifecycle",
        "sections": [
            {
                "section": "Creating and Provisioning Subscriptions",
                "section_anchor": "creating",
                "subsections": [],
                "text": (
                    "A subscription connects a Customer object to one or more Price objects, establishing a recurring billing schedule. "
                    "Upon creation via the API, an initial Invoice is automatically generated. If the invoice requires immediate payment, "
                    "the subscription status remains `incomplete` until the payment successfully clears the network. It is a critical best "
                    "practice to only provision access to your SaaS application or service when the subscription transitions to `active`. "
                    "You can also configure trial periods by passing the `trial_end` parameter. During a trial, the subscription is active, "
                    "but invoices generated are for $0.00 until the trial elapses. Capturing a payment method upfront for a trial is optional "
                    "but recommended to reduce friction at trial conversion."
                ),
            },
            {
                "section": "Active Status and Billing Cycles",
                "section_anchor": "active",
                "subsections": [],
                "text": (
                    "Once the initial payment succeeds, the subscription becomes `active`. Background workers operating on distributed cron jobs "
                    "will automatically generate new draft invoices a few hours before the end of each billing cycle (e.g., monthly, quarterly, "
                    "or annually). When the cycle officially ends, the invoice is finalized and the system attempts to charge the default "
                    "payment method attached to the customer or the subscription. If you need to add one-off charges, such as setup fees or "
                    "overage usage costs, you can add InvoiceItems to the customer's account; these will be bundled into the next recurring invoice."
                ),
            },
            {
                "section": "Pausing and Resuming",
                "section_anchor": "pausing",
                "subsections": [],
                "text": (
                    "To prevent churn, you can allow customers to temporarily pause a subscription instead of canceling it. Setting the "
                    "`pause_collection` parameter retains the customer's subscription record in the database, but no new invoices are generated "
                    "and no automatic collections are attempted. You can specify whether the pause takes effect immediately or at the end of "
                    "the current paid period. You can also configure a `resumes_at` timestamp if you want the system to automatically reactivate "
                    "the subscription after a set duration, such as a 3-month sabbatical."
                ),
            },
            {
                "section": "Complex Cancellations",
                "section_anchor": "canceling",
                "subsections": [],
                "text": (
                    "Cancellations can be executed immediately or scheduled for the end of the current billing period using `cancel_at_period_end`. "
                    "If canceled immediately, the API allows you to issue a prorated refund for the unused time by passing the `prorate: true` flag. "
                    "Once a subscription is fully canceled, its state changes to `canceled` and it cannot be reactivated under any circumstances; "
                    "a brand new subscription object must be created. Track the `customer.subscription.deleted` webhook to automatically revoke "
                    "user access in your application database."
                ),
            },
        ],
    },
    {
        "product": "Billing",
        "category": "Invoices",
        "article_id": "invoice-management",
        "article_title": "Managing Lifecycle of Invoices",
        "article_path": "/docs/billing/invoices",
        "sections": [
            {
                "section": "Drafts and Finalization",
                "section_anchor": "drafts-finalization",
                "subsections": [],
                "text": (
                    "Before an invoice is finalized, it exists in a `draft` state. During this flexible period, which typically lasts about an hour "
                    "before automatic collection, you can dynamically add or remove invoice items, apply flat-rate or percentage coupons, or adjust "
                    "tax rates via the API. Draft invoices cannot be paid, do not possess a final PDF, and are not visible to customers on the portal. "
                    "When an invoice is finalized, its state is frozen cryptographically, a sequential and unique invoice number (e.g., INV-0001) is "
                    "assigned for accounting compliance, and the PDF is generated. The system triggers the `invoice.finalized` webhook, indicating "
                    "that the invoice has officially become an account receivable in your ledger and is ready for payment collection."
                ),
            },
            {
                "section": "Voiding vs Deleting",
                "section_anchor": "voiding",
                "subsections": [],
                "text": (
                    "Accounting principles dictate strict rules regarding invoice modification. If a finalized invoice contains an error (such as incorrect "
                    "billing details or wrong tax calculations), it cannot be deleted from the system. Instead, it must be `voided`. Voiding an invoice "
                    "cancels it entirely, dropping its balance to zero and updating the PDF to clearly display 'VOID'. This ensures your accounting, "
                    "revenue recognition reports, and audit trails remain perfectly accurate. Draft invoices, however, can be deleted completely since "
                    "they were never legally issued."
                ),
            },
            {
                "section": "Credit Notes",
                "section_anchor": "credit-notes",
                "subsections": [],
                "text": (
                    "Credit notes are vital financial instruments used to refund a portion of a finalized invoice or adjust the total amount owed downward "
                    "after the invoice has been issued. They are strictly compliant with international accounting standards (like GAAP and IFRS). Issuing "
                    "a credit note generates proper documentation for both the merchant's ledger and the customer's AP department. Credit notes can be "
                    "applied to open invoices to reduce the balance due, or refunded directly to the customer's original payment method if the invoice "
                    "was already fully paid."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 3: CONNECT (Marketplaces, Cuentas, Payouts)
    # ------------------------------------------------------------------
    {
        "product": "Connect",
        "category": "Account Types",
        "article_id": "account-types",
        "article_title": "Choosing the right Connect Account Type",
        "article_path": "/docs/connect/account-types",
        "sections": [
            {
                "section": "Standard Accounts",
                "section_anchor": "standard",
                "subsections": [],
                "text": (
                    "Standard accounts are best suited for software platforms that want their users to have a direct, independent relationship with the "
                    "payment gateway. In this model, the platform merely facilitates the OAuth connection via Connect. The connected user logs directly "
                    "into their own fully-featured dashboard provided by the payment processor. Crucially, the connected user handles their own disputes, "
                    "issues their own refunds, and configures their own payout schedules. This shifts all fraud liability and compliance burdens away "
                    "from the platform. Examples include e-commerce website builders like Shopify or Wix."
                ),
            },
            {
                "section": "Custom and Express Accounts",
                "section_anchor": "custom-express",
                "subsections": [],
                "text": (
                    "Custom accounts are completely white-labeled through APIs. The connected user never sees the payment provider's brand. Your platform "
                    "is fully responsible for building the frontend UI to collect identity data, bank accounts, and managing the dashboard experience. "
                    "Because of this control, the platform bears complete liability for negative balances and fraudulent disputes. Express accounts offer "
                    "a hybrid middle-ground: the platform controls the customer experience, but relies on a pre-built, hosted onboarding and dashboard "
                    "component to manage complex compliance, KYC tracking, and tax form (1099-K) generation. Platform liability remains the same as Custom."
                ),
            },
        ],
    },
    {
        "product": "Connect",
        "category": "Routing",
        "article_id": "routing-funds",
        "article_title": "Complex Fund Routing and Splits",
        "article_path": "/docs/connect/routing",
        "sections": [
            {
                "section": "Direct and Destination Charges",
                "section_anchor": "direct-destination",
                "subsections": [],
                "text": (
                    "Fund routing determines how money flows between the end customer, your platform, and the connected account. Direct charges are created "
                    "directly on the connected account. The customer's credit card statement shows the connected account's business name. The platform "
                    "can optionally collect an `application_fee_amount`. Destination charges are the opposite: the payment is processed on the platform's "
                    "main account (the platform name appears on the statement), and immediately transfers a portion of the funds to a specified connected "
                    "account via the `transfer_data[destination]` parameter. The platform covers network processing fees automatically."
                ),
            },
            {
                "section": "Separate Charges and Transfers (SCT)",
                "section_anchor": "sct",
                "subsections": [],
                "text": (
                    "Separate Charges and Transfers (SCT) method completely decouples the customer payment from the payout to the provider. This is vital "
                    "for complex marketplaces (like food delivery or booking platforms). A customer might pay $100 on Monday, but the platform splits and "
                    "transfers $40 to a driver account, $30 to a restaurant account, and holds $30 as margin, executing these transfers on Wednesday only "
                    "after the service is fulfilled. This method requires robust internal balance tracking and careful management of `source_transaction` "
                    "links to handle refunds gracefully without draining the platform's reserve balances."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 4: RADAR / FRAUD (Completado y expandido)
    # ------------------------------------------------------------------
    {
        "product": "Radar",
        "category": "Fraud Prevention",
        "article_id": "radar-overview",
        "article_title": "Machine Learning and Fraud Prevention",
        "article_path": "/docs/radar/overview",
        "sections": [
            {
                "section": "Risk Scores and Machine Learning",
                "section_anchor": "risk-scores",
                "subsections": [],
                "text": (
                    "Radar is an integrated fraud prevention tool powered by adaptive machine learning. It evaluates every transaction across the entire "
                    "global network of millions of businesses in milliseconds. Radar assigns a risk score between 0 and 99 to each PaymentIntent. "
                    "A score above a certain threshold (typically 75) is classified as 'elevated risk' and will be automatically blocked or pushed to a "
                    "manual review queue. The machine learning models analyze thousands of signals, including IP address velocity, mismatching billing "
                    "and shipping addresses, proxy detection, behavioral biometrics (like mouse movement speed), and the historical fraud rate of the "
                    "specific card BIN across the global network."
                ),
            },
            {
                "section": "Custom Rules Engine",
                "section_anchor": "rules-engine",
                "subsections": [],
                "text": (
                    "While the ML models are powerful out-of-the-box, businesses often need tailored logic. The Radar Rules Engine allows you to write "
                    "custom rules using a specialized syntax. For example, you can write a rule like: `Block if :amount_in_usd: > 1000 and "
                    ":risk_level: = 'elevated' and :is_anonymous_ip: = 'true'`. You can create block rules, review rules, or allow rules. "
                    "Allow rules always override block rules, which is highly useful for ensuring VIP customers or internal testing cards are never "
                    "accidentally declined by the ML model. You can also utilize velocity rules to stop card testing attacks, such as blocking "
                    "a single IP that attempts more than 5 different credit cards within a 10-minute window."
                ),
            },
            {
                "section": "3D Secure (SCA)",
                "section_anchor": "3d-secure",
                "subsections": [],
                "text": (
                    "3D Secure is a protocol designed to add an extra layer of security for online credit and debit card transactions. In Europe, "
                    "this is mandated under Strong Customer Authentication (SCA) regulations. When Radar determines a transaction is high risk but not "
                    "quite risky enough to block outright, it can dynamically trigger a rule asking the bank to authenticate the user via 3D Secure. "
                    "The customer is prompted to complete an action, like entering a code sent via SMS or authenticating in their mobile banking app. "
                    "Successfully completing 3D Secure shifts the liability for fraudulent chargebacks from your business directly to the card issuer."
                ),
            },
        ],
    },
    {
        "product": "Terminal",
        "category": "Hardware Lifecycle",
        "article_id": "reader-management",
        "article_title": "Reader Management and Pairing",
        "article_path": "/docs/terminal/readers",
        "sections": [
            {
                "section": "Device Provisioning and Pairing",
                "section_anchor": "pairing",
                "subsections": [],
                "text": (
                    "Stripe Terminal enables you to build in-person checkout flows into your web or mobile applications. The process begins "
                    "with provisioning hardware. Readers, such as the BBPOS WisePad 3 or the Stripe Reader S700, must be registered to a "
                    "specific Location object in your account to ensure accurate localized settings and tax rates. To pair a reader to your "
                    "Point of Sale (POS) application, you use the Terminal SDK (available for iOS, Android, and React Native) or the "
                    "server-driven Terminal API for smart readers. The SDK connects to local devices via Bluetooth Low Energy (BLE) or "
                    "Local Area Network (LAN). In a development environment, you can bypass physical hardware by utilizing the simulated "
                    "reader functionality within the SDK, which allows you to programmatically trigger successful reads, dip failures, "
                    "or contactless NFC declines to thoroughly test your error handling."
                ),
            },
            {
                "section": "Offline Mode and Fallbacks",
                "section_anchor": "offline-mode",
                "subsections": [],
                "text": (
                    "Network instability is a reality for physical retail environments. Terminal SDKs support an Offline Mode feature, "
                    "allowing you to continue accepting payments even when your POS device loses its internet connection. When offline, "
                    "the SDK securely encrypts and stores the payment details on the local device storage. Once connectivity is restored, "
                    "a background process automatically forwards the stored payloads to the API for authorization (Store and Forward). "
                    "However, offline transactions inherently carry higher risk, as live balance checks and backend fraud rules cannot be "
                    "run in real-time. You must configure strict risk thresholds, such as a maximum transaction amount (e.g., $50) and a "
                    "maximum duration for offline operations (e.g., 24 hours), after which the reader will force-decline transactions "
                    "until it synchronizes with the network."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 6: TAX (Impuestos Automatizados)
    # ------------------------------------------------------------------
    {
        "product": "Tax",
        "category": "Compliance",
        "article_id": "tax-calculations",
        "article_title": "Automated Tax Calculation and Nexus",
        "article_path": "/docs/tax/calculations",
        "sections": [
            {
                "section": "Economic Nexus and Thresholds",
                "section_anchor": "nexus",
                "subsections": [],
                "text": (
                    "Stripe Tax monitors your transactions continuously to determine where you have tax obligations, a concept known as "
                    "economic nexus. As your sales volume or transaction count grows in specific jurisdictions (states in the US, or "
                    "countries in the EU), you may cross regulatory thresholds that legally require you to register and collect taxes. "
                    "The API exposes a `/v1/tax/registrations` endpoint that allows you to programmatically define where you are currently "
                    "registered. It is vital to keep this updated; Stripe Tax will not append tax amounts to a checkout session unless an "
                    "active registration exists for the buyer's jurisdiction. The system uses real-time geocoding and address validation "
                    "to pinpoint the exact district-level tax rates, overriding standard zip-code-based averages which are notoriously "
                    "inaccurate."
                ),
            },
            {
                "section": "Tax Codes and Exemptions",
                "section_anchor": "tax-codes",
                "subsections": [],
                "text": (
                    "Not all products are taxed equally. Software as a Service (SaaS), digital goods, physical apparel, and food items "
                    "have distinct tax treatments depending on local laws. You must assign a highly specific `tax_code` (e.g., txcd_10000000 "
                    "for general tangible goods) to your Product objects. Furthermore, handling Business-to-Business (B2B) transactions "
                    "requires specialized logic. In Europe, if a buyer provides a valid VAT ID, the transaction may be subject to the "
                    "reverse charge mechanism, dropping the effective tax rate to 0%. The API includes a `customer_tax_id` validation "
                    "service that checks the provided VAT or EIN against government databases (like VIES in Europe) in real-time before "
                    "applying exemptions."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 7: ISSUING (Emisión de Tarjetas)
    # ------------------------------------------------------------------
    {
        "product": "Issuing",
        "category": "Card Lifecycle",
        "article_id": "card-management",
        "article_title": "Card Creation and Authorization Controls",
        "article_path": "/docs/issuing/cards",
        "sections": [
            {
                "section": "Virtual vs Physical Cards",
                "section_anchor": "card-types",
                "subsections": [],
                "text": (
                    "The Issuing API empowers your platform to programmatically create virtual and physical credit or debit cards. Virtual "
                    "cards are instantly active upon creation and are ideal for single-use online purchases, expense management, or "
                    "immediate injection into mobile wallets (Apple Pay/Google Pay). Physical cards require interacting with the `/v1/issuing/cards` "
                    "endpoint and providing a valid `shipping` object. You can track the physical fulfillment lifecycle through webhooks "
                    "such as `issuing_card.shipped` and `issuing_card.delivered`. Physical cards arrive inactive to prevent mail interception "
                    "fraud; the cardholder must verify receipt, after which you call the API to transition the status from `inactive` to `active`."
                ),
            },
            {
                "section": "Real-time Authorization Hooks",
                "section_anchor": "auth-controls",
                "subsections": [],
                "text": (
                    "One of the most powerful features of Issuing is synchronous Authorization Controls. When a cardholder attempts a purchase, "
                    "the card network pings the gateway, which then fires a synchronous `issuing_authorization.request` webhook directly to "
                    "your server. Your system has exactly 2 seconds to respond with a 200 OK containing an `approved` or `declined` JSON payload. "
                    "This allows you to implement highly complex, real-time spending logic. You can analyze the `merchant_data.network_id` (MCC), "
                    "rejecting transactions at casinos or liquor stores. You can also implement dynamic spend limits, ensuring an employee "
                    "can only spend up to their approved travel budget. If your server fails to respond within the timeout window, the "
                    "authorization is handled by a fallback rule you define in the dashboard."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 8: DEVELOPER TOOLS & ARCHITECTURE (Bonus para variabilidad)
    # ------------------------------------------------------------------
    {
        "product": "Developer Tools",
        "category": "API Architecture",
        "article_id": "api-versioning",
        "article_title": "API Versioning and Webhook Security",
        "article_path": "/docs/developer/architecture",
        "sections": [
            {
                "section": "API Upgrades and Version Pinning",
                "section_anchor": "versioning",
                "subsections": [],
                "text": (
                    "The API follows a strict date-based versioning scheme (e.g., '2023-10-16'). This ensures backwards compatibility. When you "
                    "make an API request, the system evaluates the version pinned to your account dashboard to determine the shape of the JSON "
                    "response. However, you can explicitly override this on a per-request basis by sending the `Stripe-Version` HTTP header. "
                    "When upgrading API versions, you should thoroughly test the new payload structures in your test mode environment. Webhook "
                    "payloads will also conform to your pinned API version, meaning a version upgrade can cause unexpected key errors in your "
                    "webhook listeners if your deserialization logic is strictly typed."
                ),
            },
            {
                "section": "Webhook Signature Verification",
                "section_anchor": "webhook-security",
                "subsections": [],
                "text": (
                    "Webhook endpoints must be completely publicly accessible over the internet to receive POST requests, making them prime "
                    "targets for malicious actors attempting to simulate successful payments. To guarantee authenticity, every payload is signed "
                    "with an `Stripe-Signature` header containing a timestamp and one or more cryptographic signatures (HMAC SHA-256). Your backend "
                    "must compute the expected signature using the raw HTTP request body (do not parse it to JSON first, as formatting alters the "
                    "byte match) and your endpoint's unique secret. Additionally, verifying the timestamp prevents replay attacks, where a valid "
                    "historical payload is intercepted and re-transmitted. By default, SDK signature verification functions will reject any webhook "
                    "older than 5 minutes."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 9: BILLING (Suscripciones y Facturación Recurrente)
    # ------------------------------------------------------------------
    {
        "product": "Billing",
        "category": "Recurring Revenue",
        "article_id": "invoice-states-and-dunning",
        "article_title": "Invoice State Machine, Dunning, and Metered Usage",
        "article_path": "/docs/billing/subscriptions/dunning-and-usage",
        "sections": [
            {
                "section": "Dunning Retry Schedules and Terminal Outcomes",
                "section_anchor": "dunning-retry-schedules",
                "subsections": [],
                "text": (
                    "When an invoice payment attempt fails due to insufficient funds, an expired card, or a generic decline, the invoice enters "
                    "the 'dunning' process (Smart Retries) instead of failing permanently on the first attempt. Dunning is a configurable schedule "
                    "of automated retry attempts paired with customer-facing email notifications reminding the cardholder to update their payment "
                    "method. By default, the system retries the charge 3 days, 5 days, and 7 days after the initial failure, spacing attempts out "
                    "to catch cases where a temporarily insufficient balance resolves itself or a replacement card arrives. Retry timing is not "
                    "arbitrary: retrying too aggressively increases the odds of the issuing bank flagging the merchant for excessive authorization "
                    "attempts, which can itself lower future approval rates. If every scheduled retry fails, the platform must decide the terminal "
                    "outcome by configuring the subscription's 'dunning behavior' setting to automatically transition to 'canceled', 'unpaid', or "
                    "left indefinitely 'past_due'. Webhooks such as 'invoice.payment_failed' should drive in-app messaging at each retry step, "
                    "while 'customer.subscription.deleted' should drive the final access revocation once the dunning schedule is exhausted."
                ),
            },
            {
                "section": "Proration and Subscription Upgrades",
                "section_anchor": "proration",
                "subsections": [],
                "text": (
                    "When a customer upgrades or downgrades their subscription mid-cycle, the API automatically calculates prorations down to "
                    "the exact second. For example, if a user switches from a $30/month Basic tier to a $90/month Pro tier exactly halfway "
                    "through their billing month, the system generates a credit for the unused 15 days of the Basic tier (-$15) and creates a "
                    "new charge for the 15 days of the Pro tier (+$45). The net amount owed ($30) is immediately appended to an upcoming invoice "
                    "or billed instantly, depending on your 'proration_behavior' setting (which accepts 'create_prorations', 'always_invoice', "
                    "or 'none'). Dealing with prorations requires careful frontend design so that users understand exactly what they are being "
                    "charged for today versus what will appear on their next regular billing cycle."
                ),
            },
            {
                "section": "Usage-Based (Metered) Billing",
                "section_anchor": "metered-billing",
                "subsections": [],
                "text": (
                    "Unlike flat-rate subscriptions, metered billing charges customers based on their actual consumption during the billing cycle, "
                    "such as API requests made, gigabytes of storage used, or emails sent. To implement this, you create a Price object with "
                    "'recurring[usage_type]=metered'. Your backend must then frequently report usage events using the '/v1/subscription_items/{id}/usage_records' "
                    "endpoint. You can configure how the system aggregates these events: 'sum' (total requests), 'last_during_period' (for tracking "
                    "current storage limits), 'last_ever', or 'max'. Because usage records must be timestamped and are immutable once the billing "
                    "period closes, handling delayed telemetry data requires idempotency keys and strict synchronization before the draft invoice "
                    "finalizes."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 10: CONNECT (Marketplaces y Pagos Multi-parte)
    # ------------------------------------------------------------------
    {
        "product": "Connect",
        "category": "Multi-Party Payments",
        "article_id": "account-types-and-onboarding",
        "article_title": "Account Onboarding: Standard, Express, and Custom",
        "article_path": "/docs/connect/onboarding",
        "sections": [
            {
                "section": "Onboarding Flow Selection and KYC Requirements",
                "section_anchor": "onboarding-flow-selection",
                "subsections": [],
                "text": (
                    "Once a platform has selected an account type from the account types overview, it must implement the matching integration "
                    "surface to actually collect KYC information from the seller. For Standard accounts, integration means initiating an OAuth "
                    "authorization request to '/oauth/authorize' and storing the returned 'stripe_user_id' against your internal seller record; "
                    "the platform never touches identity documents directly, since the seller completes verification entirely on the processor's "
                    "own domain. For Express accounts, integration means generating a single-use Account Link via the API and redirecting the "
                    "seller to it; the resulting hosted form collects identity documents, bank details, and business information on the platform's "
                    "behalf, and the platform is notified of completion through the 'account.updated' webhook. For Custom accounts, integration "
                    "is the most involved: the platform submits collected fields like `individual.id_number` or `company.tax_id` directly against "
                    "the Accounts API from its own UI, and must additionally poll or listen for the `requirements.currently_due` array, since a "
                    "connected account's documents can expire and re-trigger verification requirements at any point after initial onboarding "
                    "completes."
                ),
            },
            {
                "section": "Cross-Border Onboarding and Platform Payout Timing",
                "section_anchor": "cross-border-payout-timing",
                "subsections": [],
                "text": (
                    "Onboarding a connected account is only the first step; the platform must also configure how quickly funds reach that account "
                    "once transactions begin flowing (see the fund routing article for how the money itself is split). By default, newly onboarded "
                    "accounts are placed on a rolling payout schedule with an extended first-payout delay, often 7 to 14 days, while Stripe's risk "
                    "systems build a baseline transaction history for the seller. Platforms operating across multiple countries must also account "
                    "for the fact that connected accounts can only be provisioned in countries where Connect is officially supported, and each "
                    "supported country carries its own minimum KYC document set, payout currency restrictions, and minimum payout thresholds. A "
                    "connected account domiciled in a country with weekly bank processing windows, for instance, will receive payouts on a fixed "
                    "weekly cadence regardless of the platform's preferred schedule, so platforms serving a global seller base should surface "
                    "country-specific payout timing directly in their onboarding UI to set accurate expectations."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 11: RADAR (Prevención de Fraude)
    # ------------------------------------------------------------------
    {
        "product": "Radar",
        "category": "Risk Management",
        "article_id": "fraud-prevention",
        "article_title": "Machine Learning and Custom Fraud Rules",
        "article_path": "/docs/radar/rules",
        "sections": [
            {
                "section": "Rule Evaluation Order and Conflict Resolution",
                "section_anchor": "rule-evaluation-order",
                "subsections": [],
                "text": (
                    "Radar is a real-time fraud prevention engine powered by machine learning models trained on data across millions of global "
                    "businesses. Every transaction is evaluated in real-time and assigned a risk score from 0 to 99, using the same scoring model "
                    "described in the Radar overview. Because a single PaymentIntent can match multiple custom rules simultaneously, Radar applies "
                    "a deterministic precedence order rather than evaluating rules in the sequence they were written. Block rules are checked first: "
                    "if any block condition matches, the charge is stopped immediately and no further rules are evaluated. If no block rule fires, "
                    "review rules are checked next, routing the charge to a manual queue without stopping the authorization. Allow rules are "
                    "evaluated last but take absolute precedence over any earlier match, which is why a narrowly scoped allow rule (for example, "
                    "an internal testing card's fingerprint) can safely coexist with a broad block rule without being accidentally caught by it. "
                    "Teams should audit their ruleset periodically, since an overly broad allow rule can silently suppress legitimate ML-driven "
                    "blocks across unrelated transaction types."
                ),
            },
            {
                "section": "Post-Authentication Dispute Handling",
                "section_anchor": "post-authentication-disputes",
                "subsections": [],
                "text": (
                    "Once a transaction has completed the 3D Secure challenge described in the Radar overview and a Liability Shift has occurred, "
                    "the merchant's obligations do not disappear entirely; they change in scope. If the cardholder later files a dispute with "
                    "the reason code 'fraudulent', the presence of a successful 3DS authentication is the single strongest piece of evidence a "
                    "merchant can submit, since the issuer who authenticated the cardholder is now contractually responsible for the loss and will "
                    "typically decline to pursue the chargeback further. However, liability shift only covers the 'fraudulent' reason code: disputes "
                    "filed as 'product_not_received' or 'duplicate' still require the merchant to submit standard delivery or billing evidence "
                    "regardless of whether 3DS ran. You can write custom Radar rules such as 'Request 3D Secure if risk_level = elevated and "
                    "amount > 500' to control which transactions are routed through the additional friction, balancing fraud loss against the "
                    "conversion drop that authentication challenges typically introduce at checkout."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 12: IDENTITY (KYC y Verificación)
    # ------------------------------------------------------------------
    {
        "product": "Identity",
        "category": "Compliance",
        "article_id": "kyc-verification",
        "article_title": "Document and Biometric Verification",
        "article_path": "/docs/identity/verification",
        "sections": [
            {
                "section": "Automated Document Checking",
                "section_anchor": "document-checks",
                "subsections": [],
                "text": (
                    "To comply with Anti-Money Laundering (AML) and Know Your Customer (KYC) laws, the Identity API allows you to programmatically "
                    "verify a user's identity. You create a VerificationSession which provides a secure, hosted URL or native SDK flow where the "
                    "user uploads photos of their government-issued ID (passport, driver's license, or national ID). The system uses computer "
                    "vision to extract the Machine Readable Zone (MRZ), check for holographic tampering, verify the document's expiration date, "
                    "and match the extracted PII (Personally Identifiable Information) against the data provided during account registration."
                ),
            }
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 13: SIGMA (Data Warehouse)
    # ------------------------------------------------------------------
    {
        "product": "Sigma",
        "category": "Data and Analytics",
        "article_id": "sql-reporting",
        "article_title": "Writing SQL Queries for Payment Data",
        "article_path": "/docs/sigma/queries",
        "sections": [
            {
                "section": "ANSI SQL Data Interrogation",
                "section_anchor": "sql-queries",
                "subsections": [],
                "text": (
                    "Sigma provides a fully managed data warehouse containing all of your transactional data, accessible via standard ANSI SQL. "
                    "Instead of pulling paginated data through REST APIs and aggregating it locally, your finance and data teams can write complex "
                    "JOINs directly in the dashboard. For example, you can join the 'charges', 'disputes', and 'customers' tables to generate a "
                    "custom report on chargeback rates by customer cohort over the last 36 months. The data is updated on a daily schedule, making "
                    "it ideal for month-end reconciliation, calculating complex multi-tier commissions, or feeding aggregated risk signals into your "
                    "internal business intelligence tools."
                ),
            }
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 14: TREASURY (BaaS - Banking as a Service)
    # ------------------------------------------------------------------
    {
        "product": "Treasury",
        "category": "Banking as a Service",
        "article_id": "financial-accounts-and-money-movement",
        "article_title": "Financial Accounts, Routing Numbers, and Outbound Transfers",
        "article_path": "/docs/treasury/financial-accounts",
        "sections": [
            {
                "section": "Financial Account Provisioning and Compliance",
                "section_anchor": "account-provisioning",
                "subsections": [],
                "text": (
                    "Stripe Treasury enables platforms to embed financial services directly into their product offerings, effectively operating "
                    "as a Banking-as-a-Service (BaaS) provider. At the core of this system is the FinancialAccount object. Unlike a standard "
                    "Stripe balance, a FinancialAccount acts as a fully functional, FDIC-pass-through insured deposit account held at our "
                    "partner banks (e.g., Evolve Bank & Trust or Goldman Sachs). When you provision a FinancialAccount for a connected "
                    "Custom account, the API automatically generates standard banking credentials, including a unique routing number and "
                    "account number. This allows the connected account to receive funds from external sources via ACH, wire transfers, or "
                    "standard payroll direct deposits. Because provisioning these accounts requires strict adherence to federal banking "
                    "regulations, the platform must first enforce a rigorous Identity Verification (KYC/KYB) workflow. You cannot create "
                    "a FinancialAccount until the connected account has successfully passed all verification checks and has a status of "
                    "'verified' in the capabilities array. Furthermore, the platform assumes responsibility for monitoring transactions "
                    "for suspicious activity, relying on Treasury's built-in transaction monitoring and risk limits to block unexpected "
                    "spikes in outbound volume."
                ),
            },
            {
                "section": "Outbound Payments and Money Movement",
                "section_anchor": "outbound-payments",
                "subsections": [],
                "text": (
                    "Once funds reside within a FinancialAccount, the platform can programmatically trigger money movement using the "
                    "OutboundTransfer and OutboundPayment APIs. An OutboundTransfer is used to move funds from the Treasury account "
                    "back to the connected account's external payout bank account (typically registered during onboarding). Conversely, "
                    "an OutboundPayment enables you to send money to third parties. For example, a marketplace seller could use their "
                    "Treasury balance to pay their raw material suppliers directly via ACH or wire. The API supports Same-Day ACH and "
                    "standard ACH, each carrying different settlement timelines and cut-off windows. It is critical to build robust "
                    "webhook listeners for events such as 'treasury.outbound_payment.posted', 'treasury.outbound_payment.failed', and "
                    "'treasury.outbound_payment.returned'. An ACH return can occur days after the transaction was ostensibly completed, "
                    "necessitating a complex ledgering system on your backend to handle reversals, insufficient funds (NSF) fees, and "
                    "balance recalculations dynamically. To prevent overdrafts, the API natively implements balance locking during pending "
                    "outbound operations."
                ),
            },
            {
                "section": "Yield and Interest Accrual",
                "section_anchor": "yield-accrual",
                "subsections": [],
                "text": (
                    "To increase the attractiveness of embedded finance offerings, platforms can opt into the yield feature, allowing "
                    "end users to earn interest on the idle balances held in their FinancialAccounts. Yield is calculated daily based "
                    "on the end-of-day ledger balance and is paid out monthly. The API exposes endpoints to query the current Annual "
                    "Percentage Yield (APY) and fetch historical interest payouts. Because interest rates fluctuate based on macroeconomic "
                    "conditions and federal reserve policies, the APY is subject to change without prior notice. Platforms must build "
                    "disclaimer components in their UI to clearly communicate that yield rates are variable. Furthermore, providing "
                    "interest-bearing accounts introduces additional tax reporting requirements, such as generating 1099-INT forms for "
                    "users at the end of the fiscal year, a process that can be automated through the Stripe Tax and Reporting pipelines."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 15: CAPITAL (Préstamos y Financiamiento)
    # ------------------------------------------------------------------
    {
        "product": "Capital",
        "category": "Financing",
        "article_id": "capital-loans-and-repayments",
        "article_title": "Loan Eligibility, Offers, and Automated Repayments",
        "article_path": "/docs/capital/loans",
        "sections": [
            {
                "section": "Machine Learning Eligibility and Offers",
                "section_anchor": "eligibility",
                "subsections": [],
                "text": (
                    "Stripe Capital provides fast, flexible financing to your platform's users without requiring complex paperwork or "
                    "traditional credit checks. Eligibility is determined continuously by a proprietary machine learning model that analyzes "
                    "payment volume, dispute rates, customer retention, and overall business health directly from the user's processing "
                    "history. When a business qualifies, the API generates a Capital Offer object containing three primary variables: the "
                    "advance amount (the principal), the flat fee (the cost of capital, rather than compounding interest), and the "
                    "repayment rate (the percentage of daily sales withheld). Platforms can fetch active offers using the '/v1/capital/offers' "
                    "endpoint and present them in a white-labeled dashboard. It is important to note that offers have an expiration date "
                    "and can be revoked dynamically if the model detects a sudden degradation in the business's risk profile, such as a "
                    "massive spike in chargebacks over a 24-hour period."
                ),
            },
            {
                "section": "Automated Repayment and Capture Rates",
                "section_anchor": "repayment-mechanics",
                "subsections": [],
                "text": (
                    "Unlike traditional term loans with fixed monthly payments, Capital utilizes a dynamic repayment model tied directly "
                    "to the business's revenue flow. Upon accepting an offer, the funds are instantly deposited into the user's balance. "
                    "Simultaneously, the API configures a capture rate on all future incoming transactions. For example, if the repayment "
                    "rate is 12%, then for every $100 processed, $12 is automatically intercepted and routed toward loan repayment, while "
                    "$88 is routed to the user's standard payout balance. This architecture ensures that businesses pay more during busy "
                    "seasons and less during slow periods, aligning debt service with cash flow. However, to mitigate risk for the lender, "
                    "contracts often include a minimum repayment threshold over a specified time horizon (e.g., paying off at least 1/18th "
                    "of the total balance every 60 days). If the automated transaction deductions fall short of this minimum, the system "
                    "will automatically trigger a direct debit via ACH from the user's linked bank account to cover the shortfall."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 16: ATLAS (Incorporación de Empresas)
    # ------------------------------------------------------------------
    {
        "product": "Atlas",
        "category": "Company Formation",
        "article_id": "company-incorporation",
        "article_title": "Delaware C-Corp, LLC Formation, and Equity",
        "article_path": "/docs/atlas/incorporation",
        "sections": [
            {
                "section": "Entity Selection and Legal Architecture",
                "section_anchor": "entity-selection",
                "subsections": [],
                "text": (
                    "Stripe Atlas completely automates the process of incorporating a new company, turning weeks of legal coordination into "
                    "a straightforward API call or dashboard flow. Founders must first decide between establishing a Delaware C-Corporation "
                    "or a Delaware Limited Liability Company (LLC). C-Corps are specifically engineered for high-growth startups that intend "
                    "to raise venture capital, as institutional investors mandate this structure for its robust corporate governance framework "
                    "and the ability to easily issue stock options to employees. LLCs, on the other hand, offer operational flexibility and "
                    "pass-through taxation, making them ideal for bootstrapped businesses, holding companies, or solo ventures. Regardless "
                    "of the entity type, Atlas automatically handles the filing of the Certificate of Incorporation (or Formation) with the "
                    "Delaware Division of Corporations, acts as the registered agent for the first year, and orchestrates the generation of "
                    "foundational legal documents, including the initial board resolutions and corporate bylaws."
                ),
            },
            {
                "section": "Tax Identification (EIN) and Post-Incorporation",
                "section_anchor": "ein-and-equity",
                "subsections": [],
                "text": (
                    "Once the Delaware filing is confirmed, a company cannot legally operate, open a US bank account, or process payments "
                    "without an Employer Identification Number (EIN). Atlas integrates directly with the Internal Revenue Service (IRS) to "
                    "expedite the acquisition of the EIN (Form SS-4). While founders with a US Social Security Number can typically receive "
                    "their EIN within days, foreign founders may experience delays of several weeks due to IRS processing times for non-US "
                    "residents. Upon successful EIN generation, Atlas unlocks the equity allocation phase for C-Corps. The platform provides "
                    "standardized stock issuance templates, enabling founders to formally purchase their shares. Crucially, Atlas also includes "
                    "instructions and templates for filing the 83(b) election, a time-sensitive tax document that must be submitted to the IRS "
                    "within 30 days of stock issuance. Failing to file the 83(b) election can result in devastating tax liabilities for founders "
                    "if the company's valuation increases rapidly."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 17: INVOICING (Facturación Avanzada B2B)
    # ------------------------------------------------------------------
    {
        "product": "Invoicing",
        "category": "B2B Payments",
        "article_id": "advanced-b2b-invoicing",
        "article_title": "Virtual Accounts, Reconciliation, and Payment Terms",
        "article_path": "/docs/invoicing/b2b",
        "sections": [
            {
                "section": "Virtual Bank Accounts for Auto-Reconciliation",
                "section_anchor": "virtual-accounts",
                "subsections": [],
                "text": (
                    "While consumer payments rely heavily on credit cards, B2B transactions predominantly utilize bank transfers (ACH, Wire) due "
                    "to high transaction volumes and the desire to avoid percentage-based credit card fees. To streamline this, the Invoicing "
                    "API introduces the concept of Customer Bank Accounts and Virtual Accounts. When you generate an invoice for $50,000, you "
                    "can configure the payment method to 'customer_balance'. Stripe will then dynamically generate a unique, single-use or "
                    "customer-specific virtual routing and account number. The invoice PDF displays these virtual banking credentials rather "
                    "than your company's actual master bank account. When the buyer initiates a wire transfer from their corporate portal to "
                    "the virtual account, the Stripe backend automatically intercepts the incoming funds, perfectly matches the exact amount "
                    "to the outstanding invoice without any manual intervention, transitions the invoice state to 'paid', and triggers the "
                    "'invoice.paid' webhook. This eliminates the notorious 'cash application' problem where accounting teams spend countless "
                    "hours matching generic incoming wire transfers to specific client invoices."
                ),
            },
            {
                "section": "Payment Terms and Net-D Configurations",
                "section_anchor": "payment-terms",
                "subsections": [],
                "text": (
                    "Enterprise invoicing requires complex payment terms that dictate exactly when an invoice becomes past due. Through the API, "
                    "you can configure the 'collection_method' to 'send_invoice' and define the 'days_until_due' attribute. This enables standard "
                    "Net-15, Net-30, Net-60, or Net-90 configurations. You can also specify absolute due dates using Unix timestamps for custom "
                    "contractual agreements. To incentivize early payment, platforms can implement dynamic discount logic on the frontend, modifying "
                    "the invoice total if payment is received within a certain window (e.g., 2/10 Net 30, meaning a 2% discount if paid within 10 "
                    "days, otherwise the full amount is due in 30 days). Furthermore, if an invoice passes its due date without reconciliation, "
                    "the system can be configured to automatically apply late fees by appending a new line item to the next billing cycle's draft "
                    "invoice, compounding the financial penalty."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 18: CLIMATE (Sostenibilidad y Remoción de Carbono)
    # ------------------------------------------------------------------
    {
        "product": "Climate",
        "category": "Sustainability",
        "article_id": "carbon-removal-api",
        "article_title": "Fractional Carbon Removal and Portfolio Allocation",
        "article_path": "/docs/climate/api",
        "sections": [
            {
                "section": "Scientific Methodology and Portfolios",
                "section_anchor": "climate-portfolios",
                "subsections": [],
                "text": (
                    "Stripe Climate is an API designed to direct funds toward frontier carbon removal technologies rather than traditional, often "
                    "unverifiable, carbon offset programs. Traditional offsets focus on avoiding future emissions (like not cutting down a forest), "
                    "whereas Stripe Climate exclusively funds permanent, scientifically validated removal technologies, such as Direct Air Capture "
                    "(DAC), bio-oil sequestration, enhanced rock weathering, and ocean alkalinity enhancement. By utilizing the Climate API, platforms "
                    "can automatically route a fraction of their revenue to a curated portfolio of these technologies. The portfolio is managed by "
                    "expert climatologists who vet the suppliers for permanence (guaranteeing carbon stays out of the atmosphere for >1,000 years), "
                    "additionality, and scalability. Because frontier technologies are currently expensive per ton of CO2 removed, the API abstracts "
                    "the complexity of fractional purchasing, allowing businesses to contribute as little as 1% of their gross revenue to these "
                    "massive industrial projects."
                ),
            },
            {
                "section": "Programmatic Contributions and User Opt-ins",
                "section_anchor": "programmatic-contributions",
                "subsections": [],
                "text": (
                    "You can integrate Climate into your payment flow in two primary ways: platform-level contributions or user-level opt-ins. "
                    "Platform-level integration involves configuring a fixed percentage of all processed volume to be withheld and directed to Climate. "
                    "This is managed seamlessly in the dashboard or via the API by updating your account's settings. For user-level opt-ins, you "
                    "can build a checkout UI that prompts the end consumer to 'Make this order carbon neutral' by adding a specific monetary amount "
                    "or percentage to their cart total. When creating the PaymentIntent, you pass a 'climate' parameter detailing the contribution "
                    "amount. The Stripe backend instantly splits the funds upon capture, routing the principal to your account and the climate "
                    "contribution directly to the removal portfolio. To ensure transparency, the API also provides data endpoints to fetch the exact "
                    "number of metric tons of carbon your platform has funded, allowing you to build dynamic sustainability impact dashboards for "
                    "your marketing pages."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 19: FINANCIAL CONNECTIONS (Open Banking)
    # ------------------------------------------------------------------
    {
        "product": "Financial Connections",
        "category": "Open Banking",
        "article_id": "account-linking-and-data",
        "article_title": "Bank Linking, OAuth, and Balance Checking",
        "article_path": "/docs/financial-connections/linking",
        "sections": [
            {
                "section": "OAuth Flows and Instant Verification",
                "section_anchor": "oauth-verification",
                "subsections": [],
                "text": (
                    "Financial Connections provides a secure, conversion-optimized interface for users to link their bank accounts directly to your "
                    "platform, similar to Plaid. Instead of relying on users to manually type routing and account numbers—a process prone to typos "
                    "and fraud—the API utilizes open banking standards and direct API integrations with thousands of financial institutions. When "
                    "you invoke a FinancialConnectionsSession, the SDK presents a hosted modal window. For modern banks, this utilizes an OAuth 2.0 "
                    "flow, redirecting the user to their bank's native mobile app or website to authenticate securely without ever sharing their "
                    "password with Stripe or your platform. Upon successful authentication, the API instantly verifies the account and returns a "
                    "tokenized bank account object. This immediate verification completely eliminates the traditional multi-day waiting period "
                    "associated with micro-deposits, drastically increasing the activation rate for ACH direct debit payments."
                ),
            },
            {
                "section": "Balance Checking and Account Data Extraction",
                "section_anchor": "balance-checks",
                "subsections": [],
                "text": (
                    "Beyond simple payment routing, Financial Connections grants authorized access to deep account telemetry. One of the most critical "
                    "features for risk mitigation is real-time balance checking. Before initiating a large ACH debit, your server can query the "
                    "'/v1/financial_connections/accounts/{id}/balance' endpoint to verify that the user has sufficient funds. If the 'available' "
                    "balance is lower than your target charge, you can proactively halt the transaction, saving your platform from expensive ACH "
                    "return fees (NSF fees) and preserving your reputation with the banking network. Furthermore, with explicit user consent, "
                    "the API can extract historical transaction data and account ownership details. This data can be utilized to underwrite credit "
                    "models, verify the legal name associated with the account against KYC documents, or build personalized financial management "
                    "(PFM) tools within your application. To maintain security, access tokens have expiration limits, and continuous data syncing "
                    "requires periodic re-authentication by the user."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 20: DATA PIPELINE (ETL y Data Warehousing)
    # ------------------------------------------------------------------
    {
        "product": "Data Pipeline",
        "category": "Analytics",
        "article_id": "warehouse-syncing-and-etl",
        "article_title": "ETL Automation for Snowflake and Redshift",
        "article_path": "/docs/data-pipeline/etl",
        "sections": [
            {
                "section": "Automated Schema Management and Syncing",
                "section_anchor": "schema-sync",
                "subsections": [],
                "text": (
                    "Stripe Data Pipeline completely automates the extraction, transformation, and loading (ETL) of your entire Stripe data footprint "
                    "directly into your central data warehouse, such as Amazon Redshift or Snowflake. Rather than engineering custom REST API polling "
                    "scripts, dealing with pagination limits, and handling API rate limits (429 errors), Data Pipeline establishes a secure, continuous "
                    "connection between Stripe's infrastructure and your cloud environment. The service automatically creates and maintains over "
                    "40 standardized tables representing your core objects (Charges, Customers, Subscriptions, Refunds, Invoices). Crucially, the "
                    "pipeline handles schema evolution automatically. When Stripe releases a new API version that introduces a new column to the "
                    "Charge object, Data Pipeline seamlessly executes the ALTER TABLE statements in your warehouse, ensuring that your data models "
                    "never break and your BI tools always have access to the latest fields."
                ),
            },
            {
                "section": "Historical Backfills and Parquet Optimization",
                "section_anchor": "historical-backfill",
                "subsections": [],
                "text": (
                    "When initializing Data Pipeline, the system performs a massive historical backfill, transferring your entire account history "
                    "from day one into your warehouse. Depending on your transaction volume, this initial load can encompass hundreds of millions "
                    "of rows. To optimize query performance and minimize storage costs on the receiving end, the data is serialized into highly "
                    "compressed, columnar formats like Apache Parquet before transit. Once the historical backfill is complete, the pipeline shifts "
                    "into an incremental sync mode, typically updating your warehouse tables on a recurring schedule (e.g., every few hours or "
                    "daily at midnight UTC). This architecture allows your data science teams to join your transactional financial data directly "
                    "with your internal application databases, marketing attribution models, or CRM systems (like Salesforce). You can easily write "
                    "a single SQL query to determine the exact Customer Acquisition Cost (CAC) to Lifetime Value (LTV) ratio per advertising campaign "
                    "by linking Stripe payment metadata with Google Analytics session IDs."
                ),
            },
            {
                "section": "Security, PII Redaction, and Access Control",
                "section_anchor": "data-security",
                "subsections": [],
                "text": (
                    "Because financial data is inherently sensitive, Data Pipeline employs strict security protocols. Data is encrypted in transit "
                    "using TLS 1.3 and at rest within the warehouse environment. For organizations subject to stringent compliance frameworks like "
                    "PCI-DSS, SOC 2, or GDPR, the pipeline offers robust Personally Identifiable Information (PII) redaction features. Administrators "
                    "can configure the pipeline to automatically hash or completely drop specific columns containing customer emails, physical "
                    "addresses, or phone numbers before the data ever leaves Stripe's servers. This ensures that broad teams of analysts can safely "
                    "query aggregated revenue metrics without risking the exposure of sensitive consumer data. Additionally, cross-region replication "
                    "policies guarantee that European customer data can be confined to EU-based warehouse instances, strictly adhering to data "
                    "sovereignty and localization laws."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 21: CHECKOUT (Hosted Payment Pages)
    # ------------------------------------------------------------------
    {
        "product": "Checkout",
        "category": "Hosted UI",
        "article_id": "checkout-sessions-and-domains",
        "article_title": "Session Lifecycle, Custom Domains, and Cart Recovery",
        "article_path": "/docs/checkout/sessions",
        "sections": [
            {
                "section": "The Session State Machine and Redirection",
                "section_anchor": "session-lifecycle",
                "subsections": [],
                "text": (
                    "Stripe Checkout provides a fully hosted, conversion-optimized payment page that dynamically adapts to the customer's "
                    "device, location, and preferred language. The architecture revolves around the Checkout Session object. When a user "
                    "initiates a purchase, your backend creates a Session via a POST request to '/v1/checkout/sessions', defining the "
                    "line items, success URL, and cancel URL. The API responds with a Session ID and a short-lived URL. Your server then "
                    "issues an HTTP 303 redirect, sending the client's browser to the Stripe-hosted domain. A Session exists in one of "
                    "three terminal states: 'open', 'complete', or 'expired'. By default, an open Session expires after 24 hours to prevent "
                    "inventory lock-up, though this can be configured via the 'expires_at' parameter. When the payment succeeds, the user "
                    "is redirected to your 'success_url' with the Session ID appended as a query parameter. Crucially, your backend must "
                    "never rely solely on this frontend redirect to fulfill the order, as users can close the tab before the redirect executes. "
                    "Instead, you must listen for the 'checkout.session.completed' asynchronous webhook to provision the digital goods or "
                    "initiate physical shipping."
                ),
            },
            {
                "section": "Custom Domains and Branding Security",
                "section_anchor": "custom-domains",
                "subsections": [],
                "text": (
                    "To maintain brand consistency and reduce cart abandonment caused by domain switching, platforms can configure Custom "
                    "Domains for their Checkout pages. Instead of redirecting users to 'checkout.stripe.com', the URL can be masked as "
                    "'pay.yourbrand.com'. This requires configuring specific DNS records (CNAME and TXT) in your domain registrar to prove "
                    "ownership and allow Stripe to automatically provision and rotate SSL/TLS certificates via Let's Encrypt. Because "
                    "Checkout handles raw Primary Account Numbers (PAN), it operates under the highest level of Payment Card Industry Data "
                    "Security Standard (PCI-DSS) compliance. Even when using a custom domain, the underlying infrastructure is entirely "
                    "isolated from your servers, meaning your platform qualifies for the SAQ-A compliance tier, completely offloading the "
                    "burden of vulnerability scans and penetration testing associated with handling raw cardholder data."
                ),
            },
            {
                "section": "Abandoned Cart Recovery and Retention",
                "section_anchor": "cart-recovery",
                "subsections": [],
                "text": (
                    "E-commerce platforms experience high rates of cart abandonment. Checkout includes built-in recovery mechanics to recapture "
                    "lost revenue. When creating the Session, you can pass the 'recovery' dictionary to enable automated follow-up emails. "
                    "If a user enters their email address on the Checkout page but fails to complete the payment within a specified timeframe, "
                    "Stripe dispatches a highly optimized, localized email containing a unique cryptographic link to resume the session exactly "
                    "where they left off. You can track the efficacy of these emails via webhooks such as 'checkout.session.expired' and monitor "
                    "the 'recovered' boolean flag on the resulting PaymentIntent. Furthermore, the 'consent_collection' object allows you to "
                    "seamlessly capture marketing opt-ins (e.g., newsletter subscriptions) directly on the payment page, synchronizing this "
                    "data with your CRM or marketing automation pipelines."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 22: ELEMENTS (UI Components & PCI Compliance)
    # ------------------------------------------------------------------
    {
        "product": "Elements",
        "category": "Custom UI",
        "article_id": "payment-element-and-tokenization",
        "article_title": "The Payment Element, Link, and PCI Isolation",
        "article_path": "/docs/elements/payment-element",
        "sections": [
            {
                "section": "The Payment Element Architecture",
                "section_anchor": "payment-element",
                "subsections": [],
                "text": (
                    "For merchants requiring granular control over their frontend checkout experience, Stripe Elements offers a suite of highly "
                    "customizable, pre-built UI components. The flagship component is the Payment Element, a unified, embeddable iFrame that "
                    "dynamically surfaces the most relevant payment methods based on the transaction's currency, the amount, and the buyer's "
                    "geolocation. Unlike legacy integration methods that required building separate UIs for credit cards, iDEAL, Bancontact, "
                    "and Klarna, the Payment Element reads the configuration from the backend PaymentIntent and renders the optimal layout "
                    "automatically. Because the input fields (like the card number and CVC) are hosted inside an iFrame originating from Stripe's "
                    "domain, the host page cannot access the raw keystrokes via JavaScript. This DOM-level isolation guarantees that malicious "
                    "browser extensions or Cross-Site Scripting (XSS) attacks on your main domain cannot siphon sensitive cardholder data, "
                    "preserving your SAQ-A compliance status."
                ),
            },
            {
                "section": "Tokenization and Intent Confirmation",
                "section_anchor": "tokenization",
                "subsections": [],
                "text": (
                    "The lifecycle of a payment through Elements relies heavily on asynchronous tokenization. When the user clicks the final "
                    "submit button, the frontend SDK executes the 'stripe.confirmPayment' function. Behind the scenes, the SDK securely "
                    "transmits the encrypted card details to the gateway, receiving a PaymentMethod token in return. This token is then "
                    "automatically attached to the PaymentIntent, and the authorization request is dispatched to the card network. If the "
                    "issuing bank mandates Step-Up Authentication via 3D Secure 2 (3DS2), the Elements SDK intercepts the 'requires_action' "
                    "status and dynamically injects an authentication modal into the DOM without requiring a full page redirect. Once the user "
                    "completes the challenge (e.g., biometrics on their banking app), the SDK automatically resumes the confirmation flow. "
                    "Your frontend logic must gracefully handle exhaustive error states returned by this function, mapping decline codes like "
                    "'insufficient_funds' or 'do_not_honor' to localized, user-friendly error messages."
                ),
            },
            {
                "section": "Link Authentication and Network Effects",
                "section_anchor": "link-authentication",
                "subsections": [],
                "text": (
                    "The Payment Element natively integrates 'Link', Stripe's one-click checkout network. When a user lands on your payment "
                    "page, the SDK automatically checks if their email address or browser fingerprint is associated with an existing Link "
                    "account. If recognized, the system triggers a frictionless authentication flow—typically sending a One-Time Password (OTP) "
                    "via SMS to the user's mobile device. Upon entering the six-digit OTP, the Payment Element instantly hydrates with the "
                    "user's securely vaulted credit cards and shipping addresses across the entire global Stripe network. This massive network "
                    "effect drastically reduces friction on mobile devices, boosting conversion rates by eliminating the need to manually type "
                    "sixteen-digit PANs and complex billing addresses. Developers can customize the appearance of the Link button and control "
                    "its specific placement within the component hierarchy using the 'Appearance API', passing CSS variables natively through "
                    "the JavaScript initialization object."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 23: REVENUE RECOGNITION (RevRec)
    # ------------------------------------------------------------------
    {
        "product": "Revenue Recognition",
        "category": "Accounting",
        "article_id": "asc-606-and-amortization",
        "article_title": "ASC 606 Compliance and Amortization Schedules",
        "article_path": "/docs/revenue-recognition/principles",
        "sections": [
            {
                "section": "Deferred Revenue and ASC 606/IFRS 15",
                "section_anchor": "deferred-revenue",
                "subsections": [],
                "text": (
                    "Modern software-as-a-service (SaaS) businesses operate on recurring revenue models that complicate standard cash-basis "
                    "accounting. According to the ASC 606 (US GAAP) and IFRS 15 accounting standards, revenue cannot be recognized on the income "
                    "statement simply when the cash is collected; it must be recognized proportionally as the service is delivered over time. "
                    "Stripe Revenue Recognition completely automates this complex ledgering process. When a customer purchases an annual subscription "
                    "for $1,200 upfront in January, the system automatically books the entire $1,200 to a liability account called 'Deferred Revenue' "
                    "on the balance sheet. Then, a systemic chron job automatically amortizes this amount, shifting $100 from Deferred Revenue "
                    "to 'Recognized Revenue' on the income statement on the final day of each month. This automation replaces fragile Excel "
                    "spreadsheets and prevents severe auditing penalties during financial due diligence or IPO preparations."
                ),
            },
            {
                "section": "Contract Modifications and Upgrades",
                "section_anchor": "contract-modifications",
                "subsections": [],
                "text": (
                    "The true complexity of revenue recognition arises when customers alter their contracts mid-cycle—a process known as contract "
                    "modification. If a user downgrades, upgrades, or receives a prorated refund in the middle of their billing period, the "
                    "underlying amortization schedule must be instantly recalculated. The RevRec engine intelligently evaluates whether the modification "
                    "represents a distinct new contract or a cumulative catch-up adjustment to the existing contract based on the standalone selling "
                    "price (SSP). Furthermore, it handles the complex accounting treatment of platform fees and disputes. When a chargeback occurs, "
                    "the system must accurately reverse the previously recognized revenue and adjust the corresponding contra-revenue accounts (like "
                    "bad debt expense), ensuring that your month-end journal entries exported to NetSuite, QuickBooks, or Xero remain mathematically "
                    "perfect and audit-ready."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 24: TAX REPORTING (1099 E-Filing)
    # ------------------------------------------------------------------
    {
        "product": "Tax Reporting",
        "category": "Compliance",
        "article_id": "irs-1099-filing",
        "article_title": "Form 1099-K, 1099-NEC, and TIN Matching",
        "article_path": "/docs/tax-reporting/1099s",
        "sections": [
            {
                "section": "Tax Information Number (TIN) Verification",
                "section_anchor": "tin-matching",
                "subsections": [],
                "text": (
                    "For platform models using Stripe Connect, the platform carries the legal obligation to report the gross earnings of its "
                    "connected accounts to the Internal Revenue Service (IRS) and relevant state tax authorities. Before the platform can legally "
                    "file these documents, it must collect accurate Taxpayer Identification Numbers (TINs), typically via a Form W-9 for US entities "
                    "or a W-8BEN for foreign entities. Stripe automates this critical step by integrating directly with the IRS TIN Matching system. "
                    "When a connected account submits their Social Security Number (SSN) or Employer Identification Number (EIN) during onboarding, "
                    "Stripe cross-references the name and TIN combination against federal databases in real-time. If a mismatch is detected, the "
                    "API triggers a 'requirements.past_due' state on the account, pausing payouts until the user submits corrected tax documentation. "
                    "This automated gating mechanism prevents the platform from accruing massive 'B-Notice' penalties issued by the IRS for filing "
                    "inaccurate tax returns."
                ),
            },
            {
                "section": "E-Filing and Backup Withholding",
                "section_anchor": "efiling",
                "subsections": [],
                "text": (
                    "At the close of the fiscal year, the API calculates the gross volume processed by every connected account. Depending on the "
                    "fund routing architecture, the platform must file either Form 1099-K (for payment settlement entities handling third-party "
                    "network transactions) or Form 1099-NEC (for non-employee compensation, typically used for freelancers and independent contractors). "
                    "The threshold for federal 1099-K reporting has historically fluctuated, requiring dynamic threshold monitoring built into the "
                    "reporting engine. Stripe Tax Reporting generates draft forms in the dashboard, allowing platform administrators to review the "
                    "aggregated volumes, apply manual corrections, and formally e-file the batches directly with the IRS and the FIRE (Filing "
                    "Information Returns Electronically) system. Additionally, the platform automates postal delivery of paper copies to the end "
                    "recipients. If an account refuses to provide valid tax documentation, the API can be configured to enforce Backup Withholding, "
                    "automatically deducting 24% of all future payouts and remitting those funds directly to the IRS on behalf of the unverified user."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 25: EVENT DESTINATIONS (Webhooks V2)
    # ------------------------------------------------------------------
    {
        "product": "Event Destinations",
        "category": "API Architecture",
        "article_id": "eventbridge-and-pubsub",
        "article_title": "Serverless Event Routing and AWS Integration",
        "article_path": "/docs/event-destinations/serverless",
        "sections": [
            {
                "section": "Direct Cloud Provider Integrations",
                "section_anchor": "cloud-integrations",
                "subsections": [],
                "text": (
                    "Traditional webhooks require developers to build, host, and scale dedicated HTTP endpoints exposed to the public internet, "
                    "complete with complex logic for verifying HMAC signatures, managing concurrency limits, and storing payloads in local databases "
                    "to ensure idempotency. Event Destinations modernizes this paradigm by routing Stripe events directly into your cloud provider's "
                    "native messaging buses, completely bypassing HTTP overhead. You can configure Stripe to publish events directly to Amazon "
                    "EventBridge. Once authenticated via cross-account IAM roles, events like 'invoice.paid' appear instantaneously on your AWS "
                    "event bus. From there, you can leverage native AWS routing rules to trigger AWS Lambda functions, fan out messages via Amazon "
                    "SNS, or stream the raw JSON payloads directly into Amazon S3 via Kinesis Firehose for long-term audit storage. This serverless "
                    "architecture drastically reduces infrastructure maintenance, eliminates the risk of missing events due to momentary web server "
                    "downtime, and provides enterprise-grade scalability during massive traffic spikes (e.g., Black Friday sales events)."
                ),
            },
            {
                "section": "Event Retries and Dead Letter Queues (DLQ)",
                "section_anchor": "event-retries",
                "subsections": [],
                "text": (
                    "Ensuring guaranteed delivery in distributed financial systems is paramount. When Stripe attempts to deliver an event payload "
                    "to a destination (whether a traditional HTTP webhook or an AWS EventBridge bus) and encounters a failure (such as a 5xx HTTP "
                    "status code, a network timeout exceeding 30 seconds, or a cloud provider throttle), it initiates an exponential backoff retry "
                    "schedule. The system will retry the delivery up to three days, exponentially increasing the delay between attempts to allow "
                    "your systems to recover from outages. However, if the event reaches its maximum retry limit without receiving a successful "
                    "acknowledgment, it is permanently marked as failed. To prevent data loss, developers should rely on the '/v1/events' REST "
                    "endpoint to periodically poll and reconcile their local databases against Stripe's immutable event ledger. Alternatively, when "
                    "using Event Destinations with cloud providers, you can natively configure Dead Letter Queues (DLQs). If a Lambda function fails "
                    "to process the payload, EventBridge will automatically route the message to a designated Amazon SQS queue, allowing your "
                    "engineering team to manually debug the payload, patch the code, and redrive the message through the pipeline."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # PRODUCTO 26: TEST CLOCKS (Simulación de Tiempo)
    # ------------------------------------------------------------------
    {
        "product": "Billing Test Clocks",
        "category": "Testing and QA",
        "article_id": "time-simulation",
        "article_title": "Simulating Subscription Lifecycles and Time Travel",
        "article_path": "/docs/billing/testing/test-clocks",
        "sections": [
            {
                "section": "Deterministic Time Simulation",
                "section_anchor": "time-travel",
                "subsections": [],
                "text": (
                    "Testing recurring billing logic, trial expirations, and dunning workflows is historically notoriously difficult. In standard "
                    "environments, QA engineers would have to create a subscription with a 7-day trial and literally wait 7 days to verify if the "
                    "webhooks fired correctly and the user was charged. Stripe resolves this through the Test Clocks API. A Test Clock allows you "
                    "to programmatically simulate the passage of time within an isolated testing environment. You instantiate a Test Clock object "
                    "set to a specific frozen Unix timestamp. You then create mock Customers and Subscriptions, explicitly attaching them to this "
                    "Test Clock ID. When you advance the Test Clock to a future date via a POST request to '/v1/test_helpers/test_clocks/{id}/advance', "
                    "Stripe's backend dramatically accelerates time for those specific objects, synchronously triggering all scheduled lifecycle "
                    "events. Draft invoices are generated, payment methods are automatically attempted (using simulated test cards like the '4242' "
                    "visa), and the corresponding webhooks (such as 'invoice.created' and 'invoice.paid') are rapidly dispatched to your local "
                    "development server."
                ),
            },
            {
                "section": "Complex Lifecycle Scenario Testing",
                "section_anchor": "scenario-testing",
                "subsections": [],
                "text": (
                    "Test Clocks are engineered to evaluate highly complex edge cases involving proration and payment failures. For instance, you "
                    "can simulate a scenario where a user upgrades from a $10 tier to a $50 tier precisely in the middle of their billing cycle. "
                    "By advancing the clock exactly 15 days, you can mathematically assert that the resulting invoice contains the exact positive "
                    "and negative line items expected for the proration. Furthermore, you can attach specific testing tokens to the Customer that "
                    "are hardcoded to fail on the second charge attempt. By advancing the clock past the next billing cycle, you can observe the "
                    "invoice transitioning into the 'past_due' state and verify that your application successfully restricts the user's access "
                    "privileges based on the 'customer.subscription.updated' webhook. This deterministic, programmatic testing infrastructure is "
                    "crucial for maintaining continuous integration (CI/CD) pipelines, ensuring that changes to your pricing models do not introduce "
                    "catastrophic bugs into your revenue engine before deployment to the production environment."
                ),
            },
        ],
    },
]
