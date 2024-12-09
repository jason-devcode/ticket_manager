# Lottery

## Usage Guide

### Prerequisites

1. **pyenv** (recommended for managing Python versions)
2. **Python 3.10**
3. **virtualenv**

### Steps to Set Up and Run the Project

#### Step 1: Create a Virtual Environment

First, create a virtual environment to manage the project's dependencies.

```sh
virtualenv env
```

#### Step 2: Activate the Virtual Environment

**For Linux:**

```sh
source env/bin/activate
```

**For Windows (cmd):**

```sh
env\Scripts\activate.bat
```

**For Windows (PowerShell):**

```sh
env\Scripts\Activate.ps1
```

#### Step 3: Install Python Dependencies

Install the required dependencies listed in the `requirements.txt` file.

```sh
pip install -r requirements.txt
```

#### Step 4: Run the Django Server

Start the Django development server.

```sh
python manage.py runserver
```

### Configure PostgreSQL Database (Arch Linux)

#### Step 1: Install PostgreSQL

Install PostgreSQL using the package manager.

```sh
sudo pacman -S postgresql
```

#### Step 2: Initialize the Database

Switch to the `postgres` user and initialize the database cluster.

```sh
sudo -iu postgres
initdb --locale $LANG -E UTF8 -D '/var/lib/postgres/data/'
exit
```

#### Step 3: Start and Enable PostgreSQL Service

Start and enable the PostgreSQL service to run on boot.

```sh
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Step 4: Create the Lottery Database

Create a new PostgreSQL database for the project.

```sh
sudo -u postgres psql -c "CREATE DATABASE lottery_db;"
```

#### Step 5: Configure Django to Use PostgreSQL

Edit your Django project's `settings.py` to configure the database settings. Replace the existing database configuration with the following:

**NOTE:** By default this use default postgres user and port 5432.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lottery_db',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Replace `'USER'` and `'PASSWORD'` values with your actual PostgreSQL username and password if you create a user.

#### Step 6: Apply Migrations

Apply the database migrations to create the necessary tables.

```sh
python manage.py migrate
```

## Frontend Development

### Prerequisites

1. Latest stable version of Node.js
2. **NVM** (recommended for managing Node.js versions)
3. Latest stable version of NPM

### Steps to Run Tailwind Development Server

To modify template styles with hot-reload, run the Tailwind development server alongside the Django server. This allows changes in templates to be reflected in the browser immediately.

#### Step 1: Install Tailwind Node Dependencies

Install the necessary Tailwind CSS dependencies.

```sh
python manage.py tailwind install
```

#### Step 2: Run Tailwind Development Server

Start the Tailwind development server.

```sh
python manage.py tailwind start
```

### Building Tailwind CSS

To analyze each template in the project and compile only the used Tailwind styles:

```sh
python manage.py tailwind build
```
