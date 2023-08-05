from gql import Client, gql

update_secret_client_key_mutation = gql('''
  mutation updateSecretClientKey($secretClientKey: String) {
    updateSecretClientKey(secretClientKey: $secretClientKey) {
      secretClientKey
    }
  }
''')


job_fragment = '''
  id
  status
  request {
    type
    callbackURL
    properties{
      name
      value
    }
    parameters {
      idPhoto
      userPhoto
      firstName
      lastName
      dob
    }
  }
  result {
    success
    type
    country
    state

    id
    firstName
    lastName
    middleName
    birthDate
    expireDate

    confidences {
      id
      backId
      selfie
      idMatch
      faceMatch
    }
  }
  errors {
    type
    message
    suggestion
  }
  submitted
'''

remove_job_mutation = gql('''
  mutation removeJob(
  $id: ID!
  ) {
    removeJob(
      id: $id
    ) {
      %s
    }
  }
''' % job_fragment)

submit_job_mutation = gql('''
  mutation submitJob(
    $photo1: Upload
    $photo2: Upload
    $type: String!
    $callbackURL: String
    $properties: [JobPropertyParam]
    $params: JobParams
  ) {
    submitJob(
      photo1: $photo1
      photo2: $photo2
      type: $type
      callbackURL: $callbackURL
      properties: $properties
      params: $params
    ) {
      %s
    }
  }
''' % job_fragment)


jobs_query = gql('''
  query jobs(
    $id: ID
    $ids: [ID]
    $type: String
    $token: String
    $status: String
    $to: String
    $from: String
    $withPhotos: Boolean
    $sortOrder: String
    $sortBy: String
    $page: Int
    $pageSize: Int
  ) {
    jobs(
      withPhotos: $withPhotos
      id: $id
      ids: $ids
      status: $status
      type: $type
      token: $token
      to: $to
      from: $from
      sortOrder: $sortOrder
      sortBy: $sortBy
      page: $page
      pageSize: $pageSize
    ) {
      total
      totalPages
      pageSize
      page
      items {
        %s
      }
    }
  }
''' % job_fragment )
