import os
config = dict(
    vouched_server=os.environ.get('VOUCHED_SERVER', 'https://verify.woollylabs.com/graphql')
)
