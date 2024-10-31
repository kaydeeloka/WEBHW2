# WEBHW2
Academic with flask API
# Academic Records Flask Application

Directory Structure
/your_app/
- **/templates/**: # HTML Templates
       -**base.html**
       -**login.html**             # render the login page, allowing users to enter credentials based in role.
       -**admin.html**            # admin users can manage the application, view reports,manage grades and subjects
       -**professor.html**        #professor-specific views, where they can see their courses, manage students, or view grades.      
       -**student.html**          #displaying student information and print grades

- **/static/**: 
       -**style.css**  # CSS/JS Files
 
 - **app.py**:  # Main Flask App
 - **models.py**: # ORM Models for User, Subject and Grade
 - **api_routes.py**: # Routes for users, subjects and grades
 - **unit_test.py**:  # Tests for the App
 - **requirements.txt**: #dependencies requirement

This application is designed to manage academic records, providing functionalities for user registration, login, and managing subjects and grades.
 It includes both a RESTful API and a web frontend to facilitate interactions with the academic database.

## Features

- **User Registration**: New users can register with a unique ID, role, name, department, and admission year.
- **User Authentication**: Users can log in to access their respective dashboards based on their roles (Student, Professor, Admin).
- **Subject Management**: CRUD operations for subjects including creation, retrieval, updating, and deletion.
- **Grade Management**: CRUD operations for grades, allowing for filtering based on the professor.
- **Role-Based Access**: Different dashboards for Students, Professors, and Admins with role-specific functionalities.

## Technologies Used

- Flask
- Flask-RestX
- Flask-SQLAlchemy
- MySQL (with PyMySQL)
- JWT (JSON Web Tokens) for authentication

## Installation
1. **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv (if already have can use your own venv)

2. **Change the user preference for the PowerShell script execution policy**
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process 
   
3. **Activate venv**
    source venv/bin/activate  # On Windows use
   ```bash
   venv\Scripts\activate.ps1
    ```

5. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

6. **Set up your MySQL database**:
    - Create a database named `academic_records`/ make sure your db is linked
    - Update the database URI in `app.py` with your MySQL credentials.

7. **Initialize the database**:
    - Run the application once to create the necessary tables:
    ```bash
    python app.py
    ```

## Usage

1. **Run the Flask application**:
    ```bash
    python app.py
    ```

2. **Access the application**:
    - Open a web browser and go to `http://127.0.0.1:5000/index` to access the login page.

3. **API Documentation**:
    - The API is accessible via endpoints prefixed with `/api/`.
    - You can view the documentation for API endpoints using the integrated Flask-RestX documentation.

## API Endpoints

### User Endpoints

- **Register User**: `POST /users/`
- **Get All Users**: `GET /users/`
- **Get User by ID**: `GET /users/<id>`
- **Update User**: `PUT /users/<id>`
- **Delete User**: `DELETE /users/<id>`

### Subject Endpoints

- **Get All Subjects**: `GET /subjects/`
- **Create Subject**: `POST /subjects/`
- **Get Subject by Code**: `GET /subjects/<code>`
- **Update Subject**: `PUT /subjects/<code>`
- **Delete Subject**: `DELETE /subjects/<code>`

### Grade Endpoints

- **Get All Grades**: `GET /grades/`
- **Create Grade**: `POST /grades/`
- **Get Grade by ID**: `GET /grades/<id>`
- **Update Grade**: `PUT /grades/<id>`
- **Delete Grade**: `DELETE /grades/<id>`

## Error Handling

The application includes basic error handling, which returns appropriate error messages for various scenarios, such as missing fields, invalid input, and database errors.

## Contributing

Contributions are welcome! Please create a pull request with your improvements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


