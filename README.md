

---

````markdown
# 🧩 Dynamic DB Task Management

A full-stack **To-Do List Application** with a React frontend and a Flask backend.  
It supports dynamic database connections (MongoDB + PostgreSQL) and uses Docker for easy deployment.

---

## 📁 Project Structure
```bash
Dynamic-DB-TODO-List/
├── docker-compose.yml          # Runs backend + frontend with Docker
├── README.md                   # Main project guide
│
├── backend/                    # Flask API server
│   ├── app.py                  # Main Flask app
│   ├── config.py               # Database setup
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend Docker config
│   └── routes/                 # API routes (auth, todos)
│
└── frontend/                   # React web app
    ├── src/                    # React source code
    ├── package.json            # Node dependencies
    ├── Dockerfile              # Frontend Docker config
    └── public/                 # Static files (HTML, favicon, etc.)
````

---

## 🐳 Run Using Docker Compose

### 1️⃣ Build and Run Containers

```bash
docker-compose up --build
```

This command will:

* Build both **frontend** and **backend** images
* Run them together using a single network
* Start the backend on **port 5000** and frontend on **port 3003**

---

### 2️⃣ Access the Application

Once containers are running, open your browser and visit:
👉 **[http://localhost:3003/](http://localhost:3003/)**

---

### 3️⃣ Check Logs (Optional)

View live backend logs:

```bash
docker logs -f dynamic-db-todo-list-backend-1
```

---

### 4️⃣ Stop the Application

To stop and remove containers:

```bash
docker-compose down
```

---

### 5️⃣ Rebuild and Restart

If you make any code or dependency changes:

```bash
docker-compose up --build
```

---

## ⚙️ Environment Variables (If You Want Your Credentials)

Create a `.env` file inside the `backend/` directory with the following keys:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database>
POSTGRES_URI=your_postgres_connection_string
JWT_SECRET_KEY=your_secret_key
```

> ⚠️ **Important:**
> If your MongoDB password contains special characters (`@`, `#`, `$`, etc.), URL-encode them.
> Example: `@` → `%40`

---

## 🧑‍💻 Developer Notes

* Flask runs on port **5000** inside Docker.
* React runs on port **3003**.

---


