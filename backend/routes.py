from models import *
import openai
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Blueprint, jsonify
from flask import request 
from fpdf import FPDF
from flask import Flask, jsonify, send_file
from flask_restful import Resource

openai.api_key = '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'  # Add your OpenAI API key here

employee_parser = reqparse.RequestParser()
employee_parser.add_argument('name', type=str, required=True, help="Name is required")
employee_parser.add_argument('email', type=str, required=True, help="Email is required")
employee_parser.add_argument('role', type=str, required=True, help="Role is required")
employee_parser.add_argument('password', type=str, required=True, help="Password is required")


idea_parser = reqparse.RequestParser()
idea_parser.add_argument('title', type=str, required=True, help="Title is required")
idea_parser.add_argument('description', type=str, required=True, help="Description is required")

vote_parser = reqparse.RequestParser()
vote_parser.add_argument('idea_id', type=int, required=True, help="Idea ID is required")
vote_parser.add_argument('vote_type', type=str, required=True, help="Vote type is required")


feedback_parser = reqparse.RequestParser()
feedback_parser.add_argument('idea_id', type=int, required=True, help="Idea ID is required")
feedback_parser.add_argument('content', type=str, required=True, help="Content is required")

comment_parser = reqparse.RequestParser()
comment_parser.add_argument('idea_id', type=int, required=True, help="Idea ID is required")
comment_parser.add_argument('content', type=str, required=True, help="Content is required")

incentive_parser = reqparse.RequestParser()
incentive_parser.add_argument('points', type=int, required=True, help="Points are required")
incentive_parser.add_argument('reason', type=str, required=False)

auth_parser = reqparse.RequestParser()
auth_parser.add_argument('email', type=str, required=True, help="Email is required")
auth_parser.add_argument('password', type=str, required=True, help="Password is required")

# CRUD Resources

class LoginResource(Resource):
    def post(self):
        args = auth_parser.parse_args()
        email = args['email']
        password = args['password']

        employee = Employee.query.filter_by(email=email).first()
        if employee and employee.check_password(password):
            access_token = create_access_token(identity=str(employee.id), additional_claims={"role": employee.role})

            return {
                'access_token': access_token,
                'user': {
                    'id': employee.id,
                    'role': employee.role
                }
            }, 200
        return {'message': 'Invalid credentials'}, 401


class SecureEmployeeResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {'id': current_user['id'], 'role': current_user['role']}, 200

class EmployeeResource(Resource):
    @jwt_required()
    def get(self):
        employees = Employee.query.all()
        return [{'id': e.id, 'name': e.name, 'email': e.email, 'role': e.role} for e in employees]


    @jwt_required()
    def post(self):
        args = employee_parser.parse_args()
        hashed_password = generate_password_hash(args["password"])
        new_employee = Employee(
            name=args['name'],
            email=args['email'],
            role=args['role'],
            password_hash=hashed_password
        )
        db.session.add(new_employee)
        db.session.commit()
        return {'message': 'Employee created successfully'}, 201
    
    @jwt_required()
    def delete(self, employee_id):
        employee = Employee.query.get(employee_id)
        if employee:
            db.session.delete(employee)
            db.session.commit()
            return {'message': 'Employee deleted successfully'}, 200
        else:
            return {'message': 'Employee not found'}, 404

def serialize_votes(votes):
    return [{'id': vote.id, 'user_id': vote.user_id} for vote in votes]

def serialize_feedback(feedbacks):
    return [{'id': feedback.id, 'comment': feedback.comment} for feedback in feedbacks]

def serialize_resources(resources):
    return [{'id': resource.id, 'name': resource.name} for resource in resources]


class IdeaResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        if not employee:
            return {'message': 'User not found'}, 404
        
        current_user_role = employee.role

        # Get all ideas and their feedback
        ideas = Idea.query.all()
        
        # Prepare feedback text for all ideas to send in bulk to OpenAI for scoring and generating feedback
        feedback_data = []
        for idea in ideas:
            feedback_text = " ".join([feedback.content for feedback in idea.feedback])
            feedback_data.append({
                'idea_id': idea.id,
                'title': idea.title,
                'description': idea.description,
                'feedback': feedback_text
            })
        
        # Call OpenAI to assign scores and generate feedback for each idea based on feedback
        responses = []
        for feedback_item in feedback_data:
            # Generate AI feedback
            ai_feedback_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Or use "gpt-4" if you have access
                messages=[
                    {"role": "system", "content": "You are an assistant that provides feedback on ideas."},
                    {"role": "user", "content": f"Provide detailed feedback for this idea based on the following feedback: {feedback_item['feedback']}. The idea title is '{feedback_item['title']}' and its description is: {feedback_item['description']}"}
                ],
                max_tokens=100
            )
            ai_feedback = ai_feedback_response['choices'][0]['message']['content'].strip()

            # Rate the feedback quality using the same prompt
            rating_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Or use "gpt-4"
                messages=[
                    {"role": "system", "content": "You are an assistant that rates feedback quality."},
                    {"role": "user", "content": f"Rate the quality of the feedback for this idea from 1 to 10: {feedback_item['feedback']}"}
                ],
                max_tokens=10
            )
            rating_text = rating_response['choices'][0]['message']['content'].strip()

            # Attempt to convert the rating to an integer, with fallback logic
            try:
                score = int(rating_text)
            except ValueError:
                # Handle cases where the rating text is non-numeric or unexpected
                score = 5  # You can choose to set a default score in such cases

            responses.append({
                'idea_id': feedback_item['idea_id'],
                'title': feedback_item['title'],
                'description': feedback_item['description'],
                'feedback': feedback_item['feedback'],
                'ai_feedback': ai_feedback,  # AI-generated feedback
                'score': score  # AI rating of the feedback quality
            })
        
        # Sort the ideas by score (highest to lowest)
        sorted_ideas = sorted(responses, key=lambda x: x['score'], reverse=True)
        
        # Fetch the detailed idea info after sorting
        result = []
        for sorted_idea in sorted_ideas:
            idea = Idea.query.get_or_404(sorted_idea['idea_id'])
            votes = [{'voter_id': vote.voter_id, 'vote': vote.vote_type} for vote in idea.votes]
            
            upvotes = Vote.query.filter_by(idea_id=idea.id, vote_type=1).count()
            downvotes = Vote.query.filter_by(idea_id=idea.id, vote_type=0).count()

            user_vote = None
            for vote in votes:
                if vote['voter_id'] == current_user_id:
                    user_vote = vote['vote']
                    break

            result.append({
                'id': idea.id,
                'title': idea.title,
                'description': idea.description,
                'status': idea.status,
                'upvotes': upvotes,
                'downvotes': downvotes,
                'votes': votes,
                'user_vote': user_vote,
                'feedback': [feedback.content for feedback in idea.feedback],
                'ai_feedback': sorted_idea['ai_feedback'],  # Include AI feedback here
                'score': sorted_idea['score'],  # Include AI score here
                'resources': [resource.id for resource in idea.resources],
                'author_id': idea.author_id,
                'author': employee.email,
                'can_approve': current_user_role == 'manager'
            })

        return result, 200


    @jwt_required()
    def post(self):
        # Get the current user's identity
        current_user_id = get_jwt_identity()
        
        
        args = idea_parser.parse_args()
        new_idea = Idea(
            title=args['title'],
            description=args['description'],
            author_id=current_user_id  # Set the current user as the author
        )
        db.session.add(new_idea)
        db.session.commit()
        return {'message': 'Idea created successfully'}, 201

    @jwt_required()
    def put(self, idea_id):
        # Get the current user's identity
        current_user_id = get_jwt_identity()
        # Get the current user's ID and role from the JWT token
        employee = Employee.query.get(current_user_id)
        
        if not employee:
            return {'message': 'User not found'}, 404
        
        # Get the role from the Employee object
        current_user_role = employee.role

        idea = Idea.query.get_or_404(idea_id)
        if current_user_role == 'manager':  # Only managers can approve/reject
            action = request.json.get('action')
            if action == 'approve':
                idea.status = 'Approved'
            elif action == 'reject':
                idea.status = 'Rejected'
            db.session.commit()
            return {'message': f'Idea {action}d successfully.'}, 200
        return {'message': 'Permission denied.'}, 403
    
class VoteResource(Resource):
    @jwt_required()
    def post(self):
        args = vote_parser.parse_args()
        current_user_id = get_jwt_identity()
        new_vote = Vote(
            idea_id=args['idea_id'],
            voter_id=current_user_id
        )
        db.session.add(new_vote)
        db.session.commit()
        return {'message': 'Vote added successfully'}, 201

