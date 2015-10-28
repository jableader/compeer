# Compeer API

A simple API to vote on paired items in a list

## Usage

### Register a user

URL: `/auth/register`  
DATA:  
* `username`: Username of the person to register  
* `email`: Email of the person to register  
* `password`: Raw password of the user (will be sent over SSL in the final so its
secure enough.

RESPONSE:
* `200 - OK` with no body if the user was made  
* `400 - Bad Request` if the username is taken, or you are missing any fields.
The body will contain a dictionary of all your goofs so you should be ok to show
the user them.

### Get a token for a registered user

URL: `/auth/get-token`  
DATA:  
* `username`:  Username of the person to log in.  
* `password`: Raw password of the person to log in.

RESPONSES:  
* `200 - OK` with a body containing a dictionary with one parameter, `token`, which is a string.  
* `400 - Bad Request` for wrong username / password. Also returns a dict of all the errors.

NOTES:  
* Tokens do not expire, you could log in once and then forever authenticate.

### Lists

You can POST to create lists, or GET to get lists. GET returns the items as nested values, sorted by their rank.

General structure (note the score / rank is not included right now):
```javascript
{
    "id": 0,
    "title": "Top TV shows",
    "description": "Pretty self explainatry aye",
    "action_word": "better"
    "items": [
        {
            "id": 0,
            "caption": "Bobs Burgers",
            "description": "Bob makes burger. Hilarity ensues"
        },
        {
            "id": 1,
            "caption": "Archer",
            "description": "The worlds most famous secret agent"
        }
    ]
}
```

#### Making a list

To make a list you must be authenticated, or else you will get a 401.

You need to `POST` to `/list/` with the data `title`, `description` and optionally `action_word`.


#### Getting or updating a list

To view info about a list, you must know its PK. Then make a GET request to `/list/<pk>`. It will match the structure above.

AFAIK you can also PUT/PATCH to the url to modify information of the list. But I couldn't get the tests green.


### Items

API is pretty similar to lists, where you can create by `POST`ing to `\item\` and can update/view with `\item\<pk>`.

Right now images are not given at all, although I think you can upload them. Next on the todo list is to make it so images are provided as a URL to the image file.

Note, in order to create an item you must be authenticated as the owner of the associated list.

#### Get structure

Note: The list is provided as an ID rather than a nested structure
```javascript
{
    "id": 0,
    "list": 7, 
    "caption": "Bobs Burgers",
    "description": "Bob makes burger. Hilarity ensues"
}
```

#### POST data

To create an item, you need to provide a caption & description in the post data. You
will also need to provide the PK of the associated list with the parameter name `list`.  

### Voting

If you wish to vote, you must first make a request to the server for a pair to vote on. The server will then provide you
with a pair, and a cryptographic token. Then when you have chosen an item to vote on you make a POST request, including
the winner, the loser and the token. If all goes well the score will be incremented for the user and you will get back
a HTTP_200

### Getting a pair

URL: `/list/<pk>/get_pair`  
METHOD: `GET`
RESPONSE:
* `200 - OK` with the structure below if the response was successful

#### Structure
```javascript
{
    "vote_token": "3hgrbr98ro3nbr9",
    "pair": [
        {
            "id": 0,
            "caption": "Bobs Burgers",
            "description": "Bob makes burger. Hilarity ensues"
        },
        {
            "id": 1,
            "caption": "Archer",
            "description": "The worlds most famous secret agent"
        }
    ]
}
```

### Voting on a pair

URL: `/list/<pk>/vote`
METHOD: `POST`
RESPONSE:
*   `200 - OK` with no body if the vote was successful
*   `400 - Bad Request` with a body containing all the errors if it failed.
DATA:  
* `vote_token`:  The vote token you recieved from your get-pair request  
* `winner`: The ID/PK of the winning item
* `loser`: The ID/PK of the losing item

### Hello World

URL: `/hello-world`  
DATA:  
* Optional token header to make an authenticated request.

RESPONSE:  
* `Hello world` if you are anonymous (no token / un recognised)
* `Hello <username>` if you have the token (the tests fail for this... unverified).

#### References
How to authenticate: http://www.django-rest-framework.org/api-guide/authentication/  
Content Headers: http://www.django-rest-framework.org/api-guide/content-negotiation/


## User stories to implement

#### Key for status column
Symbol	| Meaning
------- | -------
CMP		| Complete
OPN		| Unnasigned
ASN		| Assigned but not started
WRK		| Currently working
-		| No back end code required

### Iteration 1
Status	| Resource	| Ref     | As a  | I want to         | So I can
------- | ---------	| ------- | ----- | ----------------- | ---------------------------------
CMP		| Jacob		| CS105   | User  | log in            | access restricted features
CMP		| Jacob		| CS106   | User  | register          | So I can have an account to log in with
-		| Jacob		| CS116   | User  | log out           | use the app anonymously

### Iteration 2
Status	| Resource	| Ref     | As a  | I want to         | So I can
------- | ---------	| ------- | ----- | ----------------- | ---------------------------------
CMP		| Lee		| CS104   | User  | search for a list | find the list I want
CMP		| 			| CS110   | User  | select the list I would like to vote on | vote on things I care about
CMP		| Jacob		| CS101   | User  | create a list     | add items to vote

### Iteration 3
Done?	| Resource	| Ref     | As a  | I want to         | So I can
------- | ---------	| ------- | ----- | ----------------- | ---------------------------------
CMP		| Jacob		| CS107   | User  | vote on items/lists | engage in community voting
CMP		| 			| CS109   | User  | view a list's items sorted by rank/score | see the best/worst items on the list
CMP		| 			| CS301   | LM    | view lists of which I am a LM | manage my lists
