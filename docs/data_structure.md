# Data Structure

The JSON file will not be publically available, but this document will outline
how the document is structured.

## Top Level Keys

The JSON file will look like this:

```json
{
    "research": [],
    "team": []
}
```

## `readings` key

The JSON file includes a `readings` key that will return an array. The array
returns a `reading` object with the following keys:

```json
{
    "id": "",
    "title": "",
    "url": "",
    "assigned_to": 0,
    "notes": "",
    "summary": "",
    "submitted": false
}
```

Details:

|Key|Default|Description|
|---|---|---|
|`id`|`time.time()` result|An ID for the website, based on `time.time()`|
|`title`|Title of the article|The title of the document we are researching.|
|`url`|Link of the article|The URL where we can get a copy of the document. Internal Google Drive link works too!|
|`assigned_to`|`0`|The Discord ID of the individual in charge of reading.|
|`notes`|`""`|The notes for the article, in bullet points.|
|`summary`|`""`|A general summary of the document.|
|`submitted`|`false`|Whether or not it is in the git repository.|

## `team` key

This returns an array of `team` object, representing a team member. The object looks like:

```json
{
    "id": 0,
    "name": "",
    "email": ""
}
```

Details:

|Key|Description|
|---|---|
|`id`|A Discord ID|
|`name`|The individual's first and last name, for commit purposes|
|`email`|The individual's email, for commit purposes|
