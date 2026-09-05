## Task1: JWT token
### Example JWT token
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjMiLCJuYW1lIjoiSm9obiBEb2UiLCJyb2xlIjoiQWRtaW4ifQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

### Three Parts of a JWT
A jwt consists of three dot separated parts
1. Header
2. Payload
3. Signature

### Decoded Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
## Explanation:
- `alg` means the signing algorithm used (HS256)
- `typ` means the token type which is JWT

### Decoded payload
```json
{
  "sub": "123",
  "name": "John Doe",
  "role": "Admin"
}
```
## Explanation:
- `sub` is the user ID.
- `name` is the user's name.
- `role` tells what permissions the user has (Admin).
The payload contains information called **claims** about the logged in user.

### Signature
The third part is the signature. It is created by the server using a secret key to verify that the token has not been changed. It is not decoded because it is used for security and verification.


## Task 2: Why passwords should not be stored as plain text?
Passwords should never be stored as plain text because if the database is leaked anyone can immediately read every users password. Many people reuse the same password for different websites so attackers could also access their email or social media. Instead of passwords should be stored as hashed values. A hash is a one way encrypted value that cannot easily be converted back into the original password as during login the entered password is hashed and compared with the stored hash instead of storing or checking the actual password.


## Task 3: Authentication sequence
Client
   │
   │ Login Request
   ▼
Server
   │
   │ Check Password Hash
   ▼
Server
   │
   │ Issue JWT Token
   ▼
Client
   │
   │ Store JWT
   ▼
Client
   │
   │ Send JWT with Next Request
   ▼
Server
   │
   │ Validate JWT
   ▼
Access Granted

### Explanation
1. The client sends a login request with a username and password.
2. The server checks the password by comparing its hash with the stored hash.
3. If the password is correct the server creates a JWT.
4. The client stores the JWT.
5. The client sends the JWT with future requests.
6. The server validates the JWT before allowing access to protected resources.