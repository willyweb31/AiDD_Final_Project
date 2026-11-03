# AiDD_Final_Project

## Signing in

Run `python seed.py` once, then start the app with `flask --app app run` and open http://127.0.0.1:5000.

### Admin

`seed.py` creates the admin account.

- Sign in at http://127.0.0.1:5000/login
- Email: `admin@mycarai.test`
- Password: `admin12345`

Admins upload and manage manuals on `/admin/manuals`. They cannot use the chat: `/vehicle`, `/chat`, and `/conversations` return 403 for admins.

### Driver

There is no seeded driver account. Make one yourself:

1. Sign up at http://127.0.0.1:5000/signup with any email and password.
2. Pick the 2024 Toyota Camry XSE on the vehicle page.
3. You land on `/chat`, where you can ask questions about the car.

To be signed in as an admin and a driver at the same time, use a private or incognito window for one of them.
