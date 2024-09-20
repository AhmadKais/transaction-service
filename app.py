from flask import Flask, request, jsonify
import boto3
from decimal import Decimal
import uuid

app = Flask(__name__)

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TransactionsTable')

# Create a new transaction
@app.route('/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()  # Get data sent in the request body
    transaction_id = str(uuid.uuid4())  # Generate a unique ID for the transaction

    # Put the transaction data into the DynamoDB table
    table.put_item(
        Item={
            'transaction_id': transaction_id,
            'amount': Decimal(str(data['amount'])),  # Use Decimal for the amount
            'user_id': data['user_id'],
            'description': data['description']
        }
    )
    return jsonify({'message': 'Transaction created successfully', 'transaction_id': transaction_id}), 201


# Get a transaction by ID
@app.route('/transactions/<string:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    response = table.get_item(Key={'transaction_id': transaction_id})
    transaction = response.get('Item')

    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404

    return jsonify(transaction)

# Update a transaction
# Update a transaction
@app.route('/transactions/<string:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    data = request.get_json()

    update_expression = "set "
    expression_attribute_values = {}

    if 'amount' in data:
        update_expression += "amount = :a, "
        expression_attribute_values[':a'] = Decimal(str(data['amount']))  # Convert to Decimal

    if 'description' in data:
        update_expression += "description = :d, "
        expression_attribute_values[':d'] = data['description']

    # Remove the trailing comma and space
    update_expression = update_expression.rstrip(', ')

    try:
        table.update_item(
            Key={'transaction_id': transaction_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return jsonify({'message': 'Transaction updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error updating transaction'}), 500

# Delete a transaction
@app.route('/transactions/<string:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    table.delete_item(Key={'transaction_id': transaction_id})
    return jsonify({'message': 'Transaction deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
