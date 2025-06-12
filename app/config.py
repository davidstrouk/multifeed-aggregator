# Configuration for data sources
# This structure allows us to support multiple different source providers.
DATA_PROVIDERS = {
    "heroku_provider": {
        "base_url": "https://credcompare-hr-test-d81ffdfbad0d.herokuapp.com",
        "streams": ["stream1", "stream2", "stream3", "stream4"],
    }
    # To add another provider:
    # "another_provider": {
    #     "base_url": "http://some-other-service.com",
    #     "streams": ["alpha", "beta"],
    # }
}