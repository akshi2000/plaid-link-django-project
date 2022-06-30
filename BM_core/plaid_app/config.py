PLAID_CLIENT_ID = "61e82289504b2a001a43604d"
PLAID_SECRET = "842a9ed2b74da36f657304aa0b5eda"
PLAID_API_VERSION = "2019-05-29"
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = "sandbox"
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = "transactions"

# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = "US"
