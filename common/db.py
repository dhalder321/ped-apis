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
    def get_highest_fileid(table_name, partitionKey, gsiName):

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        response = table.query(
            IndexName= gsiName,
            Limit=1,
            ScanIndexForward=False,
            ProjectionExpression=partitionKey
        )
        items = response.get('Items', [])
        max_fileid = int(items[0][partitionKey]) if items else 0
        return max_fileid
    

    @staticmethod
    # Insert item with auto-incremented partition key
    def addRecordInDynamoTableWithAutoIncrKey(tableName, partitionKey, gsiName, jsonBody):
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tableName)

        try:
            next_fileid = DBManager.get_highest_fileid(tableName, partitionKey, gsiName) + 1
            jsonBody[partitionKey] = next_fileid

            response = table.put_item(Item=jsonBody)
            return True
        
        except Exception as e:
            logging.error("Error occured in addRecordInDynamoTableWithAutoIncrKey method: " + str(e))
            return False