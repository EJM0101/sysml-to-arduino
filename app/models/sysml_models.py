from app import db

class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    req_id = db.Column(db.String(50), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('requirement.id'))
    children = db.relationship('Requirement', backref=db.backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'<Requirement {self.req_id}: {self.name}>'

class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    operations = db.Column(db.Text)
    properties = db.Column(db.Text)
    constraints = db.Column(db.Text)

    def __repr__(self):
        return f'<Block {self.name} ({self.type})>'