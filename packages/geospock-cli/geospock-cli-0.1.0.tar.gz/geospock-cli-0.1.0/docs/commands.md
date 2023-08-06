# Available commands

All the commands below are used by entering `geospock COMMAND [--ARGUMENTNAME {ARGUMENTVALUE}]` 
on the command-line. A list of all commands can be obtained by running `geospock help`, and further information on the 
input types of each command can be obtained by running `geospock help COMMAND`.

Each of the commands can have the `--profile {profileName}` argument added if multiple profiles have been set up. 
Arguments listed in square brackets are optional or have default values which can be overridden.

Arguments listed here that end with `.json` should read from the file specified.

## User administration

### Invite new user
`geospock account-invite --email {email} --role {role} [--full-name {full name}]`

Role ID can be one of `USER` and `ADMINISTRATOR`. Refer to documentation
[here](https://docs.geospock.com/Content/Dashboard/userManagement.htm) for information on these roles.

### Delete user
`geospock account-delete --account-id {account ID}`

Deletes the specified user account from the platform. The unique ID of a user must be supplied (not the user's name or 
email). This can be obtained by using the "List user accounts" query to search for the relevant user.

### Update user role
`geospock account-update-role --account-id {account ID} --role {role}`

Changes the role of the specified user account. The unique ID of a user account must be supplied (not the user's name 
or email). This can be obtained by using the "List user accounts" query to search for the relevant user.

Role ID can be one of `USER` and `ADMINISTRATOR`. Refer to documentation
[here](https://docs.geospock.com/Content/Dashboard/userManagement.htm) for information on these roles.

### List user accounts
`geospock account-list [--page-index {page index} --page-size {page size}]`

Lists the user accounts for all platform users. The page index/number can supplied (starting with page 0) and/or the 
number of accounts per page. By default page 0 will be returned with 100 accounts listed per page.

---

## Dataset administration

### List datasets
`geospock dataset-list [--page-index {page index} --page-size {page size}]`

Lists all datasets which the current user has permission to view. The page index/number can supplied (starting with 
page 0) and/or the number of datasets per page. By default page 0 will be returned with 1000 datasets listed per page.

### Get dataset information
`geospock dataset-info --dataset-id {dataset ID}`

Gets information about the specified dataset, including its title, a summary of its contents and when it was created.

### Get dataset operations summary
`geospock dataset-operations --dataset-id {dataset ID}`

Gets a summary of operations for the specified dataset, including its ingest operations.

### Get dataset operations history
`geospock dataset-history --dataset-id {dataset ID} [--page-index {page index} --page-size {page size}]`

Gets the history of the specified dataset, providing information about all the operations which have been performed on
it, including ingest operations.
The page index/number can supplied (starting with page 0) and/or the number of dataset operations per page. By default 
page 0 will be returned with 1000 dataset operations listed per page.

### Create dataset and ingest (schema)
`geospock dataset-create --dataset-id {dataset ID} --data-url {data URL} --schema {schema.json}`

Creates the specified dataset and triggers the ingestion of its data from a specified source (URL), using the specified 
schema file.

### Create dataset and ingest (dataset description)
`geospock dataset-create-extended --dataset-id {datasetID} --data-url {dataURL} --model {model.json}
--query {query.json} --parsing {parsing.json}`

Creates the specified dataset using the specified Dataset Description files (model.json, query.json and parsing.json) 
and triggers the ingestion of the data at the specified URL.

### Ingest further data into dataset
`geospock dataset-add-data --dataset-id {dataset ID} --data-url {data URL}`

Triggers the ingestion of additional data into a specified existing dataset.

### Get the schema used by a dataset
`dataset-get-schema --dataset-id {dataset ID}`

Gets the schema used by a particular dataset.

### Delete dataset
`geospock dataset-delete --dataset-id {dataset ID}`

Deletes the specified dataset and its associated data.