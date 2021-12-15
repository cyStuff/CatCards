# CatCards

### hosted on [app.restingties.com](https://app.restingties.com)
### [github](https://github.com/cyStuff/webapp)

## Requirements
requres flask, flask_login, flask_sqlalchemy, and passlib.
`pip install flask flask_login flask_sqlalchemy passlib`

## Information
This project is for my web development class.

Because I found the assignment boring, I took it a little outside the scope of the class. One of the requirements is that it removes rows from the database. This reqirement is met, but not in an obvious way. If you upgrade a cat and it has a count of exactly 5, the existing cat is removed. There is no other way for a cat to be removed from your inventory.