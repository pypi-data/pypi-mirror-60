# vouched-python

Install the wheel on Python 3:

```sh
pip install --user vouched_python
```

Create update `.env` with the following test environment values:

```python
VOUCHED_SERVER=https://verify.woollylabs.com/graphql
TEST_API_KEY_NO_PROD_DANGER=test_key
TEST_JOB_ID=<ID>
API_KEY=api_key
JOB_ID=<ID>
```


Run tests in the Python 3.7:

```sh
pytest
```

## Build Package

To build python package , the wheel will be created in the `dist` folder. Run:

```
python setup.py sdist bdist_wheel
```

## Quick start
Here's a very simple server using Vouched for Node.js for authentication

### Create the Vouched client

```python
from vouched.api import Client
client = Client(secret_app_key)
```

#### Arguments

| Parameter	| Type | Required | Description |
| ------ | ------ | ------ | ------ |
| key | String | * | Secret Application Key |

#### Returns

| Parameter	| Type | Required | Description |
| ------ | ------ | ------ | ------ |
| key | String | * | Secret Application Key |

#### Errors

[`InvalidRequestError`](#InvalidRequestError)


### Update client key

```python
cret_client_key = <SECRET>
data = client.update_secret_client_key(secret_client_key=secret_client_key)
```

#### Arguments

| Parameter	| Type | Required | Description |
| ------ | ------ | ------ | ------ |
| secretClientKey | String | * | The secret key to be included in the header X-Api-Key of the webhook call. |

#### Returns

| Parameter	| Type | Required | Description |
| ------ | ------ | ------ | ------ |
| secretClientKey | String | * | The updated secretClientKey |

#### Errors
[`AuthenticationError`](#AuthenticationError)
[`ConnectionError`](#ConnectionError)
[`InvalidRequestError`](#InvalidRequestError)
[`UnknownSystemError`](#UnknownSystemError)


### Submit a verification job

```python
from vouched.utils import image_to_base64

user_photo_base64 = image_to_base64('/opt/app/tests/data/selfie.png')
id_photo_base64 = image_to_base64('/opt/app/tests/data/id.jpg')
job = client.submit(
    user_photo=user_photo_base64,
    id_photo=id_photo_base64,
    properties=[
      dict(name='internal_id',value='iid'),
      dict(name='internal_username',value='bob'),
    ],
    type='id-verification',
    first_name='Janice',
    dob='06/22/1990',
    last_name='Way'
)

```

#### Arguments

|type|String|*|Type of AI job ("id-verification")}|
| ----------- | ----------- | ----------- | ----------- |
|callbackURL|String||Upon the jobs completion, Vouched will POST the job results to the webhook. If the callbackURL is not given, Vouch will process the job in realtime.|
|`properties`|Object||Arbitrary properties to add to the job, i.e. application ids. Described below.|
|`parameters`|Object|*|Object for id-verification. Described below.|

#### `properties` - arbitrary properties to add to the job, i.e. application ids

|type|String|*|Type of AI job ("id-verification")}|
| ----------- | ----------- | ----------- | ----------- |
|name|String||Name of the property|
|value|String||Value of the property|

#### `parameters` - object for id-verification.

|type|String|*|Type of AI job ("id-verification")|
| ----------- | ----------- | ----------- | ----------- |
|userPhoto|String| Buffer||The users id comparison photo. Supported types include image/png, image/jpeg|
|idPhoto|String| Buffer|*|The users official identification photo. Supported types include image/png, image/jpeg|
|idPhotoBack|String| Buffer|*|The users official back of the identification photo. Supported types include image/png, image/jpeg.|
|firstName|String|*|The users first name.|
|lastName|String|*|The users last name.|
|dob|String|*|Date in the format MM/DD/YYYY.|

#### Returns

| Parameter	| Type | Required | Description |
| ------ | ------ | ------ | ------ |
| job | Job | * | The newly created job. |

#### Errors
[`AuthenticationError`](#AuthenticationError)
[`ConnectionError`](#ConnectionError)
[`InvalidRequestError`](#InvalidRequestError)
[`UnknownSystemError`](#UnknownSystemError)


### Remove a job

```python
job = client.remove_job(
    id='USkjk33'
)
```

#### Arguments

| Parameter	| Type | Required | Description |
| ------ | ------ | ------ | ------ |
| id | String | * | ID of the job to remove. |

#### Returns

| Parameter	| Type | Required | Description |
| ------ | ------ | ------ | ------ |
| job | Job | * | The newly created job. |

#### Errors
[`AuthenticationError`](#AuthenticationError)
[`ConnectionError`](#ConnectionError)
[`InvalidRequestError`](#InvalidRequestError)
[`UnknownSystemError`](#UnknownSystemError)


### Provide results on jobs
```python
params := map[string]interface{}{
  "page":       1,
  "sortBy":     "date",
  "sortOrder":  "desc",
  "from":       "1990-12-24T04:44:00+00:00",
  "to":         "2020-12-24T04:44:00+00:00",
  "type":       "id-verification",
  "token":       "SESSION_TOKEN",
  "status":     "active",
  "withPhotos": false,
  "pageSize":   2,
}
if resp, err := c.Jobs(params); err != nil {
  fmt.Printf("Error: %+v\n", err)
} else {
  fmt.Printf("Jobs: %+v\n", resp)
}

jobs = client.jobs(
    page=1,
    page_size=2,
    type='id-verification',
    token=<TOKEN_FROM_WEB_CLIENT>,
    status='active',
    sort_by='date',
    sort_order='desc',
    with_photos=True,
    from_date='2017-01-24T04:44:00+00:00',
    to_date='2020-12-24T04:44:00+00:00'
 )
```

#### Arguments
|Parameter|Type|Required|Description|
| ------ | ------ | ------ | ------ |
|id|String|*|ID of the job to remove.|
|type|String||Type of job ("id-verification").|
|ids|[ID]||Filter by a list of job IDs.|
|page|String||Paginate list by page where the page starts at 1, defaults to 1.|
|pageSize|String||The number of items for a page, max 1000, defaults to 100.|
|sortBy|String||Sort the list from ("date", "status").|
|sortOrder|String||Order the sort from ("asc", "desc").|
|status|String||Filter by status from ("active","completed")|
|to|String||Filter by submitted to ISO8601 date.|
|from|String||Filter by submitted from ISO8601 date.|
|withPhotos|Boolean||Defaults to False. The returned job will contain detailed information idPhoto, idPhotoBack, and userPhoto.|

#### Returns
| Parameter	| Type | Required | Description |
| ------ | ------ | ------ | ------ |
|jobs|[Job]|*|The removed job.|
|totalPages|Int|*|Total number of pages of jobs.|
|pageSize|Int|*|The requested page size.|
|page|Int|*|The requested page.|
|total|Int|*|Total number of filtered jobs.|

### Errors
[`AuthenticationError`](#AuthenticationError)
[`ConnectionError`](#ConnectionError)
[`InvalidRequestError`](#InvalidRequestError)
[`UnknownSystemError`](#UnknownSystemError)

## Types
### Errors

|Parameter|Type|Required|Description|
| ------ | ------ | ------ | ------ |
|`type`|String|*||
|message|String|*|Type of job ("id-verification").|
|suggestion|[ID]||A suggestion for matching name, John Smith, Jon Smith.|
|errors|[Error]|InvalidRequestError contains a sub list of errors|

#### `type`
`InvalidRequestError` - The request is invalid.
`FaceMatchError` - Face match felled below the threshold
`NameMatchError` - Name match felled below the threshold
`BirthDateMatchError` - Birth date match felled below the threshold
`InvalidIdPhotoError` - The ID is invalid
`InvalidUserPhotoError` - The user photo (selfie) is invalid
`UNAUTHENTICATED`/`AuthenticationError` - The request could not be authenticated
`ConnectionError` - A connection error occurred while communicating to the Vouched service
`InvalidIdBackPhotoError` - The back of the ID is invalid
`UnknownSystemError` - A unknown system error occurred
`InvalidIdError` - The ID is invalid

### Job
|Parameter|Type|Required|Description|
| ------ | ------ | ------ | ------ |
|id|ID |*|Job ID|
|status|String|*|Job status from ("active","completed")|
|submitted|String||ISO8601 date
|`request`|Object||Object for 'id-verification'.|
|`result`|Object||Object of 'id-verification'.|
|errors|[Error] ||List of errors for unsuccessful completed jobs.|

#### `request`
|Parameter|Type|Required|Description|
| ------ | ------ | ------ | ------ |
|type |String |* |Job type|
|callbackURL |String ||POST enabled webhook|
|parameters |JobParameters |* |Object for 'id-verification'|

#### `result`
|Parameter|Type|Required|Description|
| ------ | ------ | ------ | ------ |
|success|Boolean|*|Did the id verification completed successfully?|
|type|String||The id type|
|callbackURL|String||POST enabled webhook|
|state|String||The issuing state of the id if applicable|
|country|String||The issuing country of the id|
|id|String||The verified id number of the id|
|expireDate|String||The verified expired date in the format MM/DD/YYYY|
|birthDate|String||The verified date in the format MM/DD/YYYY|
|firstName|String||The user's verified first name.|
|lastName|String||The user's verified last name|
|confidences|Confidences||Confidence scores|

### Confidences
|Parameter|Type|Required|Description|
| ------ | ------ | ------ | ------ |
|id|Float |*|Confidence score for an id photo, 0-1.0|
|backId|Float |*|Confidence score for the back of the id photo, 0-1.0|
|selfie|Float |*|Confidence score for a selfie photo, 0-1.0|
|idMatch|Float |*|Confidence score for matching data on the id, 0-1.0|
|faceMatch|Float |*|Confidence score for matching faces, 0-1.0|

### JobParameters
|Parameter|Type|Required|Description|
| ------ | ------ | ------ | ------ |
|idPhoto|String |*|The user's official identification photo in base64.|
|userPhoto|String ||The user's id comparison photo in base64.|
|twicPhoto|String ||The user's id twic id photo in base64.|
|carInsurancePhoto|String ||The user's id car insurance photo in base64.|
|dotPhoto|String |*|The user's id dot letter photo in base64.|
|idPhotoBack|String ||The user's official back of the identification photo in base64.|
|dob|String ||Date in the format MM/DD/YYYY.|
|firstName|String ||The user's first name.|
|lastName|String ||The user's last name.|