class FeedbackResource(Resource):
    @jwt_required()
    def get(self):
        idea_id = request.args.get('idea_id')  # Ensure 'idea_id' is retrieved from query params
        print("idea id:", idea_id)
        if not idea_id:
            return {'message': 'Idea ID is required'}, 400
        
        feedbacks = Feedback.query.filter_by(idea_id=idea_id).all()
        
        
        return [{'id': comment.id, 'content': comment.content, 'author_id': comment.author_id} for comment in feedbacks], 200
    
    @jwt_required()
    def post(self):
        args = feedback_parser.parse_args()
        current_user_id = get_jwt_identity()
        # Get the current user's ID and role from the JWT token
        employee = Employee.query.get(current_user_id)
        
        if not employee:
            return {'message': 'User not found'}, 404
        
        # Get the role from the Employee object
        current_user_role = employee.role

        feedback = Feedback(
            idea_id=args['idea_id'],
            author_id=current_user_id,
            content=args['content']
        )
        db.session.add(feedback)
        db.session.commit()
        return {'message': 'Feedback added successfully'}, 201

class CommentResource(Resource):
    @jwt_required()
    def get(self):
        idea_id = request.args.get('idea_id')  # Ensure 'idea_id' is retrieved from query params
        print("idea id:", idea_id)
        if not idea_id:
            return {'message': 'Idea ID is required'}, 400
        
        comments = Comment.query.filter_by(idea_id=idea_id).all()
        
        return [{'id': comment.id, 'content': comment.content, 'author_id': comment.author_id} for comment in comments], 200
    
    @jwt_required()
    def post(self):
        args = comment_parser.parse_args()
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        if not employee:
            return {'message': 'User not found'}, 404
        
        current_user_role = employee.role

        comment = Comment(
            idea_id=args['idea_id'],
            author_id=current_user_id,
            content=args['content']
        )
        db.session.add(comment)
        db.session.commit()
        return {'message': 'Comment added successfully'}, 201


# Add this route to your Flask API
class IdeaVoteResource(Resource):
    @jwt_required()
    def post(self, idea_id):
        current_user_id = get_jwt_identity()
        args = vote_parser.parse_args()

        # Ensure the `idea_id` matches the parsed data
        if idea_id != args['idea_id']:
            return {'message': 'Idea ID mismatch'}, 400

        # Check if the user already voted on this idea
        existing_vote = Vote.query.filter_by(idea_id=idea_id, voter_id=current_user_id).first()
        if existing_vote:
            return {'message': 'You have already voted on this idea'}, 400

        new_vote = Vote(
            idea_id=idea_id,
            voter_id=current_user_id,
            vote_type=args['vote_type']  # Adjust based on your data
        )
        db.session.add(new_vote)
        db.session.commit()

        return {'message': 'Vote added successfully'}, 201

class ResourceAllocationResource(Resource):
    @jwt_required()
    def post(self, idea_id):
        # Retrieve the current user's role
        current_user = get_jwt_identity()
        if current_user['role'] != 'manager':
            return {'message': 'Only managers can allocate resources.'}, 403

        # Get the quantity and resource type from the request body
        resource_type = request.json.get('resource_type')
        quantity = request.json.get('quantity')

        if not resource_type or not quantity:
            return {'message': 'Resource type and quantity are required.'}, 400

        # Retrieve the idea and create the resource allocation entry
        idea = Idea.query.get(idea_id)
        if not idea:
            return {'message': 'Idea not found'}, 404

        resource = Resource.query.filter_by(idea_id=idea_id, resource_type=resource_type).first()

        if resource:
            resource.allocated_amount += quantity  # Add the new allocated amount
        else:
            # Create a new resource allocation if not already exists
            resource = Resource(idea_id=idea_id, resource_type=resource_type, allocated_amount=quantity)
            db.session.add(resource)

        db.session.commit()
        return {'message': f'Resource allocated successfully to {idea.title}'}, 200
    
class IdeaActionResource(Resource):
    @jwt_required()
    def get(self, idea_id):
        idea = Idea.query.get(idea_id)
        if not idea:
            return {'message': 'Idea not found'}, 404
        return {
            'id': idea.id,
            'title': idea.title,
            'description': idea.description,
            'status': idea.status,
        }, 200

    @jwt_required()
    def put(self, idea_id):
        idea = Idea.query.get(idea_id)
        if not idea:
            return {'message': 'Idea not found'}, 404
        action = request.json.get('action')
        if action == 'approve':
            idea.status = 'Approved'
        elif action == 'reject':
            idea.status = 'Rejected'
        db.session.commit()
        return {'message': f'Idea {action}d successfully.'}, 200
   

