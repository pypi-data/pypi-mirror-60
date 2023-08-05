``robotframework-sqless`` is a  SQL abstraction library for [Robot Framework](https://robotframework.org/)

## Usage

```bash
pip install robotframework-sqless
```

## Example testcase
|                     |                           |                     |                       |
| ----------------    | --------------------------| ------------------- | --------------------- |
| *** Settings ***    |                           |                     |                       |
| Library             | SQLess                    |                     |                       |
| *** Test Cases ***  |                           |                     |                       |
| Get Users By Filter |                           |                     |                       |
|                     | ${users}                  | Users               | username=TestUser     |
|                     | Length Should Be          | ${users}            | 1                     |

The example presumes there is a database with a user table and at least a column `username`.

## Schema definition
The database schema must be defined in an .yml file. For the above example, the following file should apply:

```yaml
database_config:
  dbms: sqlite
  db: sqless.db

schema:
  users:
    tablename: user
    fields:
      id: integer
      username: char
```
