import boto3
import logging

class DBManager:

    @staticmethod
    def addRecordInDynamoTable(tableName, jsonData):

        try: 
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(tableName)
            response = table.put_item(Item= jsonData)
            return True
        
        except Exception as e:
            logging.error("Error occured in addRecordInDynamoTable method: " + str(e))
            return False
        
    @staticmethod
    # Function to get the highest fileid value
    def get_highest_fileid(table_name, index_key_column, partitionKeyColumn, \
                           index_name, index_key_value="99"):

        client = boto3.client('dynamodb')

        # Define the request parameters
        response = client.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression='#pk = :pk',
            ExpressionAttributeValues={':pk': {'N': index_key_value}},
            ExpressionAttributeNames={'#pk': index_key_column},
            ScanIndexForward=False,
            ProjectionExpression=partitionKeyColumn,
            Limit=1
        )

        # return the highest value
        if 'Items' in response and len(response['Items']) > 0: 
            return int(response['Items'][0][partitionKeyColumn]['N'])
        return 0

    

    @staticmethod
    # Insert item with auto-incremented partition key
    def addRecordInDynamoTableWithAutoIncrKey(tableName, indexKeyCol, partitionKey, gsiName, jsonBody):
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tableName)

        try:
            next_fileid = DBManager.get_highest_fileid(tableName, indexKeyCol, partitionKey, gsiName) + 1
            jsonBody[partitionKey] = next_fileid

            response = table.put_item(Item=jsonBody)
            return True
        
        except Exception as e:
            logging.error("Error occured in addRecordInDynamoTableWithAutoIncrKey method: " + str(e))
            return False