import os


class ReportResource(Resource):
    def get(self, idea_id):
        try:
            # Ensure the 'reports' directory exists
            if not os.path.exists('./reports'):
                os.makedirs('./reports')

            # Fetch the idea from the database
            idea = Idea.query.get(idea_id)
            if not idea:
                return {"error": "Idea not found"}, 404

            # Fetch related data
            votes = Vote.query.filter_by(idea_id=idea_id).all()
            feedbacks = Feedback.query.filter_by(idea_id=idea_id).all()
            comments = Comment.query.filter_by(idea_id=idea_id).all()

            # Define the author (handling case when author is None)
            author_name = idea.author.name if idea.author else "Unknown"

            # Manually fetching author details for feedback and comments
            feedbacks_data = []
            for feedback in feedbacks:
                feedback_author = Employee.query.get(feedback.author_id)
                feedback_author_email = feedback_author.email if feedback_author else "Unknown"
                feedbacks_data.append([feedback_author_email, feedback.content])

            comments_data = []
            for comment in comments:
                comment_author = Employee.query.get(comment.author_id)
                comment_author_email = comment_author.email if comment_author else "Unknown"
                comments_data.append([comment_author_email, comment.content])

            # Example data structure for the report
            data = {
                "title": idea.title,
                "description": idea.description,
                "author": author_name,
                "status": idea.status,
                "votes": len(votes),
                "feedbacks": feedbacks_data,
                "comments": comments_data
            }

            # Generate PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Title
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt=data["title"], ln=True, align="C")
            pdf.ln(10)  # Line break

            # Description
            pdf.set_font("Arial", 'I', 12)
            pdf.multi_cell(0, 10, txt=data["description"])
            pdf.ln(5)

            # Author and Status
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Author: {data['author']}")
            pdf.ln(5)
            pdf.cell(0, 10, f"Status: {data['status']}")
            pdf.ln(10)

            # Votes
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Votes: {data['votes']}")
            pdf.ln(10)

            # Feedback Section
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Feedbacks:", ln=True)
            pdf.set_font("Arial", '', 12)

            # Table header for feedbacks
            pdf.cell(90, 10, 'Author', border=1, align='C')
            pdf.cell(100, 10, 'Feedback', border=1, align='C')
            pdf.ln()

            # Populate feedbacks
            for feedback in data["feedbacks"]:
                pdf.cell(90, 10, feedback[0], border=1, align='L')
                pdf.multi_cell(100, 10, feedback[1], border=1, align='L')
                pdf.ln()

            pdf.ln(10)

            # Comments Section
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Comments:", ln=True)
            pdf.set_font("Arial", '', 12)

            # Table header for comments
            pdf.cell(90, 10, 'Author', border=1, align='C')
            pdf.cell(100, 10, 'Comment', border=1, align='C')
            pdf.ln()

            # Populate comments
            for comment in data["comments"]:
                pdf.cell(90, 10, comment[0], border=1, align='L')
                pdf.multi_cell(100, 10, comment[1], border=1, align='L')
                pdf.ln()

            # Save PDF to a file
            file_path = f"./reports/idea_{idea_id}.pdf"
            pdf.output(file_path)

            # Return the generated PDF file
            return send_file(file_path, as_attachment=True, mimetype="application/pdf")

        except Exception as e:
            return {"error": str(e)}, 500

# Register Resources Function
def register_routes(api):
    api.add_resource(LoginResource, '/login')
    api.add_resource(SecureEmployeeResource, '/secure-employee')
    #api.add_resource(EmployeeResource, '/employees')
    api.add_resource(EmployeeResource, '/employees', '/employees/<int:employee_id>')
    api.add_resource(IdeaResource, '/ideas')
    api.add_resource(IdeaActionResource, '/ideas/<int:idea_id>')  # For /ideas/<id>
    api.add_resource(VoteResource, '/votes')
    api.add_resource(FeedbackResource, '/feedbacks')
    api.add_resource(CommentResource, '/comments')
    api.add_resource(IdeaVoteResource, '/ideas/<int:idea_id>/vote')
    api.add_resource(ReportResource, '/reports/generate/<int:idea_id>')  # Notice the <int:idea_id> part



