from firebase_admin import firestore
from flask import jsonify
from flask import session
from users import *

task_bp = Blueprint('task', __name__)

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    user_id = session.get("user_mail")
    tasks_ref = db.collection("Sarcini")\
                  .where("user_mail", "==", user_id)\
                  .stream()
    tasks = []
    for task in tasks_ref:
        data = task.to_dict()
        data["task_id"] = task.id
        tasks.append(data)
    return render_template('tasks.html', tasks=tasks)


@task_bp.route('/tasks/<int:task_number>', methods=['GET'])
def get_task_by_number(task_number):
    user_mail = session.get("user_mail")
    tasks_ref = db.collection("Sarcini") \
        .where("user_mail", "==", user_mail) \
        .where("task_number", "==", task_number) \
        .stream()

    task_list = list(tasks_ref)
    if task_list:
        task_data = task_list[0].to_dict()
        task_data["task_id"] = task_list[0].id
        return render_template('task.html', task=task_data)
    else:
        return jsonify({"error": "Task not found"}), 404

@task_bp.route('/submit_task', methods=['POST'])
def submit_task():
    user_mail = session.get("user_mail")
    task_title = request.form.get('task_title')
    task_description = request.form.get('task_description')

    tasks_ref = db.collection("Sarcini") \
        .where("user_mail", "==", user_mail) \
        .stream()

    last_task_number = 0
    for task in tasks_ref:
        tn = task.to_dict().get("task_number", 0)
        if tn > last_task_number:
            last_task_number = tn

    new_task_number = last_task_number + 1

    db.collection("Sarcini").add({
        "task_title": task_title,
        "task_description": task_description,
        "task_state": "Uncompleted",
        "user_mail": user_mail,
        "task_number": new_task_number
    })

    return """
    <script>
        alert('Task submitted successfully!');
        window.location.href='/tasks';
    </script>
    """


@task_bp.route('/tasks/<int:task_number>', methods=['POST'])
def modify_task(task_number):
    user_mail = session.get("user_mail")

    tasks_ref = db.collection("Sarcini") \
        .where("task_number", "==", task_number) \
        .where("user_mail", "==", user_mail) \
        .limit(1) \
        .stream()

    doc_id = None
    for doc in tasks_ref:
        doc_id = doc.id

    if doc_id is None:
        return jsonify({"error": "Task not found or unauthorized"}), 404

    task_ref = db.collection("Sarcini").document(doc_id)

    if request.form.get('_method') == 'delete':
        task_ref.delete()
        return """
        <script>
            alert('Task deleted successfully!');
            window.location.href='/tasks';
        </script>
        """

    elif request.form.get('_method_1') == 'put':
        task_ref.update({"task_state": "Completed"})
        return """
        <script>
            alert('Task updated successfully!');
            window.location.href='/tasks';
        </script>
        """

    return jsonify({"error": "Invalid request"}), 400