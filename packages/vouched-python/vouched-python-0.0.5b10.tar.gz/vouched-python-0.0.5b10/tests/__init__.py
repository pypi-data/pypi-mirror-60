import os
config = dict(
    test=dict(
        key=os.environ.get('TEST_API_KEY_NO_PROD_DANGER'),
        job_id=os.environ.get('TEST_JOB_ID')
    )
)
