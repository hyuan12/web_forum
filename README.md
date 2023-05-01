### Group:

Hai Yuan hyuan12@stevens.edu    Wenkai Xiao wxiao7@stevens.edu    Thrinath Reddy Adaboina tadaboin@stevens.edu

### GitHub repo:

https://github.com/hyuan12/web_forum

### hours we spent on the project

We spent about 40 hours in total

### a description of how you tested your code

1) Create a post, read the post, delete the post

2) Create a user, create a post with this user, delete a post with a user key, search for a post by id, search for a post by text, find a post by time

3) Create admin account Create post Delete post via admin key

### any bugs or issues you could not resolve

The code uses a global lock (glock) to synchronize access to the database. While this can prevent data corruption due to race conditions, it can also lead to performance issues and slow down the application

### an example of a difficult issue or bug and how you resolved

We didn't know to properly handle errors and exceptions in Flask when just started learning. We define a custom exception class UserNotFoundException that we raise if the user does not exist in the database. We then catch this exception in the except block and return a custom error message to the user with a 404 status code. If there is a database error, we catch the SQLAlchemyError exception and log the error before returning a generic error message to the user with a 500 status code.

### a list of the four extensions you’ve chosen to implement

① Users and user keys

To create a user by accessing the /user interface through a post request, a username needs to be passed in
example:

```
{
	"username":"jack"
}
```

return:

```
{

    "id": 1,

    "key": "20b02c5247a65028a8c817dd9485b607f8405f9d5e58461e389828fa91015c81e633bdf495f7366e",

    "timestamp": "Sat, 29 Apr 2023 01:10:35 GMT",

    "username": "jack"

}
```

② Date- and time-based range queries

Visit /search_ts/<int:st>/<int:et> to query posts by time range, st is the start timestamp, et is the end timestamp

example:

http://127.0.0.1:5000/search_ts/0/9999999999

return:

```
{

    "posts": [

        {

            "id": 1,

            "msg": "hello world.",

            "timestamp": "Sat, 29 Apr 2023 01:10:35 GMT"

        }

    ]

}
```

③ Fulltext search

Visit /search_msg/\<msg\> for full-text search, msg is the keyword to be searched

example:

http://127.0.0.1:5000/search_msg/h

return:

```
{

    "posts": [

        {

            "id": 1,

            "msg": "hello world.",

            "timestamp": "Sat, 29 Apr 2023 01:10:35 GMT"

        }

    ]

}
```

④ Moderator role

Create an administrator role by accessing /user through a post request. The difference from creating an ordinary user is that creating an administrator account needs to pass in a built-in key to create it. The key returned by the administrator is 80 bits, while that of an ordinary user is 76 bits. , used to distinguish between administrators and ordinary users

```
{
    "username":"admin",
    "key":"admin"
}
```

return:

```
{

    "id": 1,

    "key": "d253c3dd055ce8376904f76962874784d0e11aa10c6bf163d0e9074408b31c4f45f44e8acb4cbc90",

    "timestamp": "Sat, 29 Apr 2023 01:24:04 GMT",

    "username": "admin"

}
```

⑤ Persistence

Persist data through python's built-in shelve library


### detailed summaries of your tests for each of your extensions

test 1

Create a post by visiting /post, then visit /post/int:id to view the created post, and delete this post through /post/<int:id>/\<key\> after viewing

test 2

Create a user through /user, then use the user's key to create a post, use the user's key to delete the post, and access /search/\<int:id\> to find the specified user's post, and access /search_msg/ \<msg\> to search by text, use /search_ts/<int:st>/<int:et> to search by time

test 3

Creating a user is to add a key field to create an administrator account, create a post, and delete this post through the key of the administrator account
