from flask_ui import db



class Group(db.Model):
	__tablename__ = 'Groups'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30))


class User(db.Model):
	__tablename__ = 'Users'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60))


class Tag(db.Model):
	__tablename__ = 'Tags'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True)
	group_id = db.Column(db.Integer, db.ForeignKey('Group.id'))


class Project(db.Model):
	__tablename__ = 'Projects'
	id = db.Column(db.Integer, primary_key=True)
	name = db.String(30)


class Question(db.Model):
	__tablename__ = 'Questions'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True)
	text = db.Column(db.Text)


class Answer(db.Model):
	__tablename__ = 'Answers'
	id = db.Column(db.Integer, primary_key=True)
