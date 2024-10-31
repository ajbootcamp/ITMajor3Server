from fastapi import FastAPI, HTTPException
import pymysql, bcrypt
from models import UserBase, UserCreate, UserLogin, UserResponse, GoalBase, GoalCreate, GoalResponse, GoalUpdate, UserUpdate, MilestoneBase, MilestoneCreate, MilestoneUpdate, MilestoneResponse, GoalStatus, CommentCreate, CommentResponse, CommentResponse, CommentUpdate
from typing import List
from models import UserLogin
from fastapi.middleware.cors import CORSMiddleware


def get_db():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='goals'
    )
    return connection

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the Personal Goal Tracker!"}

@app.post("/login/", response_model=UserResponse)
def login(user: UserLogin):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
    user_data = cursor.fetchone()
    
    if user_data and bcrypt.checkpw(user.password.encode('utf-8'), user_data[2].encode('utf-8')):  # Assuming password is at index 2
        return UserResponse(id=user_data[0], username=user_data[1])  # Assuming id is at index 0
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")


@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    connection = get_db()
    cursor = connection.cursor()
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    cursor.execute(sql, (user.username, hashed_password))
    user_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return UserResponse(id=user_id, username=user.username)

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    connection.close()
    return UserResponse(id=user[0], username=user[1])

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate):
    connection = get_db()
    cursor = connection.cursor()
    if user_update.username:
        cursor.execute("UPDATE users SET username = %s WHERE id = %s", (user_update.username, user_id))
    if user_update.password:
        hashed_password = bcrypt.hashpw(user_update.password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("UPDATE users SET hashed_password = %s WHERE id = %s", (hashed_password, user_id))
    connection.commit()
    connection.close()
    return get_user(user_id)

@app.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    connection.commit()
    connection.close()
    return UserResponse(id=user[0], username=user[1])

@app.post("/goals/", response_model=GoalResponse)
def create_goal(goal: GoalCreate, user_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO goals (user_id, title, description, deadline) VALUES (%s, %s, %s, %s)", (user_id, goal.title, goal.description, goal.deadline))
    goal_id = cursor.lastrowid
    connection.commit()
    connection.close()
    response = GoalResponse(id=goal_id, user_id=user_id, title=goal.title, description=goal.description, deadline=goal.deadline)
    return response


@app.get("/goals/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_id, title, description, deadline FROM goals WHERE id = %s", (goal_id,))
    goal = cursor.fetchone()
    return GoalResponse(id=goal[0], user_id=goal[1], title=goal[2], description=goal[3], deadline=goal[4])

@app.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: int, goal_update: GoalUpdate):
    connection = get_db()
    cursor = connection.cursor()
    if goal_update.title:
        cursor.execute("UPDATE goals SET title = %s WHERE id = %s", (goal_update.title, goal_id))
    if goal_update.description:
        cursor.execute("UPDATE goals SET description = %s WHERE id = %s", (goal_update.description, goal_id))
    if goal_update.deadline:
        cursor.execute("UPDATE goals SET deadline = %s WHERE id = %s", (goal_update.deadline, goal_id))
    connection.commit()
    connection.close()
    return get_goal(goal_id)

@app.delete("/goals/{goal_id}", response_model=GoalResponse)
def delete_goal(goal_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM goals WHERE id = %s", (goal_id,))
    goal = cursor.fetchone()
    cursor.execute("DELETE FROM goals WHERE id = %s", (goal_id,))
    connection.commit()
    connection.close()
    return GoalResponse(id=goal[0], title=goal[2], description=goal[3], deadline=goal[4])

@app.post("/milestone/", response_model=MilestoneResponse)
def create_goal_progress(milestone: MilestoneCreate):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO milestones(goal_id, title, description, due_date, status) VALUES (%s, %s, %s, %s, %s)", (milestone.goal_id, milestone.title, milestone.description, milestone.due_date, milestone.status.value))
    connection.commit()
    milestone_id = cursor.lastrowid
    cursor.execute("SELECT id, goal_id, title, description, due_date, status FROM milestones WHERE id = %s", (milestone_id,))
    new_milestone = cursor.fetchone()
    connection.close()
    return MilestoneResponse(
        id=new_milestone[0],
        goal_id=new_milestone[1],
        title=new_milestone[2],
        description=new_milestone[3],
        due_date=new_milestone[4],
        status=GoalStatus(new_milestone[5])
    )

@app.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(milestone_id: int, milestone_update: MilestoneUpdate):
    connection = get_db()
    cursor = connection.cursor()
    if milestone_update.title:
        cursor.execute("UPDATE milestones SET title = %s WHERE id = %s", (milestone_update.title, milestone_id))
    if milestone_update.description:
        cursor.execute("UPDATE milestones SET description = %s WHERE id = %s", (milestone_update.description, milestone_id))
    if milestone_update.due_date:
        cursor.execute("UPDATE milestones SET due_date = %s WHERE id = %s", (milestone_update.due_date, milestone_id))
    if milestone_update.status:
        cursor.execute("UPDATE milestones SET status = %s WHERE id = %s", (milestone_update.status.value, milestone_id))
    connection.commit()
    cursor.execute("SELECT id, goal_id, title, description, due_date, status FROM milestones WHERE id = %s", (milestone_id,))
    updated_milestone = cursor.fetchone()
    connection.close()
    return MilestoneResponse(
        id=updated_milestone[0],
        goal_id=updated_milestone[1],
        title=updated_milestone[2],
        description=updated_milestone[3],
        due_date=updated_milestone[4],
        status=GoalStatus(updated_milestone[5])
    )

@app.get("/goals/{goal_id}/milestones/", response_model=List[MilestoneResponse])
def get_milestones_for_goal(goal_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, goal_id, title, description, due_date, status FROM milestones WHERE goal_id = %s", (goal_id,))
    milestones = cursor.fetchall()
    connection.close()
    return [MilestoneResponse(
        id=milestone[0],
        goal_id=milestone[1],
        title=milestone[2],
        description=milestone[3],
        due_date=milestone[4],
        status=GoalStatus(milestone[5])
    ) for milestone in milestones]

@app.delete("/milestones/{milestone_id}", response_model=MilestoneResponse)
def delete_milestone(milestone_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, goal_id, title, description, due_date, status FROM milestones WHERE id = %s", (milestone_id,))
    milestone = cursor.fetchone()
    cursor.execute("DELETE FROM milestones WHERE id = %s", (milestone_id,))
    connection.commit()
    connection.close()
    return MilestoneResponse(
        id=milestone[0],
        goal_id=milestone[1],
        title=milestone[2],
        description=milestone[3],
        due_date=milestone[4],
        status=GoalStatus(milestone[5])
    )

@app.post("/comments/", response_model=CommentResponse)
def add_comment(comment: CommentCreate):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute( "INSERT INTO comments (user_id, goal_id, comment_text) VALUES (%s, %s, %s)", (comment.user_id, comment.goal_id, comment.comment_text))
    comment_id = cursor.lastrowid
    cursor.execute("SELECT id, user_id, goal_id, comment_text, created_at FROM comments WHERE id = %s", (comment_id,))
    new_comment = cursor.fetchone()
    connection.close()
    return CommentResponse(
        id=new_comment[0],
        user_id=new_comment[1],
        goal_id=new_comment[2],
        comment_text=new_comment[3],
        created_at=str(new_comment[4])
    )

@app.put("/comments/{comment_id}/", response_model=CommentResponse)
def update_comment(comment_id: int, update_data: CommentUpdate):
    connection = get_db()
    cursor = connection.cursor()
    if update_data.comment_text:
        cursor.execute("UPDATE comments SET comment_text = %s WHERE id = %s", (update_data.comment_text, comment_id))
    connection.commit()
    cursor.execute("SELECT id, user_id, goal_id, comment_text, created_at FROM comments WHERE id = %s",(comment_id,))
    new_comment = cursor.fetchone()
    connection.close()
    return CommentResponse(
        id=new_comment[0],
        user_id=new_comment[1],
        goal_id=new_comment[2],
        comment_text=new_comment[3],
        created_at=str(new_comment[4])
    )

@app.delete("/comment/{comment_id}", response_model=CommentResponse)
def delete_milestone(comment_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_id, goal_id, comment_text, created_at FROM comments WHERE id = %s",(comment_id,))
    comment = cursor.fetchone()
    cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
    connection.commit()
    connection.close()
    return CommentResponse(
        id=comment[0],
        user_id=comment[1],
        goal_id=comment[2],
        comment_text=comment[3],
        created_at=str(comment[4])
    )

@app.get("/comments/{comment_id}", response_model=List[CommentResponse])
def get_comments(comment_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_id, goal_id, comment_text, created_at FROM comments WHERE id = %s",(comment_id,))
    comments = cursor.fetchall()
    connection.close()
    return [CommentResponse(
        id=comment[0],
        user_id=comment[1],
        goal_id=comment[2],
        comment_text=comment[3],
        created_at=str(comment[4])
    )for comment in comments]

@app.get("/goals/", response_model=GoalResponse)
def all_goals():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, description, deadline FROM goals")
    goals = cursor.fetchall()
    connection.close()
    return [GoalResponse(id=goal[0], title=goal[1], description=goal[2], deadline=goal[3]) for goal in goals]

@app.get("/milestones/completed", response_model=List[MilestoneResponse])
def all_incomplete():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, description, goal_id, status, due_date FROM milestones WHERE status = %s", ("Completed",))
    milestones = cursor.fetchall()
    connection.close()
    return [MilestoneResponse(
        id=milestone[0],
        title=milestone[1],
        description=milestone[2],
        goal_id=milestone[3], 
        status=milestone[4],
        due_date=str(milestone[5]) if milestone[5] else None
    ) for milestone in milestones]

@app.get("/milestones/ongoing", response_model=List[MilestoneResponse])
def all_incomplete():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, description, goal_id, status, due_date FROM milestones WHERE status = %s", ("Ongoing",))
    milestones = cursor.fetchall()
    connection.close()
    return [MilestoneResponse(
        id=milestone[0],
        title=milestone[1],
        description=milestone[2],
        goal_id=milestone[3], 
        status=milestone[4],
        due_date=str(milestone[5]) if milestone[5] else None
    ) for milestone in milestones]

@app.get("/milestones/incomplete", response_model=List[MilestoneResponse])
def all_incomplete():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, description, goal_id, status, due_date FROM milestones WHERE status = %s", ("Incomplete",))
    milestones = cursor.fetchall()
    connection.close()
    return [MilestoneResponse(
        id=milestone[0],
        title=milestone[1],
        description=milestone[2],
        goal_id=milestone[3], 
        status=milestone[4],
        due_date=str(milestone[5]) if milestone[5] else None
    ) for milestone in milestones]

@app.get("/milestones/", response_model=List[MilestoneResponse])
def get_all_milestones():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, description, goal_id, status, due_date FROM milestones")
    milestones = cursor.fetchall()
    connection.close()
    return [MilestoneResponse(
        id=milestone[0],
        title=milestone[1],
        description=milestone[2],
        goal_id=milestone[3],
        status=milestone[4],
        due_date=str(milestone[5]) if milestone[5] else None
    ) for milestone in milestones]

@app.get("/comments/", response_model=List[CommentResponse])
def all_comments():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_id, goal_id, comment_text, created_at FROM comments")
    comments = cursor.fetchall()
    connection.close()
    return [CommentResponse(
        id=comment[0],
        user_id=comment[1],
        goal_id=comment[2],
        comment_text=comment[3],
        created_at=str(comment[4])
    )for comment in comments]