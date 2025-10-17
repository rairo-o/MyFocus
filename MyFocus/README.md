# MyFocus Project

MyFocus is a personal productivity and task management web application built using Flask. This application helps users manage their tasks, events, notes, and plans efficiently.

## Project Structure

```
MyFocus
├── app.py
├── models.py
├── config.py
├── requirements.txt
├── instance
│   └── myfocus.sqlite
├── templates
│   ├── base.html
│   ├── index.html
│   ├── tasks.html
│   └── task_detail.html
├── static
│   ├── css
│   │   └── styles.css
│   └── js
│       └── main.js
└── README.md
```

## Features

- User-friendly dashboard displaying today's tasks and events.
- Task management functionality to add, edit, and delete tasks.
- Detailed view for each task with additional information.
- Responsive design for a seamless experience across devices.

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd MyFocus
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```
   python app.py
   ```

5. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage Guidelines

- Navigate through the application using the sidebar.
- Manage your tasks from the tasks page.
- View detailed information about each task by clicking on it.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.